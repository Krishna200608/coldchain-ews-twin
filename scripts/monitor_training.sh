#!/usr/bin/env bash
# scripts/monitor_training.sh
# ===========================
# Headless remote monitor for background GPU training on the college server.
# Run anytime: bash scripts/monitor_training.sh

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=========================================================================="
echo "          COLD CHAIN EWS — GPU BACKGROUND TRAINING MONITOR                "
echo "=========================================================================="
echo "Host: $(hostname) | Time: $(date)"
echo ""

# 1. GPU Status
echo "--- GPU Accelerator Status ---"
if command -v nvidia-smi &>/dev/null; then
    nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader | awk -F', ' '{print "GPU: "$1" | VRAM: "$2" / "$3" | Compute Load: "$4" | Temp: "$5}'
else
    echo "nvidia-smi not found in PATH."
fi
echo ""

# 2. Process Status
echo "--- Background Training Process ---"
PID=$(pgrep -f "scripts/train_vlstm_ae.py" | head -n 1)
if [ -n "$PID" ]; then
    echo "Status: ACTIVE (PID: $PID)"
    ps -p "$PID" -o pid,user,%cpu,%mem,etime,cmd --headers
else
    echo "Status: INACTIVE / FINISHED"
fi
echo ""

# 3. Structured Training State
STATUS_FILE="$REPO_ROOT/logs/vlstm_train_status.json"
if [ -f "$STATUS_FILE" ]; then
    echo "--- Current Training State ---"
    cat "$STATUS_FILE"
    echo ""
fi

# 4. Recent Log Output
LOG_FILE="$REPO_ROOT/logs/train_vlstm.log"
if [ -f "$LOG_FILE" ]; then
    echo "--- Recent Log Output (Last 15 lines from logs/train_vlstm.log) ---"
    tail -n 15 "$LOG_FILE"
    echo ""
fi

echo "=========================================================================="
echo "Useful commands:"
echo "  Follow live output:      tail -f logs/train_vlstm.log"
echo "  Attach to tmux session:  tmux attach -t vlstm_training  (Ctrl+B then D to detach)"
echo "  Re-check this status:    bash scripts/monitor_training.sh"
echo "=========================================================================="
