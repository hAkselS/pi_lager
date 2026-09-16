#!/usr/bin/env bash

if [ "$BENCHTEST" != "1" ]; then
    sudo dtoverlay sdio
fi

SCRIPT_DIR="$HOME/pi_lager"
LOG_DIR="$SCRIPT_DIR/logs"

mkdir -p "$LOG_DIR"

log_number=0
while :; do
    log_file="$LOG_DIR/log_$(printf '%04d' "$log_number")"
    if (set -o noclobber; : > "$log_file") 2>/dev/null; then
        break
    fi
    log_number=$((log_number + 1))
done

source "$SCRIPT_DIR/venv/bin/activate"

export PYTHONUNBUFFERED=1
python -u "$SCRIPT_DIR/pi_logger/serial_command_handler.py" >> "$log_file" 2>&1