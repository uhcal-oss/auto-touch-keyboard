#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Touch Keyboard Manager for Linux / GNOME
Automatically enables the touchscreen on-screen keyboard when no physical keyboard is connected,
and disables it when a physical keyboard is plugged in.

Maintained by @uhcal-oss (Urla Hakan Çeken Anadolu Lisesi Open Source)
"""

import os
import sys
import glob
import time
import signal
import argparse
import subprocess
from gi.repository import Gio, GLib

# Linux input event constants
KEY_A = 30
KEY_SPACE = 57

def test_bit(bit, hex_words):
    """Checks if a given bit is set in the kernel hex capability words."""
    try:
        val = int("".join(hex_words), 16)
        return bool(val & (1 << bit))
    except (ValueError, TypeError):
        return False

def get_real_keyboards():
    """
    Scans /sys/class/input/event* to detect actual physical typing keyboards.
    Filters out ACPI power buttons, sleep buttons, volume knobs, mouse dongles,
    and touchscreen devices.
    """
    keyboards = []
    for dev in sorted(glob.glob("/sys/class/input/event*")):
        name_file = os.path.join(dev, "device/name")
        key_file = os.path.join(dev, "device/capabilities/key")
        if os.path.exists(name_file) and os.path.exists(key_file):
            try:
                with open(name_file, "r") as f:
                    name = f.read().strip()
                with open(key_file, "r") as f:
                    keys = f.read().strip().split()
                
                if keys and keys != ["0"]:
                    # A typing keyboard MUST have both KEY_A and KEY_SPACE
                    if test_bit(KEY_A, keys) and test_bit(KEY_SPACE, keys):
                        # Filter out virtual touchscreen drivers that might advertise keys
                        lower_name = name.lower()
                        if "touch" in lower_name or "screen" in lower_name or "wacom" in lower_name:
                            continue
                        keyboards.append({
                            "event": os.path.basename(dev),
                            "name": name,
                            "path": dev
                        })
            except Exception:
                continue
    return keyboards

def get_current_osk_state():
    """Returns current screen-keyboard-enabled boolean from GSettings."""
    try:
        settings = Gio.Settings.new("org.gnome.desktop.a11y.applications")
        return settings.get_boolean("screen-keyboard-enabled")
    except Exception as e:
        print(f"[!] Error reading GSettings: {e}", file=sys.stderr)
        return False

def set_osk_state(enabled, notify=True):
    """Sets the screen-keyboard-enabled GSetting and sends a notification."""
    try:
        settings = Gio.Settings.new("org.gnome.desktop.a11y.applications")
        current = settings.get_boolean("screen-keyboard-enabled")
        if current != enabled:
            settings.set_boolean("screen-keyboard-enabled", enabled)
            
            # Also ensure universal access panel status is visible when OSK is enabled
            if enabled:
                try:
                    a11y = Gio.Settings.new("org.gnome.desktop.a11y")
                    a11y.set_boolean("always-show-universal-access-status", True)
                except Exception:
                    pass

            if notify:
                title = "Dokunmatik Klavye"
                msg = (
                    "Fiziksel klavye bağlı değil. Ekran klavyesi açıldı."
                    if enabled else
                    "Fiziksel klavye algılandı. Ekran klavyesi kapatıldı."
                )
                try:
                    subprocess.run(
                        ["notify-send", "-a", "Auto Touch Keyboard", "-i", "input-keyboard", title, msg],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception:
                    pass
            print(f"[*] Touchscreen keyboard {'ENABLED' if enabled else 'DISABLED'}")
            return True
        return False
    except Exception as e:
        print(f"[!] Error setting GSettings: {e}", file=sys.stderr)
        return False

def evaluate_and_update(notify=True):
    """Checks keyboards and updates OSK state accordingly."""
    keyboards = get_real_keyboards()
    has_kbd = len(keyboards) > 0
    # Enable OSK if NO physical keyboard is attached
    target_osk = not has_kbd
    changed = set_osk_state(target_osk, notify=notify)
    return has_kbd, keyboards, changed

def print_status():
    """Prints current keyboard and OSK status to stdout."""
    keyboards = get_real_keyboards()
    osk_state = get_current_osk_state()
    
    print("=== Auto Touch Keyboard Status ===")
    print(f"Touchscreen Keyboard Enabled : {'\033[92mYES\033[0m' if osk_state else '\033[93mNO\033[0m'}")
    print(f"Physical Keyboards Connected : {len(keyboards)}")
    
    if keyboards:
        for idx, kbd in enumerate(keyboards, 1):
            print(f"  {idx}. {kbd['name']} ({kbd['event']})")
    else:
        print("  (None detected - Touchscreen keyboard should be active)")

def run_daemon():
    """Runs the background daemon monitoring udev input events."""
    import pyudev
    
    print("[*] Starting Auto Touch Keyboard daemon...", flush=True)
    # Initial evaluation without notification spam
    has_kbd, keyboards, _ = evaluate_and_update(notify=False)
    print(f"[*] Initial scan: {len(keyboards)} keyboard(s) found. OSK active: {not has_kbd}", flush=True)
    
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="input")
    
    # Simple debouncing loop
    last_event_time = 0
    debounce_interval = 0.5  # seconds
    
    try:
        for device in iter(monitor.poll, None):
            if device.action in ("add", "remove"):
                current_time = time.time()
                # Debounce fast multi-interface device bursts
                if current_time - last_event_time >= debounce_interval:
                    time.sleep(0.3)  # wait for sysfs nodes to settle
                    has_kbd, keyboards, changed = evaluate_and_update(notify=True)
                    if changed:
                        print(f"[*] State changed: {len(keyboards)} keyboard(s) found. OSK active: {not has_kbd}", flush=True)
                    last_event_time = time.time()
    except (KeyboardInterrupt, SystemExit):
        print("\n[*] Stopping Auto Touch Keyboard daemon.")

def main():
    parser = argparse.ArgumentParser(
        description="Automatic Touchscreen On-Screen Keyboard Manager"
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="daemon",
        choices=["daemon", "status", "check", "enable", "disable", "toggle"],
        help="Action to perform (default: daemon)"
    )
    args = parser.parse_args()

    if args.action == "status":
        print_status()
    elif args.action == "check":
        has_kbd, keyboards, changed = evaluate_and_update(notify=True)
        print(f"[*] Check complete. {len(keyboards)} keyboard(s) detected. OSK enabled: {not has_kbd}")
    elif args.action == "enable":
        set_osk_state(True, notify=True)
    elif args.action == "disable":
        set_osk_state(False, notify=True)
    elif args.action == "toggle":
        current = get_current_osk_state()
        set_osk_state(not current, notify=True)
    elif args.action == "daemon":
        run_daemon()

if __name__ == "__main__":
    main()
