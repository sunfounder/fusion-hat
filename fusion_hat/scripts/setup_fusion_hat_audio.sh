#!/bin/bash

# global variables
# =================================================================
VERSION="1.0.1"
USERNAME=${SUDO_USER:-$LOGNAME}
# 安全地获取用户 ID
USER_ID=$(id -u "${USERNAME}" 2>/dev/null || echo "1000")
USER_RUN="sudo -u ${USERNAME} XDG_RUNTIME_DIR=/run/user/${USER_ID} DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/${USER_ID}/bus"
SKIP_TEST=false

# 检测是否在终端环境中
if [ -t 1 ]; then
    TERMINAL=true
else
    TERMINAL=false
fi

POSSIBLE_CONFIGS=(
    "/boot/config.txt"
    "/boot/firmware/config.txt"
    "/boot/firmware/current/config.txt"
)
CONFIG=""
for config in "${POSSIBLE_CONFIGS[@]}"; do
    if test -f $config; then
        CONFIG=$config
        break
    fi
done

ASOUND_CONF="/etc/asound.conf"

DTOVERLAY="googlevoicehat-soundcard"
AUDIO_CARD_NAME="sndrpigooglevoi"
ALSA_CARD_NAME="snd_rpi_googlevoicehat_soundcar"
HAT_NAME="Fusion Hat"

_is_install_deps=true
_is_with_mic=true
_cleanup=false

success() {
    if [ "$TERMINAL" = true ]; then
        echo -e "$(tput setaf 2 2>/dev/null)$1$(tput sgr0 2>/dev/null)"
    else
        echo "[SUCCESS] $1"
    fi
}

info() {
    if [ "$TERMINAL" = true ]; then
        echo -e "$(tput setaf 6 2>/dev/null)$1$(tput sgr0 2>/dev/null)"
    else
        echo "[INFO] $1"
    fi
}

warning() {
    if [ "$TERMINAL" = true ]; then
        echo -e "$(tput setaf 3 2>/dev/null)$1$(tput sgr0 2>/dev/null)"
    else
        echo "[WARNING] $1"
    fi
}

error() {
    if [ "$TERMINAL" = true ]; then
        echo -e "$(tput setaf 1 2>/dev/null)$1$(tput sgr0 2>/dev/null)"
    else
        echo "[ERROR] $1"
    fi
}

newline() {
    echo ""
}

confirm() {
    if [ "$FORCE" == '-y' ]; then
        true
    else
        read -r -p "$1 [y/N] " response </dev/tty
        if [[ $response =~ ^(yes|y|Y)$ ]]; then
            true
        else
            false
        fi
    fi
}

sudocheck() {
    if [ $(id -u) -ne 0 ]; then
        warning "Install must be run as root. Try 'sudo bash ./i2samp.sh'"
        exit 1
    fi
}

ask_reboot() {
    read -e -p "$(tput setaf 5)$1 (Y/N): $(tput sgr0)" choice
    if [ "$choice" == "Y" ] || [ "$choice" == "y" ]; then
        info "Rebooting now ..."
        sudo sync && sudo reboot
    fi
}

get_soundcard_index() {
    card_name=$1
    if [[ -z "${card_name}" ]]; then
        error "card_name is null"
        return
    fi
    card_index=$(sudo aplay -l | grep $card_name | awk '{print $2}' | tr -d ':')
    echo $card_index
}

config_asound() {
    # backup file
    if [ -e "${ASOUND_CONF}" ]; then
        if [ -e "${ASOUND_CONF}.old" ]; then
            sudo rm -f "${ASOUND_CONF}.old"
        fi
        sudo cp "${ASOUND_CONF}" "${ASOUND_CONF}.old"
    fi

    sudo cat >"${ASOUND_CONF}" <<EOF

pcm.hat {
    type asym
    playback.pcm {
        type plug
        slave.pcm "speaker"
    }
    capture.pcm {
        type plug
        slave.pcm "mic"
    }
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

ctl.dmixer {
    type hw
    card ${AUDIO_CARD_NAME}
}

pcm.speaker {
    type softvol
    slave {
        pcm "dmixer"
    }
    control {
        name "${HAT_NAME} Playback Volume"
        card ${AUDIO_CARD_NAME}
    }
    min_dB -51.0
    max_dB 0.0
}

pcm.mic_hw {
    type hw
    card ${AUDIO_CARD_NAME}
    device 0
}

pcm.mic {
    type softvol
    slave {
        pcm "mic_hw"
    }
    control {
        name "${HAT_NAME} Capture Volume"
        card ${AUDIO_CARD_NAME}
    }
    min_dB -26.0
    max_dB 25.0
}

ctl.hat {
    type hw
    card ${AUDIO_CARD_NAME}
}

pcm.!default hat
ctl.!default hat

EOF

}

get_sink_index() {
    card_name=$1
    if [[ -z "${card_name}" ]]; then
        error "card name is null"
        return
    fi
    index=$($USER_RUN \
        pactl -f json list sinks | jq -r \
        '.[] | select(.["properties"]["alsa.card_name"] == "'${card_name}'"
        and .["properties"]["device.class"] == "sound"
        ).index')
    echo $index
}

get_source_index() {
    card_name=$1
    if [[ -z "${card_name}" ]]; then
        error "card name is null"
        return
    fi
    index=$($USER_RUN \
        pactl -f json list sources | jq -r \
        '.[] | select(.["properties"]["alsa.card_name"] == "'${card_name}'"
        and .["properties"]["device.class"] == "sound"
        ).index')
    echo $index
}

set_default_sink() {
    sink_index=$1
    if [[ -z "${sink_index}" ]]; then
        error "sink index is null"
        return
    fi
    $USER_RUN \
        pactl set-default-sink ${sink_index}
}

set_default_source() {
    source_index=$1
    if [[ -z "${source_index}" ]]; then
        error "source index is null"
        return
    fi
    $USER_RUN \
        pactl set-default-source ${source_index}
}

set_default_sink_volume() {
    volume=$1
    if [[ -z "${volume}" ]]; then
        error "volume is null"
        return
    fi
    $USER_RUN \
        pactl set-sink-volume @DEFAULT_SINK@ ${volume}%
}

set_default_source_volume() {
    volume=$1
    if [[ -z "${volume}" ]]; then
        error "volume is null"
        return
    fi
    $USER_RUN \
        pactl set-source-volume @DEFAULT_SOURCE@ ${volume}%
}

APT_INSTALL_PKGS=(
    "i2c-tools"
    "alsa-utils"
    "pulseaudio"
    "pulseaudio-utils"
    "jq"
    "sox"
)

# main_fuction
# ================================================================================
install_soundcard_driver() {
    info "Setup Fusion Hat audio driver >>>"
    info "script version: $VERSION"
    info "user: $USERNAME"

    # check root
    # =====================================
    sudocheck

    # apt install packages
    # =====================================
    if $_is_install_deps; then
        newline
        info "apt update..."
        apt update

        info "install apt packages ..."
        apt install ${APT_INSTALL_PKGS[@]} -y
    else
        info "skip install deps ..."
    fi

    # --- load dtoverlay ---
    newline
    info "Trying to load dtoverlay ${DTOVERLAY} ..."
    dtoverlay ${DTOVERLAY}
    sleep 1

    # --- get sound card ---
    info "get_soundcard_index ..."
    card_index=$(get_soundcard_index $AUDIO_CARD_NAME)
    if [[ -z "${card_index}" ]]; then
        error "soundcard index not found. Sometimes you need to reboot to activate the soundcard."
        ask_reboot "Would you like to reboot and retry now?"
        warning "Unfinished"
        exit 1
    else
        success "soundcard ${AUDIO_CARD_NAME} index: ${card_index}"
    fi

    # --- config /etc/asound.conf ---
    newline
    info "config /etc/asound.conf ..."
    config_asound

    # restart alsa-utils
    sudo systemctl restart alsa-utils 2>/dev/null
    # set volume 100%
    info "set ALSA speaker volume to 100% ..."
    play -n trim 0.0 0.5 2>/dev/null || true # play a short sound to activate alsamixer speaker vol control
    # 尝试多种方式设置音量，避免因控制名称问题而失败
    amixer -c ${AUDIO_CARD_NAME} sset "${HAT_NAME} Playback Volume" 100% 2>/dev/null || \
    amixer -c ${AUDIO_CARD_NAME} sset "Playback" 100% 2>/dev/null || \
    amixer -c ${AUDIO_CARD_NAME} sset "Master" 100% 2>/dev/null || \
    info "Failed to set speaker volume, but continuing..."
    
    if $_is_with_mic; then
        info "set ALSA microphone volume to 100% ..."
        rec /tmp/rec_test.wav trim 0 0.5 2>/dev/null || true # record a short sound to activate alsamixer mic vol control
        # 尝试多种方式设置麦克风音量
        amixer -c ${AUDIO_CARD_NAME} sset "${HAT_NAME} Capture Volume" 100% 2>/dev/null || \
        amixer -c ${AUDIO_CARD_NAME} sset "Capture" 100% 2>/dev/null || \
        amixer -c ${AUDIO_CARD_NAME} sset "Mic" 100% 2>/dev/null || \
        info "Failed to set microphone volume, but continuing..."
        rm -f /tmp/rec_test.wav 2>/dev/null
    fi

    # --- config pulseaudio ---
    newline
    info "config pulseaudio ..."

    # enable pulseaudio
    # https://www.raspberrypi.com/documentation/computers/configuration.html#audio-config-2
    info "raspi-config enable pulseaudio ..."
    raspi-config nonint do_audioconf 1 2>/dev/null

    # run pulseaudio
    info "run pulseaudio ..."
    # start pulseaudio (只在用户会话存在时尝试)
    if [ -d "/run/user/${USER_ID}" ]; then
        $USER_RUN pulseaudio -D 2>/dev/null || true
    else
        info "User session not found, skipping pulseaudio start."
    fi

    # get sink index
    newline
    info "get_sink_index ..."
    sink_index=$(get_sink_index $ALSA_CARD_NAME)
    if [[ -z "${sink_index}" ]]; then
        error "sink index not found."
        error "Sometimes you need to reboot to activate the soundcard."
    else
        success "sink index: ${sink_index}"
        # set default sink
        info "set default sink ..."
        set_default_sink "${sink_index}"
    fi

    # get source index
    info "get_source_index ..."
    source_index=$(get_source_index $ALSA_CARD_NAME)
    if [[ -z "${source_index}" ]]; then
        error "source index not found."
        error "Sometimes you need to reboot to activate the soundcard."
    else
        success "source index: ${source_index}"
        # set default source
        info "set default source ..."
        set_default_source "${source_index}"
    fi

    # set default volume
    info "set default Pulseaudio volume to 100% ..."
    set_default_sink_volume 100
    set_default_source_volume 100

    # --- test speaker ---
    newline
    if [ "$SKIP_TEST" = "false" ]; then
        if confirm "Do you wish to test speaker now?"; then
            info "open speaker ..."
            # enable speaker
            echo 1 > /sys/class/fusion_hat/fusion_hat/speaker
            # play a short sound to fill data and avoid the speaker overheating
            play -n trim 0.0 0.5 2>/dev/null

            info "testing speaker ..."
            # test speaker
            speaker-test -l3 -c 2 -t wav
        fi
    fi

    # --- Done ---
    newline
    success "All done!"
    newline
}

# main
# =================================================================
for arg in "$@"; do
    case $arg in
    --no-deps)
        _is_install_deps=false
        ;;
    --skip-test)
        SKIP_TEST=true
        ;;
    esac
done

install_soundcard_driver

exit 0
