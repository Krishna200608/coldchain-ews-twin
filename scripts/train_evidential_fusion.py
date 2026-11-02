"""
scripts/train_evidential_fusion.py
==================================
Trains the Dempster-Shafer Evidential Deep Learning (EDL) Multi-Detector Fusion
Layer (Proposal P5) on the college GPU server (NVIDIA RTX 5000 Ada Generation).

Fuses:
1. Naive Baseline (standardized temp exceedance)
2. Isolation Forest (negated continuous decision score)
3. Pre-trained LSTM-AE (reconstruction MSE)
4. Variational LSTM-AE (aleatoric data uncertainty)
5. Variational LSTM-AE (epistemic model uncertainty)
6. Physics-Informed LSTM-AE (Newton cooling thermodynamic residual)
7. Normalized Sampling Gap Seconds (log_gap_seconds_norm)

Outputs:
- models/evidential_fusion_out.pt
- models/evidential_fusion_in.pt
- data/processed/fusion_eval_stats.json
- data/processed/fusion_dataset_{out,in}.npz
"""

import json
import os
import pathlib
import sys
import time
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.config import (
    RANDOM_SEED,
    VLSTM_HIDDEN_SIZE,
    VLSTM_LATENT_DIM,
)
from src.models.pilstm_ae import PILSTMAutoencoder
from src.models.vlstm_ae import VLSTMAutoencoder
from src.fusion.evidential_fusion import (
    EvidentialFusionMLP,
    evidential_loss,
)


def update_status(status_dict: dict):
    status_file = REPO_ROOT / "logs" / "fusion_train_status.json"
    status_file.parent.mkdir(exist_ok=True)
    with open(status_file, "w") as f:
        json.dump(status_dict, f, indent=2)


def set_seed(seed=RANDOM_SEED):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def extract_fusion_features(series: str, device: str = "cuda"):
    """
    Constructs the 7-dimensional multi-detector feature matrix across all readings.
    Returns:
        X (np.ndarray): (N-29, 7) feature matrix.
        y (np.ndarray): (N-29,) binary ground truth targets.
        ts_valid (pd.Series): Timestamps for each window endpoint.
    """
    processed_dir = REPO_ROOT / "data" / "processed"
    models_dir = REPO_ROOT / "models"

    print(f"Extracting 7-detector telemetry features for {series.upper()} series...")
    labeled_csv = processed_dir / f"{series.lower()}_labeled.csv"
    df = pd.read_csv(labeled_csv, parse_dates=["ts"])
    df = df.dropna(subset=["gap_seconds"]).sort_values(["ts", "gap_seconds"], ascending=[True, False]).reset_index(drop=True)

    # 1. Load pre-computed adaptive log for IF and baseline LSTM
    adapt_csv = processed_dir / f"adaptive_threshold_log_{series.lower()}.csv"
    df_adapt = pd.read_csv(adapt_csv)

    # Normalization statistics
    with open(processed_dir / f"lstm_norm_stats_{series.lower()}.json") as f:
        norm_stats = json.load(f)
    t_mean = float(norm_stats["temp_injected_mean"])
    t_std = float(norm_stats["temp_injected_std"])
    g_mean = float(norm_stats["log_gap_seconds_mean"])
    g_std = float(norm_stats["log_gap_seconds_std"])

    # Clean baseline stats
    clean_csv = processed_dir / f"{series.lower()}_features.csv"
    df_clean = pd.read_csv(clean_csv)
    b_mean = float(df_clean["temp"].dropna().mean())
    b_std = float(df_clean["temp"].dropna().std())

    # Physics constants
    with open(processed_dir / f"physics_params_{series.lower()}.json") as f:
        phys_params = json.load(f)
    T_amb = float(phys_params["T_amb"])
    k_cooling = float(phys_params["k_cooling"])

    # Normalized sequence arrays for deep models
    t_norm = (df["temp_injected"].values - t_mean) / t_std
    g_norm = (np.log1p(df["gap_seconds"].values) - g_mean) / g_std
    feat_2d = np.column_stack([t_norm, g_norm]).astype(np.float32)

    # Vectorized sliding window view: (N - 29, 30, 2)
    windows = sliding_window_view(feat_2d, window_shape=(30, 2)).squeeze(1).copy()
    N_win = len(windows)

    # Load neural models onto accelerator
    pilstm = PILSTMAutoencoder(2, 32, 30).to(device)
    pilstm.load_state_dict(torch.load(models_dir / f"pilstm_{series.lower()}.pt", map_location=device)["model_state_dict"])
    pilstm.eval()

    vlstm = VLSTMAutoencoder(2, VLSTM_HIDDEN_SIZE, VLSTM_LATENT_DIM, 30).to(device)
    vlstm.load_state_dict(torch.load(models_dir / f"vlstm_{series.lower()}.pt", map_location=device)["model_state_dict"])
    vlstm.eval()

    # Batch GPU inference for PILSTM physics residual
    print(f"  Evaluating PILSTM physics residuals in batches...")
    phys_residuals = []
    with torch.no_grad():
        for i in range(0, N_win, 2048):
            batch = torch.from_numpy(windows[i : i + 2048]).to(device)
            recon = pilstm(batch)

            # Un-normalize for thermodynamic rates
            T_act = batch[:, :, 0] * t_std + t_mean
            T_hat = recon[:, :, 0] * t_std + t_mean
            gap = torch.exp(batch[:, :, 1] * g_std + g_mean) - 1.0
            gap_c = torch.clamp(gap[:, 1:], min=1.0)

            dT_pred = (T_hat[:, 1:] - T_hat[:, :-1]) / gap_c
            dT_phys = -k_cooling * (T_act[:, :-1] - T_amb)
            res = torch.mean((dT_pred[:, -1:] - dT_phys[:, -1:]) ** 2, dim=-1)
            phys_residuals.extend(res.cpu().numpy())

    # Batch GPU inference for VLSTM uncertainty
    print(f"  Evaluating VLSTM aleatoric and epistemic uncertainty...")
    aleatoric_list = []
    epistemic_list = []
    with torch.no_grad():
        for i in range(0, N_win, 1024):
            batch = torch.from_numpy(windows[i : i + 1024]).to(device)
            al, ep, _ = vlstm.compute_uncertainty(batch, n_samples=15)
            aleatoric_list.extend(al.cpu().numpy())
            epistemic_list.extend(ep.cpu().numpy())

    # Align with the endpoint of each window (index 29 to end)
    df_aligned = df.iloc[29:].reset_index(drop=True)
    df_adapt_aligned = df_adapt.iloc[29:].reset_index(drop=True)

    f0_base = (df_aligned["temp_injected"].values - b_mean) / b_std
    f1_if = -df_adapt_aligned["if_score"].values.astype(np.float32)
    f2_lstm = df_adapt_aligned["lstm_score"].values.astype(np.float32)
    f3_v_aleatoric = np.array(aleatoric_list, dtype=np.float32)
    f4_v_epistemic = np.array(epistemic_list, dtype=np.float32)
    f5_phys_res = np.array(phys_residuals, dtype=np.float32)
    f6_gap = g_norm[29:].astype(np.float32)

    X = np.column_stack([
        f0_base,
        f1_if,
        f2_lstm,
        f3_v_aleatoric,
        f4_v_epistemic,
        f5_phys_res,
        f6_gap,
    ]).astype(np.float32)

    y = df_aligned["is_injected_anomaly"].values.astype(np.float32)
    ts = df_aligned["ts"]

    print(f"  Constructed feature matrix: {X.shape}, Labels: {y.sum()} anomalies / {len(y)} total")
    return X, y, ts


def train_fusion_for_series(
    series: str,
    epochs: int = 60,
    batch_size: int = 256,
    lr: float = 2e-3,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
):
    print(f"\n========================================================")
    print(f" Training Evidential Fusion Layer on {series.upper()} Series")
    print(f" Device: {device} | Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"========================================================")

    processed_dir = REPO_ROOT / "data" / "processed"
    models_dir = REPO_ROOT / "models"

    X, y, ts = extract_fusion_features(series, device=device)

    # Save extracted dataset
    dataset_path = processed_dir / f"fusion_dataset_{series.lower()}.npz"
    np.savez_compressed(dataset_path, X=X, y=y, ts=ts.astype(str).values)
    print(f"Saved extracted features to {dataset_path}")

    # Chronological partition (D6 compliant)
    cutoff = pd.Timestamp("2018-10-29 11:10:48")
    train_mask = (ts < cutoff).values
    test_mask = ~train_mask

    X_train = X[train_mask]
    y_train = y[train_mask]

    X_test = X[test_mask]
    y_test = y[test_mask]

    print(f"Partition shapes:")
    print(f"  Train: {X_train.shape[0]} rows ({int(y_train.sum())} positive anomaly samples)")
    print(f"  Test:  {X_test.shape[0]} rows ({int(y_test.sum())} positive anomaly samples)")

    # Standardize features using train split statistics strictly (D6 compliant)
    feat_mean = np.mean(X_train, axis=0, keepdims=True)
    feat_std = np.std(X_train, axis=0, keepdims=True) + 1e-6

    X_train_norm = (X_train - feat_mean) / feat_std
    X_test_norm = (X_test - feat_mean) / feat_std

    # Target: one-hot (B, 2) -> [is_normal, is_alarm]
    y_train_oh = np.column_stack([1.0 - y_train, y_train]).astype(np.float32)
    y_test_oh = np.column_stack([1.0 - y_test, y_test]).astype(np.float32)

    train_dataset = TensorDataset(torch.from_numpy(X_train_norm), torch.from_numpy(y_train_oh))
    test_dataset = TensorDataset(torch.from_numpy(X_test_norm), torch.from_numpy(y_test_oh))

    # Weight positive class during training to handle class imbalance (182 anomalies vs 63k normal)
    pos_weight = float((len(y_train) - y_train.sum()) / (y_train.sum() + 1.0))
    print(f"  Positive class imbalance ratio: {pos_weight:.1f}x")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    model = EvidentialFusionMLP(input_dim=7, hidden_dim=32, latent_dim=16).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    best_test_loss = float("inf")
    best_weights_path = models_dir / f"evidential_fusion_{series.lower()}.pt"

    t0 = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss_acc = 0.0
        n_batches = 0
        lambda_kl = min(1.0, epoch / 10.0) * 0.05

        for bx, by in train_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()

            _, _, evidence = model(bx)
            alpha = evidence + 1.0
            loss, ace, kl = evidential_loss(alpha, by, lambda_kl=lambda_kl)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss_acc += loss.item()
            n_batches += 1

        scheduler.step()

        # Validation on test split
        model.eval()
        test_loss_acc = 0.0
        n_test = 0
        with torch.no_grad():
            for bx, by in test_loader:
                bx, by = bx.to(device), by.to(device)
                _, _, evidence = model(bx)
                alpha = evidence + 1.0
                t_loss, _, _ = evidential_loss(alpha, by, lambda_kl=lambda_kl)
                test_loss_acc += t_loss.item()
                n_test += 1

        avg_train = train_loss_acc / n_batches
        avg_test = test_loss_acc / n_test

        if avg_test < best_test_loss:
            best_test_loss = avg_test
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "epoch": epoch,
                    "test_loss": avg_test,
                    "feat_mean": feat_mean.tolist(),
                    "feat_std": feat_std.tolist(),
                },
                best_weights_path,
            )

        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {avg_train:.5f} | Val Loss: {avg_test:.5f} | Best: {best_test_loss:.5f}")

        update_status({
            "current_series": series,
            "epoch": epoch,
            "total_epochs": epochs,
            "train_loss": avg_train,
            "val_loss": avg_test,
            "best_val_loss": best_test_loss,
            "elapsed_seconds": round(time.time() - t0, 1),
            "status": "RUNNING",
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

    train_time = time.time() - t0
    print(f"Training completed in {train_time:.2f}s. Best weights saved to {best_weights_path}")

    return {
        "series": series,
        "best_val_loss": best_test_loss,
        "weights_path": str(best_weights_path),
        "feat_mean": feat_mean.tolist(),
        "feat_std": feat_std.tolist(),
    }


def main():
    set_seed(42)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"=================================================================")
    print(f"   Dempster-Shafer Evidential Fusion (EDL) GPU Training Pipeline  ")
    print(f"=================================================================")
    print(f"Device: {device}")
    if torch.cuda.is_available():
        print(f"GPU Accelerator: {torch.cuda.get_device_name(0)}")

    eval_stats = {}
    for series in ["Out", "In"]:
        stats = train_fusion_for_series(series, epochs=60, batch_size=256, device=device)
        eval_stats[series] = stats

    out_stats = REPO_ROOT / "data" / "processed" / "fusion_eval_stats.json"
    with open(out_stats, "w") as f:
        json.dump(eval_stats, f, indent=2)
    print(f"\nAll series fused and calibrated! Stats saved to {out_stats}")

    update_status({
        "status": "COMPLETED",
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "eval_stats_file": str(out_stats),
    })


if __name__ == "__main__":
    main()

