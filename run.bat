@echo off
setlocal

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

.venv\Scripts\python main.py
