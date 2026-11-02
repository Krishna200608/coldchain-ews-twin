"""
scripts/train_pilstm_ae.py
==========================
Trains the Physics-Informed LSTM-Autoencoder (PILSTM-AE, Proposal P2) on GPU
using the RTX 5000 Ada Generation accelerator.

Enforces thermodynamic loss regularizer (Newton's Law of Cooling).
Saves:
    - models/pilstm_out.pt
    - models/pilstm_in.pt
    - data/processed/physics_params_out.json
    - data/processed/physics_params_in.json
    - data/processed/pilstm_eval_stats.json
"""

import json
import pathlib
import sys
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.config import (
    PHYSICS_LAMBDA,
    K_SIGMA,
    RANDOM_SEED,
)
from src.models.pilstm_ae import (
    PILSTMAutoencoder,
    physics_informed_loss,
    fit_physics_parameters,
)


def set_seed(seed=RANDOM_SEED):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_pilstm_for_series(
    series: str,
    epochs: int = 50,
    batch_size: int = 128,
    lr: float = 1e-3,
    lambda_physics: float = PHYSICS_LAMBDA,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
):
    print(f"\n========================================================")
    print(f" Training PILSTM-AE on {series.upper()} Series [Device: {device}]")
    print(f"========================================================")

    processed_dir = REPO_ROOT / "data" / "processed"
    models_dir = REPO_ROOT / "models"
    models_dir.mkdir(exist_ok=True)

    # 1. Load pre-computed normalized window tensors
    train_npz = processed_dir / f"lstm_windows_{series.lower()}_train.npz"
    val_npz = processed_dir / f"lstm_windows_{series.lower()}_val.npz"
    norm_json = processed_dir / f"lstm_norm_stats_{series.lower()}.json"

    with open(norm_json, "r") as f:
        norm_stats = json.load(f)

    t_mean = float(norm_stats["temp_injected_mean"])
    t_std = float(norm_stats["temp_injected_std"])
    g_mean = float(norm_stats["log_gap_seconds_mean"])
    g_std = float(norm_stats["log_gap_seconds_std"])

    X_train = np.load(train_npz)["windows"].astype(np.float32)
    X_val = np.load(val_npz)["windows"].astype(np.float32)

    print(f"Loaded {len(X_train)} train windows and {len(X_val)} val windows. Shape: {X_train.shape[1:]}")

    # 2. Fit physics parameters on train split (D6 compliant)
    labeled_csv = processed_dir / f"{series.lower()}_labeled.csv"
    df_labeled = pd.read_csv(labeled_csv, parse_dates=["ts"])
    physics_params = fit_physics_parameters(df_labeled, cutoff_ts="2018-10-29 11:10:48")

    T_amb = physics_params["T_amb"]
    k_cooling = physics_params["k_cooling"]
    sigma_delta = physics_params["sigma_delta"]

    print(f"Calibrated physics parameters:")
    print(f"  T_amb:               {T_amb:.2f} °C")
    print(f"  k_cooling:           {k_cooling:.6f} s^-1")
    print(f"  sigma_delta:         {sigma_delta:.6f} °C/s")
    print(f"  Spike Threshold:     {physics_params['spike_rate_threshold']:.6f} °C/s")

    phys_json_path = processed_dir / f"physics_params_{series.lower()}.json"
    with open(phys_json_path, "w") as f:
        json.dump(physics_params, f, indent=2)
    print(f"Saved physics parameters to {phys_json_path}")

    # 3. Create DataLoaders
    train_dataset = TensorDataset(torch.from_numpy(X_train))
    val_dataset = TensorDataset(torch.from_numpy(X_val))

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=False)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # 4. Initialize model and optimizer
    model = PILSTMAutoencoder(input_size=2, hidden_size=32, window_length=30).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    best_val_loss = float("inf")
    best_weights_path = models_dir / f"pilstm_{series.lower()}.pt"

    t0 = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss_acc = 0.0
        train_mse_acc = 0.0
        train_phys_acc = 0.0
        n_batches = 0

        for (batch_x,) in train_loader:
            batch_x = batch_x.to(device)
            optimizer.zero_grad()

            recon_x = model(batch_x)
            loss, mse, phys = physics_informed_loss(
                x_norm=batch_x,
                x_hat_norm=recon_x,
                t_mean=t_mean,
                t_std=t_std,
                g_mean=g_mean,
                g_std=g_std,
                k_cooling=k_cooling,
                T_amb=T_amb,
                lambda_physics=lambda_physics,
            )

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss_acc += loss.item()
            train_mse_acc += mse.item()
            train_phys_acc += phys.item()
            n_batches += 1

        scheduler.step()

        # Validation pass
        model.eval()
        val_loss_acc = 0.0
        val_mse_acc = 0.0
        val_phys_acc = 0.0
        n_val_batches = 0

        with torch.no_grad():
            for (batch_val_x,) in val_loader:
                batch_val_x = batch_val_x.to(device)
                val_recon_x = model(batch_val_x)
                v_loss, v_mse, v_phys = physics_informed_loss(
                    x_norm=batch_val_x,
                    x_hat_norm=val_recon_x,
                    t_mean=t_mean,
                    t_std=t_std,
                    g_mean=g_mean,
                    g_std=g_std,
                    k_cooling=k_cooling,
                    T_amb=T_amb,
                    lambda_physics=lambda_physics,
                )
                val_loss_acc += v_loss.item()
                val_mse_acc += v_mse.item()
                val_phys_acc += v_phys.item()
                n_val_batches += 1

        avg_train_loss = train_loss_acc / n_batches
        avg_val_loss = val_loss_acc / n_val_batches
        avg_val_mse = val_mse_acc / n_val_batches
        avg_val_phys = val_phys_acc / n_val_batches

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "epoch": epoch,
                    "val_loss": avg_val_loss,
                    "val_mse": avg_val_mse,
                    "val_phys": avg_val_phys,
                    "physics_params": physics_params,
                },
                best_weights_path,
            )

        if epoch % 10 == 0 or epoch == 1:
            print(
                f"Epoch {epoch:02d}/{epochs:02d} | "
                f"Train Loss: {avg_train_loss:.5f} | "
                f"Val Loss: {avg_val_loss:.5f} (MSE: {avg_val_mse:.5f}, Phys: {avg_val_phys:.5f}) | "
                f"Best Val: {best_val_loss:.5f}"
            )

    train_time = time.time() - t0
    print(f"Training completed in {train_time:.2f}s. Best model checkpoint saved to {best_weights_path}")

    # 5. Threshold calibration (D13 compliant): evaluate causal scores on train windows
    checkpoint = torch.load(best_weights_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    with torch.no_grad():
        all_train_scores = []
        for (bx,) in DataLoader(train_dataset, batch_size=256, shuffle=False):
            bx = bx.to(device)
            recon = model(bx)
            # D16: Final-timestep reconstruction MSE
            diff_last = recon[:, -1, :] - bx[:, -1, :]
            mse_last = torch.mean(diff_last ** 2, dim=-1).cpu().numpy()
            all_train_scores.extend(mse_last)

    all_train_scores = np.array(all_train_scores)
    causal_mu = float(np.mean(all_train_scores))
    causal_std = float(np.std(all_train_scores))
    pilstm_thresh = float(causal_mu + K_SIGMA * causal_std)

    print(f"D13 Causal Threshold Calibration for PILSTM ({series.upper()}):")
    print(f"  Train Causal Mean (mu):  {causal_mu:.6f}")
    print(f"  Train Causal Std (std):  {causal_std:.6f}")
    print(f"  Calibrated Threshold (tau): {pilstm_thresh:.6f} (K_SIGMA={K_SIGMA:.1f})")

    return {
        "series": series,
        "best_val_loss": best_val_loss,
        "train_causal_mu": causal_mu,
        "train_causal_std": causal_std,
        "pilstm_threshold": pilstm_thresh,
        "weights_path": str(best_weights_path),
    }


def main():
    set_seed(42)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Launching PILSTM-AE Training on Device: {device}")
    if torch.cuda.is_available():
        print(f"GPU Accelerator: {torch.cuda.get_device_name(0)}")

    eval_stats = {}
    for series in ["Out", "In"]:
        stats = train_pilstm_for_series(series, epochs=50, batch_size=128, device=device)
        eval_stats[series] = stats

    out_stats_path = REPO_ROOT / "data" / "processed" / "pilstm_eval_stats.json"
    with open(out_stats_path, "w") as f:
        json.dump(eval_stats, f, indent=2)
    print(f"\nAll series trained and calibrated! Stats saved to {out_stats_path}")


if __name__ == "__main__":
    main()
