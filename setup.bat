@echo off
setlocal EnableDelayedExpansion

echo ============================================
echo  PDF to Sinhala Translator - First-Time Setup
echo ============================================
echo.

:: ── 1. Verify Python ──────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found on PATH.
    echo Download Python 3.10+ from https://python.org ^(tick "Add to PATH"^).
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo Python %PY_VER% found.

:: ── 2. Create virtual environment ─────────────────────────────────────────
if exist ".venv\Scripts\activate.bat" (
    echo Virtual environment already exists — skipping creation.
) else (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: ── 3. Install / upgrade dependencies ────────────────────────────────────
echo Installing dependencies ^(this may take a minute^)...
.venv\Scripts\pip install --quiet --upgrade pip
.venv\Scripts\pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependency installation failed. See output above.
    pause
    exit /b 1
)
echo Dependencies installed.

:: ── 4. Ollama reminder ────────────────────────────────────────────────────
echo.
echo ============================================
echo  IMPORTANT: Ollama setup required
echo ============================================
echo  1. Install Ollama:   https://ollama.com/download
echo  2. Pull the model:   ollama pull gemma4:e4b
echo  3. Set env variable: OLLAMA_NUM_PARALLEL=2
echo     ^(Windows: System Properties → Environment Variables → New User Variable^)
echo  4. Restart Ollama so the variable takes effect.
echo ============================================
echo.
echo Setup complete! Run "run.bat" to launch the app.
echo.
pause
