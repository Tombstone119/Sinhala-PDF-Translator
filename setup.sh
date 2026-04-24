#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo " PDF to Sinhala Translator - First-Time Setup"
echo "============================================"
echo

# ── 1. Verify Python ──────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found."
    echo "Install Python 3.10+ from https://python.org"
    exit 1
fi
echo "Python $(python3 --version) found."

# ── 2. Create virtual environment ─────────────────────────────────────────
if [ -f ".venv/bin/activate" ]; then
    echo "Virtual environment already exists — skipping creation."
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# ── 3. Install / upgrade dependencies ─────────────────────────────────────
echo "Installing dependencies (this may take a minute)..."
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt
echo "Dependencies installed."

# ── 4. Ollama reminder ────────────────────────────────────────────────────
echo
echo "============================================"
echo " IMPORTANT: Ollama setup required"
echo "============================================"
echo " 1. Install Ollama:   https://ollama.com/download"
echo " 2. Pull the model:   ollama pull gemma4:e4b"
echo " 3. Set env variable: OLLAMA_NUM_PARALLEL=2"
echo "    (add to ~/.bashrc or ~/.zshrc, then restart terminal)"
echo " 4. Start Ollama so it picks up the variable."
echo "============================================"
echo
echo "Setup complete! Run './run.sh' to launch the app."
