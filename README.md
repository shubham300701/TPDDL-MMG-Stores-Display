# 🏪 MMG - STORES (KPM) — Real-Time Inventory & Predictive Demand Display

> Complete hardware and software implementation guide for Tata Power-DDL Material Management Group (Keshavpuram) running on an AOC HDMI monitor powered by Raspberry Pi 3B+ / Windows with Google Sheets sync and **Real Hardware Wi-Fi scanning**.

---

## 📁 Project Directory Structure (`C:\MMG_Stores_KPM_Inventory_Display\`)

* **`start_display_with_wifi.bat`** — **Double-click launcher for Windows**: Automatically starts the Python Wi-Fi bridge daemon and opens the dashboard in your default browser.
* **`wifi_bridge.py`** — **Hardware Wi-Fi Bridge Service**: Cross-platform Python server (Windows & Linux/Raspberry Pi) that scans physical WLAN interfaces (`netsh` / `nmcli`), retrieves live SSIDs, signal strengths, IP addresses, and executes connect/disconnect commands via REST API on port `8765`.
* **`index.html`** — The full-screen 1080p dashboard for your AOC monitor (live clock, font switcher, dark/light theme, straight-aligned 3-day predictive demand, interactive trend charts, and real hardware Wi-Fi scanning).
* **`store_entry_portal.html`** — Maker-Checker 2-tier stock update portal (Storekeeper entry -> Manager PIN confirmation -> instant Google Sheet reflect).
* **`google_apps_script.js`** — Two-way Google Apps Script for live 5-second polling and maker-checker audit logging.
* **`three_year_issue_order_history.csv`** — 3 years of daily historical data (omitting Sundays & gazetted holidays) for 3-day demand forecasting.
* **`raspberry_pi_kiosk_setup.sh`** — Automated kiosk setup script for Raspberry Pi OS to boot directly into full-screen Chromium with the Wi-Fi bridge running in the background.
* **`tata_power_ddl_logo_clean.png`** — High-definition TATA POWER-DDL logo with clean 100% white background.

---

## 📶 Real Hardware Wi-Fi Feature

Unlike mock static interfaces, this dashboard communicates directly with your physical wireless adapter:

1. **How to run on Windows:**
   - Double-click **`start_display_with_wifi.bat`** (or run `python wifi_bridge.py` in terminal).
   - Click the Wi-Fi pill in the top header (`📶 Saxena-5G` or active SSID).
   - The modal displays:
     - Active SSID, internal IP, signal strength, and security.
     - All physical wireless networks detected in range by your wireless card.
     - Password entry panel for connecting to nearby networks.
     - Click **"Scan Again"** to trigger a real physical radio scan.

2. **How to run on Raspberry Pi 3B+:**
   - Run `./raspberry_pi_kiosk_setup.sh`.
   - The script automatically configures `wifi_bridge.py` to start on boot and launches Chromium in kiosk mode at `http://localhost:8765/index.html`.
