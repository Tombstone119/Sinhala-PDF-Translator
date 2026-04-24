#!/usr/bin/env bash
set -euo pipefail

if [ ! -f ".venv/bin/python" ]; then
    echo "Virtual environment not found. Please run './setup.sh' first."
    exit 1
fi

.venv/bin/python main.py
