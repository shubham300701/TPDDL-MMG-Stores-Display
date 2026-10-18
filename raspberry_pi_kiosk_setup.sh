#!/bin/bash
# =========================================================================
# MMG - STORES (KPM)
# Raspberry Pi 3B+ Automated Kiosk Mode Setup Script with Real Hardware Wi-Fi
#
# Usage:
#   chmod +x raspberry_pi_kiosk_setup.sh
#   ./raspberry_pi_kiosk_setup.sh
# =========================================================================

echo "============================================="
echo " Setting up MMG-Stores Inventory Kiosk on Pi "
echo "============================================="

# 1. Update system packages and install unclutter & network tools
sudo apt update
sudo apt install -y unclutter xdotool chromium-browser network-manager python3

# 2. Create local directory for dashboard
mkdir -p /home/pi/display
cp index.html /home/pi/display/index.html 2>/dev/null || echo "Place index.html in /home/pi/display/"
cp wifi_bridge.py /home/pi/display/wifi_bridge.py 2>/dev/null || echo "Place wifi_bridge.py in /home/pi/display/"
cp -r * /home/pi/display/ 2>/dev/null || true

# 3. Create background service for Hardware Wi-Fi bridge
mkdir -p /home/pi/.config/lxsession/LXDE-pi/
cat << 'EOF' > /home/pi/.config/lxsession/LXDE-pi/autostart
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0.1 -root
@python3 /home/pi/display/wifi_bridge.py &
@sleep 2
@chromium-browser --noerrdialogs --disable-infobars --kiosk --check-for-update-interval=31536000 http://localhost:8765/index.html
EOF

echo "============================================="
echo " Setup complete! Rebooting into kiosk mode... "
echo "============================================="
sudo reboot
