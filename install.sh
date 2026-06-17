#!/bin/bash
# =============================================================================
#  Fusion Hat Installer
#  =============================================================================
#  One-command install:
#    curl -sSL https://raw.githubusercontent.com/sunfounder/fusion-hat/main/install.sh | sudo bash
#
#  Custom branch:
#    FUSION_HAT_BRANCH=develop sudo bash install.sh
# =============================================================================

set -e

# ── Branch overrides (set via environment variable to test feature branches) ──
FUSION_HAT_BRANCH="${FUSION_HAT_BRANCH:-main}"
INSTALLER_BRANCH="${INSTALLER_BRANCH:-main}"

INSTALLER_URL="https://raw.githubusercontent.com/sunfounder/sunfounder-installer-scripts/refs/heads/${INSTALLER_BRANCH}/tools/installer_1.1.0.sh"

# ── Source shared installer utilities ────────────────────────────────────────
curl -fsSL "$INSTALLER_URL" -o /tmp/installer.sh
if [ $? -ne 0 ]; then
    echo "Network error: failed to download installer utilities."
    echo "Please check your internet connection."
    exit 1
fi
source /tmp/installer.sh
rm /tmp/installer.sh

# ── Apt dependencies ─────────────────────────────────────────────────────────
APT_INSTALL_LIST=(
    "git"
    "python3"
    "raspi-config"
    "python3-pip"
    "i2c-tools"
    "espeak"
    "libsdl2-dev"
    "libsdl2-mixer-dev"
    "portaudio19-dev"
    "sox"
    "libttspico-utils"
    "dkms"
)

# ── Parse arguments ─────────────────────────────────────────────────────────
SKIP_AUDIO_TEST=true   # skip speaker test during install; user runs it later
for arg in "$@"; do
    case $arg in
        --plain-text) ;;
        --skip-test) SKIP_AUDIO_TEST=true ;;
        --test)      SKIP_AUDIO_TEST=false ;;
    esac
done

# ── Installation ─────────────────────────────────────────────────────────────

TITLE "Install Fusion Hat Python Library\n"
TITLE "Install dependencies"
RUN "apt-get update" "Update apt"
RUN "apt-get install -y ${APT_INSTALL_LIST[*]}" "Install apt dependencies"

TITLE "Install fusion-hat library"
CD "$HOME/" "Change to home directory"
RUN "rm -rf $HOME/fusion-hat" "Remove existing fusion-hat library"
RUN "git clone --depth=1 --branch ${FUSION_HAT_BRANCH} https://github.com/sunfounder/fusion-hat.git" \
    "Clone fusion-hat library (${FUSION_HAT_BRANCH})"
RUN "chown -R $USERNAME:$USERNAME $HOME/fusion-hat" \
    "Change ownership of fusion-hat library to $USERNAME"

TITLE "Install fusion-hat driver"
CD "$HOME/fusion-hat/driver" "Change to driver directory"
RUN "make all" "Compile driver"
RUN "make install" "Install driver"
RUN "make clean" "Clean driver"
RUN 'config_txt_set "$INSTALLER_CONFIG_TXT_FILE" "dtoverlay=sunfounder-fusionhat"' \
    "Enable driver in config.txt"

TITLE "Install fusion-hat python library"
CD "$HOME/fusion-hat" "Change to fusion-hat directory"
RUN "pip3 install . --break-system-packages" "Install fusion-hat library"
RUN "pip3 uninstall -y RPi.GPIO --break-system-packages" "Uninstall RPi.GPIO"
RUN "register-python-argcomplete -s bash fusion_hat > /etc/bash_completion.d/fusion_hat" \
    "Install tab completion"

TITLE "Setup audio"
if [ "$SKIP_AUDIO_TEST" = true ]; then
    RUN "sudo bash $HOME/fusion-hat/fusion_hat/scripts/setup_fusion_hat_audio.sh --skip-test" \
        "Setup audio (speaker test skipped)"
else
    RUN "sudo bash $HOME/fusion-hat/fusion_hat/scripts/setup_fusion_hat_audio.sh" \
        "Setup audio with speaker test"
fi

installer_install

installer_prompt_reboot "Remember to run 'fusion_hat speaker setup' to enable speaker after reboot."
