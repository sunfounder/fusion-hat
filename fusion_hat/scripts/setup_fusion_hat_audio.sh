#!/bin/bash
# =============================================================================
#  Fusion Hat Audio Setup
#  =============================================================================
#  Configures ALSA and PipeWire/PulseAudio for the Fusion Hat I2S sound card.
#  Run once after driver installation. Survives reboot.
#
#  Usage:
#    sudo bash setup_fusion_hat_audio.sh           # full setup + test
#    sudo bash setup_fusion_hat_audio.sh --skip-test  # skip speaker test
#    sudo bash setup_fusion_hat_audio.sh --no-deps    # skip apt install
# =============================================================================

set -e

VERSION="2.0.0"

# ── Configuration ────────────────────────────────────────────────────────────
DTOVERLAY="googlevoicehat-soundcard"
AUDIO_CARD_NAME="sndrpigooglevoi"                    # aplay -l short name
ALSA_CARD_NAME="snd_rpi_googlevoicehat_soundcar"     # ALSA long name (31 chars)
PA_CARD_NAME="snd_rpi_googlevoicehat_soundcar"       # PulseAudio card name
HAT_NAME="Fusion Hat"
ASOUND_CONF="/etc/asound.conf"

SKIP_TEST=false
SKIP_DEPS=false

# ── Detect desktop user ──────────────────────────────────────────────────────
detect_user() {
    # Find the first non-root user with a running session
    for uid_dir in /run/user/*; do
        local uid=$(basename "$uid_dir")
        if [ "$uid" -ge 1000 ] 2>/dev/null; then
            DESKTOP_USER=$(id -un "$uid" 2>/dev/null)
            DESKTOP_UID="$uid"
            return 0
        fi
    done
    # Fallback: find first non-system user
    DESKTOP_USER=$(getent passwd | awk -F: '$3>=1000 && $3<65534 {print $1; exit}')
    DESKTOP_UID=$(id -u "$DESKTOP_USER" 2>/dev/null || echo 1000)
}

RUN_AS_USER=""
detect_user
if [ -n "$DESKTOP_USER" ] && [ -d "/run/user/$DESKTOP_UID" ]; then
    RUN_AS_USER="sudo -u $DESKTOP_USER XDG_RUNTIME_DIR=/run/user/$DESKTOP_UID DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$DESKTOP_UID/bus"
fi

# ── Output helpers ───────────────────────────────────────────────────────────
GREEN='\033[32m'; YELLOW='\033[33m'; CYAN='\033[36m'; BOLD='\033[1m'; RESET='\033[0m'
ok()   { echo -e "  ${GREEN}✓${RESET} $1"; }
warn() { echo -e "  ${YELLOW}⚠${RESET} $1"; }
info() { echo -e "  ${CYAN}•${RESET} $1"; }
stage(){ echo -e "\n${BOLD}── $1 ──${RESET}"; }

# ── Parse args ───────────────────────────────────────────────────────────────
for arg in "$@"; do
    case $arg in
        --no-deps)   SKIP_DEPS=true ;;
        --skip-test) SKIP_TEST=true ;;
    esac
done

echo ""
echo "================================================"
echo "  Fusion Hat Audio Setup  v${VERSION}"
echo "================================================"

# ══════════════════════════════════════════════════════════════════════════════
#  Stage 1: Dependencies
# ══════════════════════════════════════════════════════════════════════════════
stage "Dependencies"

APT_PKGS=(i2c-tools alsa-utils pulseaudio pulseaudio-utils jq sox)

if [ "$SKIP_DEPS" = false ]; then
    info "apt update..."
    apt-get update -qq 2>/dev/null
    info "installing: ${APT_PKGS[*]}"
    apt-get install -y -qq "${APT_PKGS[@]}" 2>/dev/null
    ok "apt packages ready"
else
    info "skip apt (--no-deps)"
fi

# ══════════════════════════════════════════════════════════════════════════════
#  Stage 2: Device tree overlay
# ══════════════════════════════════════════════════════════════════════════════
stage "Sound card"

info "loading dtoverlay ${DTOVERLAY}..."
dtoverlay ${DTOVERLAY} 2>/dev/null || true
sleep 1

card_index=$(aplay -l 2>/dev/null | grep "$AUDIO_CARD_NAME" | awk '{print $2}' | tr -d ':')
if [ -z "$card_index" ]; then
    warn "Sound card not found. Reboot may be needed."
    warn "Run 'fusion_hat speaker setup' again after reboot."
    exit 1
fi
ok "sound card detected (hw:${card_index},0)"

# ══════════════════════════════════════════════════════════════════════════════
#  Stage 3: ALSA configuration
# ══════════════════════════════════════════════════════════════════════════════
stage "ALSA config"

# Backup existing asound.conf
if [ -f "$ASOUND_CONF" ]; then
    cp "$ASOUND_CONF" "${ASOUND_CONF}.old" 2>/dev/null || true
fi

cat > "$ASOUND_CONF" << EOF

pcm.hat {
    type asym
    playback.pcm { type plug; slave.pcm "speaker" }
    capture.pcm  { type plug; slave.pcm "mic" }
}

pcm.speaker_hw {
    type hw
    card ${AUDIO_CARD_NAME}
    device 0
}

pcm.dmixer {
    type dmix
    ipc_key 1024
    ipc_perm 0666
    slave {
        pcm "speaker_hw"
        period_time 0
        period_size 1024
        buffer_size 8192
        rate 44100
        channels 2
    }
}

ctl.dmixer { type hw; card ${AUDIO_CARD_NAME} }

pcm.speaker {
    type softvol
    slave { pcm "dmixer" }
    control { name "${HAT_NAME} Playback Volume"; card ${AUDIO_CARD_NAME} }
    min_dB -51.0; max_dB 0.0
}

pcm.mic_hw { type hw; card ${AUDIO_CARD_NAME}; device 0 }

pcm.mic {
    type softvol
    slave { pcm "mic_hw" }
    control { name "${HAT_NAME} Capture Volume"; card ${AUDIO_CARD_NAME} }
    min_dB -26.0; max_dB 25.0
}

ctl.hat { type hw; card ${AUDIO_CARD_NAME} }

pcm.!default hat
ctl.!default hat

EOF
ok "wrote ${ASOUND_CONF}"

systemctl restart alsa-utils 2>/dev/null || true

# Set ALSA volume — try known control names
play -n trim 0.0 0.5 2>/dev/null || true
for ctrl in "${HAT_NAME} Playback Volume" "${HAT_NAME}" "Playback" "Master"; do
    amixer -c "$AUDIO_CARD_NAME" sset "$ctrl" 100% 2>/dev/null && break
done
ok "ALSA speaker volume set"

play -n trim 0.0 0.5 2>/dev/null || true
rec /tmp/_fh_mic_test.wav trim 0 0.5 2>/dev/null || true
for ctrl in "${HAT_NAME} Capture Volume" "${HAT_NAME}" "Capture" "Mic"; do
    amixer -c "$AUDIO_CARD_NAME" sset "$ctrl" 100% 2>/dev/null && break
done
rm -f /tmp/_fh_mic_test.wav 2>/dev/null
ok "ALSA mic volume set"

# ══════════════════════════════════════════════════════════════════════════════
#  Stage 4: Ensure audio system is ready
# ══════════════════════════════════════════════════════════════════════════════
stage "Audio system"

info "waiting for audio session..."
# Give PipeWire/PulseAudio time to discover the new sound card
sleep 2

# ══════════════════════════════════════════════════════════════════════════════
#  Stage 5: Set default sink (immediate + persistent)
# ══════════════════════════════════════════════════════════════════════════════
stage "Default sink"

if [ -z "$RUN_AS_USER" ]; then
    warn "no desktop user session found — skipping PulseAudio config"
    warn "run 'fusion_hat speaker setup' after login to complete"
else
    # Find Fusion Hat sink name (retry up to 10s)
    sink_name=""
    for i in $(seq 1 10); do
        sink_name=$($RUN_AS_USER pactl -f json list sinks 2>/dev/null | \
            jq -r ".[] | select(.properties[\"alsa.card_name\"] == \"$PA_CARD_NAME\") | .name" 2>/dev/null)
        [ -n "$sink_name" ] && break
        sleep 1
    done

    if [ -n "$sink_name" ]; then
        # Set default sink — Wireplumber persists this to
        # ~/.local/state/wireplumber/default-nodes and restores on reboot.
        $RUN_AS_USER pactl set-default-sink "$sink_name" 2>/dev/null
        ok "default sink → ${sink_name} (survives reboot)"

        # Source
        source_name=$($RUN_AS_USER pactl -f json list sources 2>/dev/null | \
            jq -r ".[] | select(.properties[\"alsa.card_name\"] == \"$PA_CARD_NAME\") | .name" 2>/dev/null)
        if [ -n "$source_name" ]; then
            $RUN_AS_USER pactl set-default-source "$source_name" 2>/dev/null || true
            ok "default source → ${source_name}"
        fi

        # Volume
        $RUN_AS_USER pactl set-sink-volume @DEFAULT_SINK@ 100% 2>/dev/null || true
        $RUN_AS_USER pactl set-source-volume @DEFAULT_SOURCE@ 100% 2>/dev/null || true
        ok "volume 100%"
    else
        warn "Fusion Hat sink not found — may need reboot"
    fi
fi

# ══════════════════════════════════════════════════════════════════════════════
#  Stage 6: Speaker test
# ══════════════════════════════════════════════════════════════════════════════
if [ "$SKIP_TEST" = false ]; then
    stage "Speaker test"

    # Enable speaker
    if [ -w /sys/class/fusion_hat/fusion_hat/speaker ]; then
        echo 1 > /sys/class/fusion_hat/fusion_hat/speaker
    fi

    # Prime the I2S interface with a short burst
    play -n trim 0.0 0.5 2>/dev/null || true

    info "playing test sound..."
    aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null && \
        ok "speaker test passed!" || \
        warn "speaker test failed — check volume or try 'fusion_hat speaker setup' again"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}✓ Audio setup complete${RESET}"
echo ""
echo "  Speaker: fusion_hat speaker test"
echo "  Health:  fusion_hat doctor"
echo ""
