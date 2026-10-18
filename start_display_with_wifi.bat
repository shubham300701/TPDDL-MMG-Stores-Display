@echo off
title MMG Stores KPM - Real Hardware Wi-Fi Bridge
cd /d "%~dp0"
echo ==============================================================
echo   TATA POWER-DDL MMG STORES (KPM) INVENTORY SYSTEM
echo   Starting Real Hardware Wi-Fi Bridge and Dashboard...
echo ==============================================================
echo.
echo Starting Python Wi-Fi bridge daemon on port 8765...
start /b python wifi_bridge.py
timeout /t 2 /nobreak >nul
echo Opening Dashboard in Default Browser...
start http://localhost:8765/index.html
echo.
echo [OK] Bridge is running. Keep this window open while using display.
echo Press Ctrl+C or close this window to stop the bridge.
pause
