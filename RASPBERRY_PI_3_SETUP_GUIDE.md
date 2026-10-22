# 🍓 TATA POWER-DDL (MMG STORES, KESHAVPURAM)
## Complete Raspberry Pi 3 Setup & Deployment Guide

Congratulations on receiving your **Raspberry Pi 3** board! This guide gives you the complete step-by-step instructions and code to turn your Raspberry Pi 3 into a **24/7 Continuous Store Inventory Kiosk & Smart Rack Display**.

---

## 🎯 What Your Raspberry Pi 3 Will Do

1. **Auto-Boot on Power On:** Plug in power, and within 30 seconds it boots directly into the TATA POWER-DDL store display.
2. **Zero Maintenance / 24/7 Kiosk:**
   - Edge-to-edge fullscreen (no browser address bar, no tabs, no popups).
   - Mouse cursor automatically disappears after 1 second of inactivity.
   - Screen blanking / screen sleep is disabled (display never turns off).
   - Automatic crash recovery (if power fluctuates or browser crashes, it restarts in 3 seconds).
3. **Live Synchronized:**
   - Automatically synchronizes with Google Sheets Cloud Database and Mobile Store Entry Portal.
   - Can display either:
     - **Main Universal Store Monitor** (`index.html`)
     - **Dedicated Per-Rack Display** (`rack_display.html?rack=1`)
     - **All 10 Racks Matrix Overview** (`rack_matrix.html`)

---

## 📋 Prerequisites & Hardware Checklist

| Item | Details |
|---|---|
| **Board** | Raspberry Pi 3 Model B or 3 Model B+ |
| **Power Supply** | 5V / 2.5A Micro-USB power adapter |
| **MicroSD Card** | 16GB or 32GB Class 10 / A1 MicroSD card |
| **Display** | Any HDMI monitor (AOC monitor, TV, or rack mini-display) |
| **HDMI Cable** | Standard HDMI to HDMI cable |
| **Internet** | Wi-Fi network (or Ethernet cable) in the store |
| **Card Reader** | USB MicroSD card reader for your PC/laptop |

---

## 🚀 Step 1: Flash the OS using Raspberry Pi Imager (5 Minutes)

1. On your Windows PC or laptop, download and install **Raspberry Pi Imager**:  
   👉 [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)
2. Insert your MicroSD card into your computer.
3. Open **Raspberry Pi Imager**:
   - **Raspberry Pi Device:** Select `Raspberry Pi 3`
   - **Operating System:** Select `Raspberry Pi OS (32-bit)` *(Recommended with Desktop)*
   - **Storage:** Select your MicroSD card
4. Click **Next**. When prompted *"Would you like to apply OS customization settings?"*, click **EDIT SETTINGS**:
   - **General Tab:**
     - Set Hostname: `tpddl-kiosk`
     - Set Username: `pi`
     - Set Password: `your-password` (e.g. `tpddl123`)
     - Configure wireless LAN:
       - Enter your Wi-Fi SSID and Password
       - Wireless LAN country: `IN` (India)
     - Set Time zone: `Asia/Kolkata`
     - Keyboard layout: `us`
   - **Services Tab:**
     - Check **Enable SSH** (select *Use password authentication*)
5. Click **Save** and then click **YES** to begin writing.
6. Once flashing is verified, eject the MicroSD card.

---

## 🔌 Step 2: Boot Up Your Raspberry Pi 3

1. Insert the flashed MicroSD card into the underside slot of your Raspberry Pi 3.
2. Connect the **HDMI cable** from the Pi 3 to your monitor.
3. (Optional for first boot) Connect a USB keyboard & mouse.
4. Plug in the **Micro-USB 5V 2.5A power supply**.
5. The Red LED (power) and Green LED (activity) will light up. The desktop will appear on your monitor within ~30 seconds, and it will automatically connect to your Wi-Fi!

---

## ⚡ Step 3: Run the 1-Line Automated Installer

You only need to run **ONE SINGLE COMMAND** in the Raspberry Pi terminal. It downloads all files from GitHub, installs all packages, configures 24/7 kiosk mode, and sets up background auto-start services!

### Option A: Directly on the Pi (Desktop Terminal)
Click the black terminal icon at the top left of the Raspberry Pi screen, and paste this command:

```bash
curl -sSL https://raw.githubusercontent.com/shubham300701/TPDDL-MMG-Stores-Display/main/setup_pi_kiosk.sh | bash
```

### Option B: Via SSH from your Windows PC
Open Command Prompt or PowerShell on your Windows laptop (connected to same Wi-Fi) and type:

```bash
ssh pi@tpddl-kiosk.local
# (or ssh pi@<PI_IP_ADDRESS> if hostname doesn't resolve)
```
Enter the password you chose during flashing, then run:

```bash
curl -sSL https://raw.githubusercontent.com/shubham300701/TPDDL-MMG-Stores-Display/main/setup_pi_kiosk.sh | bash
```

---

## ⚙️ What the Installer Script Automatically Does:

1. **Installs System Dependencies:**
   - `chromium-browser` (Full-screen kiosk browser engine)
   - `unclutter` (Hides mouse cursor when not in use)
   - `python3` (Runs the local store Wi-Fi & inventory bridge server)
   - `xdotool` & `x11-xserver-utils` (Screen wake and power tools)
2. **Disables Screen Sleep / Blanking:**
   - Configures `/etc/X11/xorg.conf.d/10-kiosk.conf` so HDMI monitor **never enters standby or blanks out**.
3. **Clones Project Repository:**
   - Clones all project files into `/home/pi/tpddl_display`.
4. **Installs Local Systemd Service (`tpddl-bridge.service`):**
   - Automatically runs `python3 wifi_bridge.py` in the background on port `8765`.
5. **Configures Auto-Start Kiosk Launcher:**
   - Creates `/home/pi/tpddl_display/start_display.sh` with auto-crash-restart loop.
   - Places `.desktop` launcher in `~/.config/autostart/`.
6. **Enables Auto-Login to Desktop:**
   - Pi boots straight to the desktop without asking for username/password.

---

## 🎛️ Step 4: Choose Which Display Screen to Show

You can easily configure the Raspberry Pi 3 to show any screen mode you want! Simply run one of these commands on the Pi:

### 1. Main Universal Store Dashboard (Default 55" Wall Monitor)
Shows all 10 meters, live status, and 3-day predictive demand:
```bash
echo "http://localhost:8765/index.html?kiosk=1" > ~/tpddl_display/dashboard_url.txt
```

### 2. Dedicated Single Rack Display (For Shelf Mounts)
Shows big bold stock numbers, QR code to scan, and analytics for a specific rack (e.g. Rack 1, 2, 3...):
```bash
# For Rack #01 (LTCT Meter):
echo "http://localhost:8765/rack_display.html?rack=1&kiosk=1" > ~/tpddl_display/dashboard_url.txt

# For Rack #02 (Poly Phase Meter):
echo "http://localhost:8765/rack_display.html?rack=2&kiosk=1" > ~/tpddl_display/dashboard_url.txt

# For Rack #03 (HT Meter):
echo "http://localhost:8765/rack_display.html?rack=3&kiosk=1" > ~/tpddl_display/dashboard_url.txt
```

### 3. All 10 Racks Shelf Matrix Overview
Shows a high-level bird's-eye view of all 10 bays side-by-side:
```bash
echo "http://localhost:8765/rack_matrix.html?kiosk=1" > ~/tpddl_display/dashboard_url.txt
```

### 4. Cloud Render URL (Direct Web Access)
If you prefer running directly from Render without the local Python server:
```bash
echo "https://your-app-name.onrender.com/index.html?kiosk=1" > ~/tpddl_display/dashboard_url.txt
```

---

## 🔄 Step 5: Test and Reboot

To activate everything, simply reboot the Pi:

```bash
sudo reboot
```

Within 30 seconds of powering up, your AOC monitor will automatically display the full-screen live inventory system!

---

## 🛠️ How to "Code" & Modify Files on the Raspberry Pi 3

If you want to edit code directly on the Raspberry Pi:

### Method 1: Using VS Code from your PC (Recommended)
1. Install **VS Code** on your Windows laptop.
2. Install the **Remote - SSH** extension.
3. Click the green icon at the bottom-left of VS Code $\rightarrow$ **Connect to Host...** $\rightarrow$ `pi@tpddl-kiosk.local`.
4. Open folder `/home/pi/tpddl_display`.
5. You can now edit HTML, CSS, JavaScript, and Python files with full syntax highlighting!

### Method 2: Pulling Latest Code from Git
Whenever you push changes from your PC to GitHub, simply pull them on the Pi:
```bash
cd ~/tpddl_display
git pull origin main
sudo systemctl restart tpddl-bridge.service
```

### Method 3: Direct Terminal Editing
You can use `nano` inside the Pi terminal:
```bash
nano ~/tpddl_display/index.html
# Press Ctrl+O then Enter to Save, Ctrl+X to Exit
```

---

## 🔍 Useful Diagnostic Commands on the Pi 3

| Command | Purpose |
|---|---|
| `sudo systemctl status tpddl-bridge.service` | Check if background Python server is running |
| `sudo systemctl restart tpddl-bridge.service` | Restart the local Python server |
| `journalctl -u tpddl-bridge.service -f` | View live server logs in real-time |
| `hostname -I` | Find the Raspberry Pi's local IP address |
| `curl http://localhost:8765/api/inventory` | Test live inventory JSON response |
| `killall chromium-browser` | Force restart the kiosk screen |

---

## 💡 Troubleshooting Tips for Raspberry Pi 3

- **Chromium shows "Restore Pages?" popup:** The `start_display.sh` script automatically clears Chromium crash state on every boot to suppress this.
- **Display Resolution:** If connected to an AOC monitor or TV, the Pi 3 will auto-detect 1080p (1920x1080). If you need to force resolution, edit `/boot/firmware/config.txt` (or `/boot/config.txt`).
- **Power Supply Warning (Lightning Bolt icon):** If you see a yellow lightning bolt icon in the top right corner, your power supply is delivering less than 4.8V. Make sure to use a good quality **5V 2.5A** adapter.
