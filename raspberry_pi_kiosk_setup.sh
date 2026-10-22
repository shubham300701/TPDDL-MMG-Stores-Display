#!/bin/bash
# ==============================================================================
# TATA POWER-DDL (TPDDL) — MMG STORES (KESHAVPURAM)
# 24/7 RASPBERRY PI 3 CONTINUOUS HDMI STORE DISPLAY KIOSK SETUP
# ==============================================================================
# Target: Raspberry Pi 3B / 3B+ / 4B / 5 running Raspberry Pi OS (Desktop)
# Purpose: Auto-boots directly into full-screen AOC Display monitor, zero sleep,
#          hidden mouse cursor, automatic crash recovery, and auto-sync.
# ==============================================================================

set -e

echo "======================================================================"
echo "⚡ TPDDL MMG STORES — RASPBERRY PI 3 CONTINUOUS KIOSK INSTALLER"
echo "======================================================================"

KIOSK_USER="${USER:-pi}"
KIOSK_HOME="/home/${KIOSK_USER}"
KIOSK_DIR="${KIOSK_HOME}/tpddl_display"
REPO_URL="https://github.com/shubham300701/TPDDL-MMG-Stores-Display.git"

# 1. Update package lists and install required kiosk packages
echo "[1/7] Installing Chromium Browser, Unclutter, X11 tools, and Python..."
sudo apt update
sudo apt install -y chromium-browser unclutter xdotool x11-xserver-utils sed git python3 python3-pip curl

# 2. Prevent screen sleeping, screen blanking, and HDMI power down
echo "[2/7] Configuring display power management (Disabling Screen Blanking)..."
sudo mkdir -p /etc/X11/xorg.conf.d/
cat << 'EOF' | sudo tee /etc/X11/xorg.conf.d/10-kiosk.conf
Section "ServerFlags"
    Option "BlankTime" "0"
    Option "StandbyTime" "0"
    Option "SuspendTime" "0"
    Option "OffTime" "0"
EndSection
EOF

# 3. Download or update the repository files
echo "[3/7] Setting up TPDDL project files in ${KIOSK_DIR}..."
if [ -d "${KIOSK_DIR}/.git" ]; then
    echo "Existing repository found. Pulling latest updates from GitHub..."
    cd "${KIOSK_DIR}"
    git pull origin main || true
elif [ -d "${KIOSK_DIR}" ] && [ -f "${KIOSK_DIR}/wifi_bridge.py" ]; then
    echo "Directory already contains files. Keeping existing setup."
else
    echo "Cloning latest TPDDL repository from GitHub..."
    git clone "${REPO_URL}" "${KIOSK_DIR}"
fi

cd "${KIOSK_DIR}"

# Install any python requirements if needed
if [ -f requirements.txt ]; then
    echo "Checking python dependencies..."
    pip3 install -r requirements.txt 2>/dev/null || true
fi

# 4. Create the startup runner script
echo "[4/7] Creating 24/7 Store Display launcher script..."

cat << 'EOF' > "${KIOSK_DIR}/start_display.sh"
#!/bin/bash
# Disable DPMS and screensaver
xset -dpms
xset s off
xset s noblank

# Hide mouse cursor when inactive for 1 second
unclutter -idle 1 -root &

# Ensure any dirty Chromium crash flags are purged to prevent "Restore Pages?" banner
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' ~/.config/chromium/Default/Preferences 2>/dev/null || true
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' ~/.config/chromium/Default/Preferences 2>/dev/null || true

# Target Dashboard URL (Defaults to local server kiosk view)
DASHBOARD_URL="http://localhost:8765/index.html?kiosk=1"

# If a custom URL or rack display is configured in ~/tpddl_display/dashboard_url.txt, use it:
if [ -f ~/tpddl_display/dashboard_url.txt ]; then
    CUSTOM_URL=$(cat ~/tpddl_display/dashboard_url.txt | tr -d '\r\n')
    if [ -n "$CUSTOM_URL" ]; then
        if [[ "$CUSTOM_URL" == *"?"* ]]; then
            DASHBOARD_URL="${CUSTOM_URL}&kiosk=1"
        else
            DASHBOARD_URL="${CUSTOM_URL}?kiosk=1"
        fi
    fi
fi

echo "Waiting for local bridge server to be ready..."
for i in {1..15}; do
    if curl -s http://localhost:8765/api/inventory >/dev/null 2>&1; then
        echo "Local server is up!"
        break
    fi
    sleep 1
done

echo "Launching TPDDL MMG Display: $DASHBOARD_URL"

# Continuous Kiosk Loop (Restarts automatically if closed or crashed)
while true; do
    chromium-browser \
        --kiosk \
        --noerrdialogs \
        --disable-infobars \
        --no-first-run \
        --fast \
        --fast-start \
        --disable-pinch \
        --overscroll-history-navigation=0 \
        --check-for-update-interval=31536000 \
        --autoplay-policy=no-user-gesture-required \
        "$DASHBOARD_URL"
    
    echo "Chromium closed or crashed. Restarting in 3 seconds..."
    sleep 3
done
EOF

chmod +x "${KIOSK_DIR}/start_display.sh"

# 5. Set up systemd service for local Python Wi-Fi bridge daemon
echo "[5/7] Setting up background local bridge daemon service (tpddl-bridge.service)..."
cat << EOF | sudo tee /etc/systemd/system/tpddl-bridge.service
[Unit]
Description=TPDDL MMG Stores Wi-Fi & Web Bridge Server
After=network.target

[Service]
Type=simple
User=${KIOSK_USER}
WorkingDirectory=${KIOSK_DIR}
ExecStart=/usr/bin/python3 ${KIOSK_DIR}/wifi_bridge.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tpddl-bridge.service
sudo systemctl restart tpddl-bridge.service || true

# 6. Configure Desktop Autostart for Kiosk
echo "[6/7] Configuring auto-start upon desktop login..."
AUTOSTART_DIR="${KIOSK_HOME}/.config/autostart"
mkdir -p "${AUTOSTART_DIR}"

cat << EOF > "${AUTOSTART_DIR}/tpddl_kiosk.desktop"
[Desktop Entry]
Type=Application
Name=TPDDL Store Display Kiosk
Exec=${KIOSK_DIR}/start_display.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

# 7. Enable Console Auto-login via raspi-config non-interactively
echo "[7/7] Ensuring desktop auto-login is active..."
sudo raspi-config nonint do_boot_behaviour B4 || true

echo "======================================================================"
echo "✅ TPDDL RASPBERRY PI 3 SETUP COMPLETED SUCCESSFULLY!"
echo "======================================================================"
echo ""
echo "How to change the display screen on this Raspberry Pi:"
echo "1. Main Universal Store Display:"
echo "   echo 'http://localhost:8765/index.html' > ~/tpddl_display/dashboard_url.txt"
echo ""
echo "2. Dedicated Rack Display (e.g. Rack 1, Rack 2, etc.):"
echo "   echo 'http://localhost:8765/rack_display.html?rack=1' > ~/tpddl_display/dashboard_url.txt"
echo ""
echo "3. All 10 Racks Matrix Overview:"
echo "   echo 'http://localhost:8765/rack_matrix.html' > ~/tpddl_display/dashboard_url.txt"
echo ""
echo "Rebooting now will automatically launch the 24/7 store display:"
echo "sudo reboot"
echo "======================================================================"