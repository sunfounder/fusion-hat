#!/bin/bash
# =============================================================================
#  Reset Fusion Hat audio to factory state
#  Use for testing — undoes all changes made by setup_fusion_hat_audio.sh
# =============================================================================
set -e

echo "Resetting Fusion Hat audio to factory state..."

# 1. Remove asound.conf
if [ -f /etc/asound.conf ]; then
    rm -f /etc/asound.conf
    echo "  ✓ removed /etc/asound.conf"
fi

# 2. Remove Wireplumber/Pipewire custom rules
for f in /etc/wireplumber/main.lua.d/*fusion* /etc/pipewire/pipewire.conf.d/*fusion* \
         /usr/share/pipewire/pipewire.conf.d/*fusion* /etc/pipewire/pipewire-pulse.conf.d/*fusion*; do
    if [ -f "$f" ]; then
        rm -f "$f"
        echo "  ✓ removed $f"
    fi
done

# 3. Reset audio config (no-op on modern Pi OS)
echo "  ✓ audio config preserved"

# 4. Remove dynamic DT overlay (ignore errors)
dtoverlay -r googlevoicehat-soundcard 2>/dev/null && echo "  ✓ removed dynamic overlay" || true

# 5. Remove systemd user service
for user_home in /home/*; do
    svc="${user_home}/.config/systemd/user/fusion-hat-default-sink.service"
    if [ -f "$svc" ]; then
        local_uid=$(stat -c '%u' "$user_home" 2>/dev/null)
        user_name=$(id -un "$local_uid" 2>/dev/null || basename "$user_home")
        sudo -u "$user_name" XDG_RUNTIME_DIR="/run/user/${local_uid}" \
            systemctl --user disable fusion-hat-default-sink 2>/dev/null || true
        rm -f "$svc"
        echo "  ✓ removed $svc"
    fi
done

# 6. Restart audio services
for user_home in /home/*; do
    local_uid=$(stat -c '%u' "$user_home" 2>/dev/null)
    [ "$local_uid" -ge 1000 ] 2>/dev/null || continue
    user_name=$(id -un "$local_uid" 2>/dev/null || basename "$user_home")
    sudo -u "$user_name" XDG_RUNTIME_DIR="/run/user/${local_uid}" \
        systemctl --user restart pipewire pipewire-pulse wireplumber 2>/dev/null || true
done

echo ""
echo "Reset complete. Run 'fusion_hat speaker setup' to re-configure."
