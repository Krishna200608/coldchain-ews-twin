"""
scripts/train_tft_forecaster.py
===============================
GPU Training Pipeline for Multi-Horizon Quantile Temporal Forecaster (Proposal P3).
Uses NVIDIA RTX 5000 Ada Generation GPU to train 10-step lookahead quantile forecasters
on Out and In telemetry series under strict chronological split (D6).

Inputs:
- data/processed/{out,in}_labeled.csv
- data/processed/lstm_norm_stats_{out,in}.json

Outputs:
- models/tft_forecaster_out.pt
- models/tft_forecaster_in.pt
- data/processed/tft_eval_stats.json
"""

import json
import pathlib
import sys
import time
import numpy as np
import pandas as pd
import torch
from numpy.lib.stride_tricks import sliding_window_view
from torch.utils.data import DataLoader, TensorDataset

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.config import RANDOM_SEED
from src.models.tft_forecaster import TemporalQuantileForecaster, pinball_loss


def build_tft_dataset(series: str):
    processed_dir = REPO_ROOT / "data" / "processed"
    df = pd.read_csv(processed_dir / f"{series.lower()}_labeled.csv", parse_dates=["ts"])
    df = df.dropna(subset=["gap_seconds"]).sort_values(["ts", "gap_seconds"], ascending=[True, False]).reset_index(drop=True)

    with open(processed_dir / f"lstm_norm_stats_{series.lower()}.json") as f:
        norm_stats = json.load(f)
    t_mean = float(norm_stats["temp_injected_mean"])
    t_std = float(norm_stats["temp_injected_std"])
    g_mean = float(norm_stats["log_gap_seconds_mean"])
    g_std = float(norm_stats["log_gap_seconds_std"])

    # 4 Input Features
    t_norm = (df["temp_injected"].values - t_mean) / t_std
    g_norm = (np.log1p(df["gap_seconds"].values) - g_mean) / g_std

    # Rolling 10 features
    rolling_std = df["temp_injected"].rolling(10, min_periods=2).std().bfill().values
    std_mean = float(rolling_std.mean())
    std_std = float(rolling_std.std()) if float(rolling_std.std()) > 1e-6 else 1.0
    r_std_norm = (rolling_std - std_mean) / std_std

    rolling_mean = df["temp_injected"].rolling(10, min_periods=1).mean().values
    delta = df["temp_injected"].values - rolling_mean
    d_mean = float(delta.mean())
    d_std = float(delta.std()) if float(delta.std()) > 1e-6 else 1.0
    r_delta_norm = (delta - d_mean) / d_std

    feat_matrix = np.column_stack([t_norm, g_norm, r_std_norm, r_delta_norm]).astype(np.float32)

    # Windowing: 30 past input steps -> 10 future target steps
    L = 30
    H = 10
    total_len = len(feat_matrix)
    n_samples = total_len - L - H + 1

    # Sliding window inputs: (n_samples, 30, 4)
    X_windows = sliding_window_view(feat_matrix, window_shape=(L, 4)).squeeze(1)[:n_samples].copy()

    # Sliding window targets: 10 future temperature steps (normalized)
    t_targets = sliding_window_view(t_norm, window_shape=H)[L : L + n_samples].copy()

    # Timestamps at the forecast origin (endpoint of input window, index L-1 to L-1+n_samples)
    ts_origins = df["ts"].iloc[L - 1 : L - 1 + n_samples].reset_index(drop=True)

    norm_dict = {
        "t_mean": t_mean,
        "t_std": t_std,
        "g_mean": g_mean,
        "g_std": g_std,
        "std_mean": std_mean,
        "std_std": std_std,
        "d_mean": d_mean,
        "d_std": d_std,
    }

    return X_windows, t_targets, ts_origins, norm_dict


def train_tft_for_series(
    series: str,
    epochs: int = 40,
    batch_size: int = 512,
    lr: float = 1e-3,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
):
    print(f"\n{'=' * 60}")
    print(f" Training Temporal Quantile Forecaster (P3) on {series.upper()}")
    print(f" Device: {device} | {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")

    X, Y, ts, norm_dict = build_tft_dataset(series)

    # Chronological partition (D6)
    cutoff = pd.Timestamp("2018-10-29 11:10:48")
    train_mask = (ts < cutoff).values
    test_mask = ~train_mask

    X_train, Y_train = X[train_mask], Y[train_mask]
    X_test, Y_test = X[test_mask], Y[test_mask]

    print(f"Dataset summary:")
    print(f"  Train: {len(X_train)} sequences (input: 30x4, horizon: 10)")
    print(f"  Test:  {len(X_test)} sequences")

    train_ds = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(Y_train))
    test_ds = TensorDataset(torch.from_numpy(X_test), torch.from_numpy(Y_test))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    model = TemporalQuantileForecaster(
        input_dim=4,
        hidden_dim=64,
        horizon=10,
        quantiles=[0.1, 0.5, 0.9],
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_val_loss = float("inf")
    models_dir = REPO_ROOT / "models"
    save_path = models_dir / f"tft_forecaster_{series.lower()}.pt"

    t0 = time.time()
    for ep in range(1, epochs + 1):
        model.train()
        train_losses = []
        for bx, by in train_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            preds = model(bx)
            loss = pinball_loss(by, preds, quantiles=[0.1, 0.5, 0.9])
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            optimizer.step()
            train_losses.append(loss.item())

        scheduler.step()

        # Validation
        model.eval()
        val_losses = []
        with torch.no_grad():
            for bx, by in test_loader:
                bx, by = bx.to(device), by.to(device)
                preds = model(bx)
                val_losses.append(pinball_loss(by, preds, quantiles=[0.1, 0.5, 0.9]).item())

        mean_train = float(np.mean(train_losses))
        mean_val = float(np.mean(val_losses))

        if mean_val < best_val_loss:
            best_val_loss = mean_val
            torch.save({
                "model_state_dict": model.state_dict(),
                "epoch": ep,
                "best_val_loss": best_val_loss,
                "norm_dict": norm_dict,
            }, save_path)

        if ep % 10 == 0 or ep == 1 or ep == epochs:
            print(f"Epoch {ep:02d}/{epochs} | Train Pinball: {mean_train:.5f} | Val Pinball: {mean_val:.5f} | Best: {best_val_loss:.5f}")

    elapsed = time.time() - t0
    print(f"Training completed in {elapsed:.2f}s. Saved best weights to {save_path}")

    return {
        "series": series,
        "best_val_loss": best_val_loss,
        "weights_path": str(save_path),
        "norm_dict": norm_dict,
    }


def main():
    torch.manual_seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(RANDOM_SEED)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"GPU Accelerator: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

    results = {
        "Out": train_tft_for_series("Out", epochs=40, device=device),
        "In": train_tft_for_series("In", epochs=40, device=device),
    }

    stats_path = REPO_ROOT / "data" / "processed" / "tft_eval_stats.json"
    with open(stats_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nAll models saved! Evaluation stats recorded at {stats_path}")


if __name__ == "__main__":
    main()
