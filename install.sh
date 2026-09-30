#!/usr/bin/env bash
set -e

# Auto Touch Keyboard Installer
# Urla Hakan Çeken Anadolu Lisesi Open Source (@uhcal-oss)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_PATH="/usr/local/bin/auto-touch-keyboard"
USER_BIN_PATH="${HOME}/.local/bin/auto-touch-keyboard"
USER_SERVICE_DIR="${HOME}/.config/systemd/user"
USER_APP_DIR="${HOME}/.local/share/applications"

echo "=== Auto Touch Keyboard Installer ==="

# 1. Check requirements
echo "[*] Checking Python dependencies..."
if ! python3 -c "import pyudev, gi" &>/dev/null; then
    echo "[*] Installing required packages (python3-pyudev, python3-gobject)..."
    if [ "$EUID" -eq 0 ]; then
        dnf install -y python3-pyudev python3-gobject
    else
        sudo dnf install -y python3-pyudev python3-gobject
    fi
fi

# 2. Install binary
echo "[*] Installing auto-touch-keyboard executable..."
mkdir -p "${HOME}/.local/bin"
install -m 0755 "${SCRIPT_DIR}/auto-touch-keyboard.py" "${USER_BIN_PATH}"

if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
    sudo install -m 0755 "${SCRIPT_DIR}/auto-touch-keyboard.py" "${BIN_PATH}" 2>/dev/null || true
fi

# 3. Install desktop launcher
echo "[*] Installing desktop shortcut..."
mkdir -p "${USER_APP_DIR}"
install -m 0644 "${SCRIPT_DIR}/tr.org.uhcal.auto-touch-keyboard.desktop" "${USER_APP_DIR}/"
if [ -d "${HOME}/Desktop" ]; then
    install -m 0755 "${SCRIPT_DIR}/tr.org.uhcal.auto-touch-keyboard.desktop" "${HOME}/Desktop/"
fi

# 4. Install and enable systemd user service
echo "[*] Configuring systemd user service..."
mkdir -p "${USER_SERVICE_DIR}"
install -m 0644 "${SCRIPT_DIR}/auto-touch-keyboard.service" "${USER_SERVICE_DIR}/auto-touch-keyboard.service"

systemctl --user daemon-reload
systemctl --user enable --now auto-touch-keyboard.service

# 5. Initial check
echo "[*] Evaluating current hardware status..."
"${USER_BIN_PATH}" status

echo ""
echo "[✓] Auto Touch Keyboard successfully installed and running!"
echo "Features:"
echo "  - Dynamically detects physical USB/Bluetooth keyboards."
echo "  - Unplug keyboard -> automatically ENABLES touchscreen keyboard."
echo "  - Plug in keyboard -> automatically DISABLES touchscreen keyboard."
echo "  - Desktop & Top-bar shortcuts for manual toggle anytime."
echo "  - Status check: auto-touch-keyboard status"
