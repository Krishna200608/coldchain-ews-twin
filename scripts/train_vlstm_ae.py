"""
scripts/train_vlstm_ae.py
=========================
Trains the Variational LSTM-Autoencoder (VLSTM-AE, Proposal P1) on the college
GPU server (NVIDIA RTX 5000 Ada Generation, 32 GB VRAM).

Features:
- Runs in background or detached sessions with continuous unbuffered logging.
- KL divergence annealing: beta increases linearly from 0 to 1 over first 50 epochs.
- Saves best checkpoints to models/vlstm_{out,in}.pt.
- Calibrates D13 causal uncertainty threshold on train partition.
- Emits real-time progress to logs/vlstm_train_status.json for headless remote monitoring.
"""

import json
import os
import pathlib
import sys
import time
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

# Ensure stdout flushes immediately for live log monitoring via tail -f
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.config import (
    K_SIGMA,
    RANDOM_SEED,
    VLSTM_HIDDEN_SIZE,
    VLSTM_LATENT_DIM,
)
from src.models.vlstm_ae import (
    VLSTMAutoencoder,
    vlstm_loss,
)


def update_status(status_dict: dict):
    status_file = REPO_ROOT / "logs" / "vlstm_train_status.json"
    status_file.parent.mkdir(exist_ok=True)
    with open(status_file, "w") as f:
        json.dump(status_dict, f, indent=2)


def set_seed(seed=RANDOM_SEED):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_vlstm_series(
    series: str,
    epochs: int = 100,
    batch_size: int = 128,
    lr: float = 1e-3,
    annealing_epochs: int = 50,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
):
    print(f"\n========================================================")
    print(f" Training VLSTM-AE on {series.upper()} Series [Device: {device}]")
    print(f" Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"========================================================")

    processed_dir = REPO_ROOT / "data" / "processed"
    models_dir = REPO_ROOT / "models"
    models_dir.mkdir(exist_ok=True)

    train_npz = processed_dir / f"lstm_windows_{series.lower()}_train.npz"
    val_npz = processed_dir / f"lstm_windows_{series.lower()}_val.npz"

    X_train = np.load(train_npz)["windows"].astype(np.float32)
    X_val = np.load(val_npz)["windows"].astype(np.float32)

    print(f"Loaded {len(X_train)} train windows and {len(X_val)} val windows. Shape: {X_train.shape[1:]}")

    train_dataset = TensorDataset(torch.from_numpy(X_train))
    val_dataset = TensorDataset(torch.from_numpy(X_val))

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=False)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model = VLSTMAutoencoder(
        input_size=2,
        hidden_size=VLSTM_HIDDEN_SIZE,
        latent_dim=VLSTM_LATENT_DIM,
        window_length=30,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    best_val_loss = float("inf")
    best_weights_path = models_dir / f"vlstm_{series.lower()}.pt"

    t0 = time.time()
    for epoch in range(1, epochs + 1):
        # KL annealing: linear schedule from 0 to 1 over first annealing_epochs
        beta = min(1.0, epoch / float(annealing_epochs))

        model.train()
        train_loss_acc = 0.0
        train_mse_acc = 0.0
        train_kl_acc = 0.0
        n_batches = 0

        for (batch_x,) in train_loader:
            batch_x = batch_x.to(device)
            optimizer.zero_grad()

            recon, mu, logvar = model(batch_x)
            loss, mse, kl = vlstm_loss(recon, batch_x, mu, logvar, beta=beta)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss_acc += loss.item()
            train_mse_acc += mse.item()
            train_kl_acc += kl.item()
            n_batches += 1

        scheduler.step()

        # Validation
        model.eval()
        val_loss_acc = 0.0
        val_mse_acc = 0.0
        val_kl_acc = 0.0
        n_val_batches = 0

        with torch.no_grad():
            for (batch_val_x,) in val_loader:
                batch_val_x = batch_val_x.to(device)
                val_recon, val_mu, val_logvar = model(batch_val_x)
                v_loss, v_mse, v_kl = vlstm_loss(val_recon, batch_val_x, val_mu, val_logvar, beta=beta)
                val_loss_acc += v_loss.item()
                val_mse_acc += v_mse.item()
                val_kl_acc += v_kl.item()
                n_val_batches += 1

        avg_train_loss = train_loss_acc / n_batches
        avg_train_mse = train_mse_acc / n_batches
        avg_train_kl = train_kl_acc / n_batches

        avg_val_loss = val_loss_acc / n_val_batches
        avg_val_mse = val_mse_acc / n_val_batches
        avg_val_kl = val_kl_acc / n_val_batches

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "epoch": epoch,
                    "val_loss": avg_val_loss,
                    "val_mse": avg_val_mse,
                    "val_kl": avg_val_kl,
                    "beta": beta,
                },
                best_weights_path,
            )

        if epoch % 10 == 0 or epoch == 1:
            print(
                f"Epoch {epoch:03d}/{epochs:03d} | beta={beta:.2f} | "
                f"Train Loss: {avg_train_loss:.5f} (MSE: {avg_train_mse:.5f}, KL: {avg_train_kl:.5f}) | "
                f"Val Loss: {avg_val_loss:.5f} (MSE: {avg_val_mse:.5f}, KL: {avg_val_kl:.5f}) | "
                f"Best Val: {best_val_loss:.5f}"
            )

        # Update persistent monitoring status JSON
        update_status({
            "current_series": series,
            "epoch": epoch,
            "total_epochs": epochs,
            "beta": beta,
            "train_loss": avg_train_loss,
            "val_loss": avg_val_loss,
            "best_val_loss": best_val_loss,
            "elapsed_seconds": round(time.time() - t0, 1),
            "status": "RUNNING",
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

    train_time = time.time() - t0
    print(f"Training {series} completed in {train_time:.2f}s. Best model checkpoint saved to {best_weights_path}")

    # Causal Threshold Calibration (D13 compliant) using MC uncertainty
    checkpoint = torch.load(best_weights_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    print(f"Calibrating D13 uncertainty thresholds on train partition...")
    all_aleatoric = []
    all_epistemic = []

    with torch.no_grad():
        for (bx,) in DataLoader(train_dataset, batch_size=256, shuffle=False):
            bx = bx.to(device)
            aleatoric, epistemic, _ = model.compute_uncertainty(bx, n_samples=15)
            all_aleatoric.extend(aleatoric.cpu().numpy())
            all_epistemic.extend(epistemic.cpu().numpy())

    all_aleatoric = np.array(all_aleatoric)
    all_epistemic = np.array(all_epistemic)

    mu_aleatoric = float(np.mean(all_aleatoric))
    std_aleatoric = float(np.std(all_aleatoric))
    tau_aleatoric = float(mu_aleatoric + K_SIGMA * std_aleatoric)

    mu_epistemic = float(np.mean(all_epistemic))
    std_epistemic = float(np.std(all_epistemic))

    print(f"D13 Causal Calibration Results ({series.upper()}):")
    print(f"  Aleatoric Train Mu:        {mu_aleatoric:.6f}")
    print(f"  Aleatoric Train Std:       {std_aleatoric:.6f}")
    print(f"  Aleatoric Threshold (tau): {tau_aleatoric:.6f} (K_SIGMA={K_SIGMA:.1f})")
    print(f"  Epistemic Train Baseline:  mu={mu_epistemic:.6f}, std={std_epistemic:.6f}")

    return {
        "series": series,
        "best_val_loss": best_val_loss,
        "mu_aleatoric": mu_aleatoric,
        "std_aleatoric": std_aleatoric,
        "tau_aleatoric": tau_aleatoric,
        "mu_epistemic": mu_epistemic,
        "std_epistemic": std_epistemic,
        "weights_path": str(best_weights_path),
    }


def main():
    set_seed(42)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"=================================================================")
    print(f"   Variational LSTM-Autoencoder (VLSTM-AE) GPU Training Pipeline ")
    print(f"=================================================================")
    print(f"Host:           saini (IIITA College GPU Server)")
    print(f"Device:         {device}")
    if torch.cuda.is_available():
        print(f"GPU Model:      {torch.cuda.get_device_name(0)}")
        print(f"Total VRAM:     {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    print(f"PID:            {os.getpid()}")
    print(f"Logging to:     logs/train_vlstm.log")
    print(f"Status file:    logs/vlstm_train_status.json")

    eval_stats = {}
    for series in ["Out", "In"]:
        stats = train_vlstm_series(series, epochs=100, batch_size=128, device=device)
        eval_stats[series] = stats

    out_stats_path = REPO_ROOT / "data" / "processed" / "vlstm_eval_stats.json"
    with open(out_stats_path, "w") as f:
        json.dump(eval_stats, f, indent=2)
    print(f"\nAll series trained and calibrated successfully! Saved stats to {out_stats_path}")

    update_status({
        "status": "COMPLETED",
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "eval_stats_file": str(out_stats_path),
    })


if __name__ == "__main__":
    main()

