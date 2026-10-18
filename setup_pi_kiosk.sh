#!/bin/bash
# ==============================================================================
# TATA POWER-DDL (TPDDL) — MMG STORES (KESHAVPURAM)
# 24/7 RASPBERRY PI CONTINUOUS HDMI STORE DISPLAY KIOSK SETUP
# ==============================================================================
# Target: Raspberry Pi 3B / 4B / 5 running Raspberry Pi OS (Bookworm / Bullseye)
# Purpose: Auto-boot directly into full-screen AOC Display monitor, zero sleep,
#          hidden mouse cursor, automatic crash recovery, and auto-reconnect.
# ==============================================================================

set -e

echo "======================================================================"
echo "⚡ TPDDL MMG STORES — RASPBERRY PI KIOSK INSTALLER"
echo "======================================================================"

# 1. Update package lists and install required kiosk packages
echo "[1/6] Installing Chromium, Unclutter, and X11 utilities..."
sudo apt update
sudo apt install -y chromium-browser unclutter xdotool x11-xserver-utils sed git python3 python3-pip

# 2. Prevent screen sleeping, screen blanking, and HDMI power down
echo "[2/6] Configuring display power management (Disabling Screen Blanking)..."
sudo mkdir -p /etc/X11/xorg.conf.d/
cat << 'EOF' | sudo tee /etc/X11/xorg.conf.d/10-kiosk.conf
Section "ServerFlags"
    Option "BlankTime" "0"
    Option "StandbyTime" "0"
    Option "SuspendTime" "0"
    Option "OffTime" "0"
EndSection
EOF

# 3. Create the startup runner script
echo "[3/6] Creating 24/7 Store Display launcher script..."
KIOSK_USER="${USER:-pi}"
KIOSK_HOME="/home/${KIOSK_USER}"
KIOSK_DIR="${KIOSK_HOME}/tpddl_display"

mkdir -p "${KIOSK_DIR}"

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

# Target Dashboard URL (Defaults to pure kiosk view)
DASHBOARD_URL="http://localhost:8765/index.html?kiosk=1"

# If a custom cloud web URL is configured in ~/tpddl_display/dashboard_url.txt, use it:
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

# 4. Set up systemd service for local Python Wi-Fi bridge daemon
echo "[4/6] Setting up background local bridge daemon service..."
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
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
# Note: enable service once files are copied to ${KIOSK_DIR}

# 5. Configure Wayland/X11 Desktop Autostart
echo "[5/6] Configuring auto-start upon desktop login..."
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

# 6. Enable Console Auto-login via raspi-config non-interactively
echo "[6/6] Ensuring desktop auto-login is active..."
sudo raspi-config nonint do_boot_behaviour B4 || true

echo "======================================================================"
echo "✅ TPDDL KIOSK SETUP COMPLETE!"
echo "To switch between Local Bridge or Cloud Link:"
echo "echo 'https://your-domain-or-cloud-link.html' > ~/tpddl_display/dashboard_url.txt"
echo "Rebooting the Raspberry Pi will now automatically open the live display!"
echo "======================================================================"
