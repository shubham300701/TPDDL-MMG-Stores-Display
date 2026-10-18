@echo off
title TATA POWER-DDL MMG Stores KPM - Inventory Display System
cd /d "%~dp0"
echo ===============================================================================
echo     TATA POWER DELHI DISTRIBUTION LIMITED - MMG STORES (KESHAVPURAM)
echo            REAL-TIME INVENTORY & 3-DAY FORECASTING SYSTEM
echo ===============================================================================
echo.
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ to run the local server.
    pause
    exit /b 1
)

echo [2/3] Starting Local Server (wifi_bridge.py) on port 8765...
start /b python wifi_bridge.py
timeout /t 2 /nobreak >nul

echo [3/3] Opening Interactive Dashboard...
start http://localhost:8765/index.html

echo.
echo ===============================================================================
echo  Dashboard URLs:
echo   - Main Web Dashboard (No WiFi Pill):    http://localhost:8765/index.html
echo   - 24/7 Kiosk Display Mode (WiFi Pill):  http://localhost:8765/index.html?kiosk=1
echo   - Mobile Store Entry Portal:            http://localhost:8765/store_entry_portal.html
echo   - Google Sheets Cloud Live Webhook:     Active
echo ===============================================================================
echo.
echo Keep this window open to maintain the local bridge server.
echo To stop the server, press Ctrl+C or close this window.
pause
