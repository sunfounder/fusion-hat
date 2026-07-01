""" Fusion Hat device related functions

Example:

    Import device module

    >>> from fusion_hat import device

    Enable speaker

    >>> device.enable_speaker()
    >>> device.get_speaker_state()
    True

    Disable speaker

    >>> device.disable_speaker()
    >>> device.get_speaker_state()
    False

    Get user button state

    >>> device.get_usr_btn()
    False

    Get shutdown request state

    >>> device.get_shutdown_request()
    0

    Toggle user LED

    >>> device.set_user_led(True)
    >>> device.set_user_led(False)
    >>> device.set_user_led(1)
    >>> device.set_user_led(0)

    Get firmware version

    >>> device.get_firmware_version()
    '1.1.4'

    Set volume

    >>> device.set_volume(50)

    Get battery voltage

    >>> device.get_battery_voltage()
    8.4
"""

__all__ = [
    'NAME',
    'ID',
    'UUID',
    'PRODUCT_ID',
    'PRODUCT_VER',
    'VENDOR',
    'DTOVERLAY_NAME',
    'is_detected',
    'is_driver_loaded',
    'doctor',
    'is_installed',
    'is_connected',
    'enable_speaker',
    'disable_speaker',
    'get_speaker_state',
    'get_usr_btn',
    'set_led',
    'get_firmware_version',
    'set_volume',
]

import os
from typing import Callable, Any

NAME = "Fusion Hat"
""" Name of the board """

ID = "fusion_hat"
""" ID of the board """

UUID = "9daeea78-0000-0774-000a-582369ac3e02"
""" UUID of the board """

PRODUCT_ID = 0x0774
""" Product ID of the board """

PRODUCT_VER = 0x000a
""" Product version of the board """

VENDOR = "SunFounder"
""" Vendor of the board """ 


DEVICE_PATH = "/sys/class/fusion_hat/fusion_hat/"
DTOVERLAY_NAME = "sunfounder-fusionhat"

def is_detected() -> bool:
    """Check if the driver sysfs interface exists (driver loaded).

    Returns:
        bool: True if /sys/class/fusion_hat/ exists
    """
    return is_driver_loaded()

def is_driver_loaded() -> bool:
    """ Check if Fusion Hat driver is loaded

    This function checks if the Fusion Hat driver module is loaded by
    verifying the existence of /sys/class/fusion_hat/ directory.

    Returns:
        bool: True if driver is loaded, False otherwise
    """
    BASE_PATH = "/sys/class/fusion_hat/"
    return os.path.exists(BASE_PATH)

def is_installed() -> bool:
    """ Check if a Fusion Hat board is installed

    .. deprecated::
        Use :func:`is_detected` instead. This function will be removed in a future version.

    Returns:
        bool: True if installed, False otherwise
    """
    import warnings
    warnings.warn(
        "is_installed is deprecated, use is_detected instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return is_detected()

def is_connected():
    """ Check if Fusion HAT is connected

    .. deprecated::
        Use :func:`is_driver_loaded` instead. This function will be removed in a future version.

    Returns:
        bool: True if connected
    """
    import warnings
    warnings.warn(
        "is_connected is deprecated, use is_driver_loaded instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return is_driver_loaded()

def raise_if_fusion_hat_not_ready() -> bool:
    """ Check if Fusion HAT is ready

    Checks whether the sysfs interface exists (driver loaded and working).
    If not, prompts the user to run ``fusion_hat doctor`` to diagnose and fix.

    Returns:
        bool: True if ready
    """
    if not is_driver_loaded():
        raise IOError(
            "Fusion Hat driver not loaded (sysfs interface missing). "
            "Run 'fusion_hat doctor' to diagnose and fix."
        )

def _find_config_txt() -> str:
    """Locate the active Raspberry Pi config.txt file.

    Returns:
        str: path to config.txt (may not exist)
    """
    candidates = [
        "/boot/firmware/config.txt",
        "/boot/config.txt",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return candidates[0]  # default for Bookworm


def _has_dtoverlay() -> bool:
    """Check if dtoverlay=sunfounder-fusionhat is already in config.txt.

    Returns:
        bool: True if the uncommented dtoverlay line exists
    """
    config = _find_config_txt()
    if not os.path.isfile(config):
        return False
    try:
        with open(config, "r") as f:
            for line in f:
                stripped = line.strip()
                if f"dtoverlay={DTOVERLAY_NAME}" in stripped and not stripped.startswith("#"):
                    return True
    except Exception:
        pass
    return False


def _add_dtoverlay() -> bool:
    """Ensure dtoverlay=sunfounder-fusionhat is active in config.txt.

    - Already active → no-op
    - Commented out → uncomment
    - Not present → append

    Returns:
        bool: True if the line is active after the call
    """
    from ._utils import run_command

    config = _find_config_txt()
    if not os.path.isfile(config):
        return False
    if _has_dtoverlay():
        return True
    try:
        line = f"dtoverlay={DTOVERLAY_NAME}"
        # Check for commented-out line and uncomment it
        _, has_commented = run_command(
            f"grep -q '^# *{line}' {config} 2>/dev/null && echo yes || echo no",
            timeout=5,
        )
        if has_commented.strip() == "yes":
            run_command(
                f"sudo sed -i 's/^# *{line}.*/{line}/' {config}",
                timeout=10,
            )
        else:
            run_command(
                f"echo '{line}' | sudo tee -a {config} > /dev/null 2>&1",
                timeout=10,
            )
        return _has_dtoverlay()
    except Exception:
        return False


def _remove_dtoverlay() -> bool:
    """Remove dtoverlay=sunfounder-fusionhat from config.txt.

    Uses sudo sed since the file requires root.

    Returns:
        bool: True if the line was removed or not present
    """
    from ._utils import run_command

    config = _find_config_txt()
    if not os.path.isfile(config):
        return False
    if not _has_dtoverlay():
        return True
    try:
        run_command(
            f"sudo sed -i '/^dtoverlay={DTOVERLAY_NAME}/d' {config}",
            timeout=10,
        )
        return not _has_dtoverlay()
    except Exception:
        return False


I2C_SCAN_TIMEOUT = 5  # seconds timeout for i2cdetect

# ── doctor helpers ───────────────────────────────────────────────────────────

GREEN  = "\033[32m"
RED    = "\033[31m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def _icon(ok: bool) -> str:
    return f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"

def _print_check(name: str, ok: bool, detail: str = "", indent: int = 2):
    """Print a single check result inline, clearing previous spinner."""
    import sys
    pad = " " * indent
    d = f" ({detail})" if detail else ""
    sys.stdout.write(f"\r{pad}{_icon(ok)} {name}{d}\033[K\n")
    sys.stdout.flush()

def _print_section(title: str):
    print(f"\n  {BOLD}{title}{RESET}")
    print(f"  {'─' * 40}")

# ── driver checks ────────────────────────────────────────────────────────────

def _check_sysfs() -> tuple:
    ok = os.path.exists("/sys/class/fusion_hat/")
    return ok, "" if ok else "/sys/class/fusion_hat not found"

def _check_module_loaded() -> tuple:
    ok = os.path.exists("/sys/module/fusion_hat")
    return ok, "" if ok else "module not loaded"

def _check_i2c_mcu() -> tuple:
    from ._utils import run_command
    try:
        _, out = run_command("sudo i2cdetect -y 1 0x10 0x1f 2>/dev/null",
                             timeout=I2C_SCAN_TIMEOUT)
        for line in out.strip().split("\n"):
            if line.startswith("10:"):
                entries = line[3:].strip().split()
                if len(entries) > 7 and entries[7] in ("17", "UU"):
                    return True, ""
        return False, "MCU not responding at 0x17"
    except Exception:
        return False, "i2cdetect failed"

def _check_dtoverlay_driver() -> tuple:
    ok = _has_dtoverlay()
    return ok, "" if ok else f"dtoverlay={DTOVERLAY_NAME} not in config.txt"

def _check_module_file() -> tuple:
    import platform
    kv = platform.uname().release
    ko_paths = [
        f"/lib/modules/{kv}/extra/fusion_hat.ko",
        f"/lib/modules/{kv}/updates/fusion_hat.ko",
        f"/lib/modules/{kv}/extra/fusion_hat.ko.xz",
        f"/lib/modules/{kv}/updates/fusion_hat.ko.xz",
        f"/lib/modules/{kv}/updates/dkms/fusion_hat.ko.xz",
        f"/lib/modules/{kv}/updates/dkms/fusion_hat.ko",
    ]
    ok = any(os.path.exists(p) for p in ko_paths)
    return ok, "" if ok else "fusion_hat.ko not installed"

# ── audio checks ─────────────────────────────────────────────────────────────

AUDIO_CARD_NAME = "sndrpigooglevoi"
# PulseAudio uses the full DT name (up to 31 chars), while aplay -l
# truncates it.  Both variants identify the Fusion Hat sound card.
AUDIO_CARD_NAMES = (AUDIO_CARD_NAME, "snd_rpi_googlevoicehat_soundcar")

def _check_sound_card() -> tuple:
    """Check Fusion HAT sound card (speaker) via ALSA."""
    from ._utils import run_command
    _, out = run_command("aplay -l 2>/dev/null")
    if AUDIO_CARD_NAME in out:
        return True, ""
    return False, "sound card not found"

def _check_capture_device() -> tuple:
    """Check Fusion HAT mic via ALSA."""
    from ._utils import run_command
    _, out = run_command("arecord -l 2>/dev/null")
    if AUDIO_CARD_NAME in out:
        return True, ""
    return False, "capture device not found"


# ── I2S clock health check ───────────────────────────────────────────────────

PCM_CLK_PATH = "/sys/kernel/debug/clk/clk_summary"


def _check_asound_conf() -> tuple:
    """Check that /etc/asound.conf routes to the Fusion Hat card."""
    asound_path = "/etc/asound.conf"
    if not os.path.isfile(asound_path):
        return False, "/etc/asound.conf not found"
    try:
        with open(asound_path, "r") as f:
            content = f.read()
        if AUDIO_CARD_NAME in content:
            return True, ""
        return False, f"{AUDIO_CARD_NAME} not referenced in asound.conf"
    except Exception:
        return False, "cannot read /etc/asound.conf"


def _check_pa_default_sink() -> tuple:
    """Check that PulseAudio default sink is the Fusion Hat card."""
    import subprocess
    import pwd

    # Find a non-root user
    username = None
    uid = None
    for user in pwd.getpwall():
        if user.pw_uid >= 1000 and user.pw_uid < 65534:
            username = user.pw_name
            uid = user.pw_uid
            break
    if username is None:
        return True, "no user session — skipped"

    env = {
        "XDG_RUNTIME_DIR": f"/run/user/{uid}",
        "DBUS_SESSION_BUS_ADDRESS": f"unix:path=/run/user/{uid}/bus",
    }
    try:
        result = subprocess.run(
            ["sudo", "-u", username, "env",
             f"XDG_RUNTIME_DIR=/run/user/{uid}",
             f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus",
             "pactl", "info"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return True, "pulseaudio not running — skipped"

        # Find default sink name
        default_sink = None
        for line in result.stdout.split("\n"):
            if line.startswith("Default Sink:"):
                default_sink = line.split(":", 1)[1].strip()
                break
        if not default_sink:
            return True, "no default sink — skipped"

        # Check if it belongs to Fusion Hat
        result2 = subprocess.run(
            ["sudo", "-u", username, "env",
             f"XDG_RUNTIME_DIR=/run/user/{uid}",
             f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus",
             "pactl", "-f", "json", "list", "sinks"],
            capture_output=True, text=True, timeout=5,
        )
        import json
        sinks = json.loads(result2.stdout)
        for s in sinks:
            if s.get("name") == default_sink:
                card = s.get("properties", {}).get("alsa.card_name", "")
                for name_variant in AUDIO_CARD_NAMES:
                    if name_variant in card:
                        return True, ""
                return False, f"default sink is '{card}' not Fusion Hat"
        return False, "default sink not found in sink list"
    except FileNotFoundError:
        return True, "pactl not available — skipped"
    except Exception:
        return True, "pulseaudio check failed — skipped"


def _check_alsa_volume() -> tuple:
    """Check that ALSA speaker volume is not zero or muted."""
    from ._utils import run_command
    # Try both possible control names
    for ctrl in ("Fusion Hat", "Fusion Hat Playback Volume", "Playback", "Master"):
        _, out = run_command(
            f"amixer -c {AUDIO_CARD_NAME} sget '{ctrl}' 2>/dev/null",
            timeout=5,
        )
        if out and "Playback" in out:
            # Check if volume is > 0 and not muted
            if "[0%]" in out or "[off]" in out or "[0dB]" in out:
                return False, f"speaker volume is 0% or muted (control: {ctrl})"
            return True, ""
    return True, "volume control not found — skipped"


def _read_pcm_enable_count() -> int:
    """Read the current PCM clock enable count from debugfs.

    Returns:
        int: enable count (first numeric column for 'pcm' row),
             or -1 if the clock summary is not accessible.
    """
    try:
        if not os.path.isfile(PCM_CLK_PATH):
            return -1
        with open(PCM_CLK_PATH, "r") as f:
            for line in f:
                if " pcm " in line or line.strip().startswith("pcm "):
                    parts = line.strip().split()
                    # Format: name  enable  prepare  protect  rate  ...
                    # The pcm line is indented, first numeric col is enable count
                    for p in parts:
                        if p.isdigit():
                            return int(p)
        return -1
    except Exception:
        return -1


def _check_i2s_clock() -> tuple:
    """Check if the I2S PCM clock actually starts during playback.

    Plays a brief silent tone via ALSA and verifies that the PCM clock's
    enable count increases.  A stuck count (especially 0 both before and
    during playback) means the I2S peripheral is not responding.

    Returns:
        (bool, str): True if the clock started, False with a diagnostic
                     message otherwise.
    """
    from ._utils import run_command

    # Only run if the sound card exists — otherwise skip with an ok result
    # because the missing-card check already catches that case.
    _, aplay_out = run_command("aplay -l 2>/dev/null")
    if AUDIO_CARD_NAME not in aplay_out:
        return True, "sound card not available — skipped"

    # Get card index for hw:X,0
    card_index = None
    for line in aplay_out.split("\n"):
        if AUDIO_CARD_NAME in line:
            parts = line.split()
            if parts:
                idx = parts[1].rstrip(":")
                if idx.isdigit():
                    card_index = idx
                    break
    if card_index is None:
        return True, "cannot determine card index — skipped"

    before = _read_pcm_enable_count()
    if before < 0:
        # debugfs not available — skip the check
        return True, "debugfs not mounted — skipped"

    # Play a very short silent audio to trigger hw_params -> clock enable.
    # We use sox to generate 0.1s of near-silence and aplay to push it.
    import tempfile
    import subprocess

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name
        # Generate 0.5s tone at 48 kHz / S32_LE / stereo (long enough to
        # reliably catch the PCM clock enable before aplay exits).
        subprocess.run(
            ["sox", "-n", "-r", "48000", "-b", "32", "-c", "2",
             wav_path, "synth", "0.5", "sin", "440"],
            capture_output=True, timeout=5
        )
        if not os.path.isfile(wav_path):
            return True, "sox not available — skipped"

        proc = subprocess.Popen(
            ["aplay", "-D", f"hw:{card_index},0", wav_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        import time
        time.sleep(0.2)  # give hw_params a moment to set up the clock

        during = _read_pcm_enable_count()
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        finally:
            # Clean up temp file
            try:
                os.unlink(wav_path)
            except OSError:
                pass

        if during > before:
            return True, ""
        elif during == 0 and before == 0:
            return False, "I2S clock stuck — PCM enable count stayed 0 during playback"
        else:
            return False, f"I2S clock anomaly — before={before} during={during}"

    except FileNotFoundError:
        return True, "sox/aplay not available — skipped"
    except Exception as e:
        return True, f"check failed: {e} — skipped"


def _get_fusion_hat_pa_sink() -> str:
    """Find the PulseAudio sink name for the Fusion Hat sound card.

    Returns:
        str: sink name like ``alsa_output.platform-soc_sound.stereo-fallback``,
             or empty string if not found.
    """
    import subprocess
    import pwd

    # Find a non-root user to run pactl as
    username = None
    uid = None
    for user in pwd.getpwall():
        if user.pw_uid >= 1000 and user.pw_uid < 65534:
            username = user.pw_name
            uid = user.pw_uid
            break
    if username is None:
        return ""

    try:
        result = subprocess.run(
            ["sudo", "-u", username, "env",
             f"XDG_RUNTIME_DIR=/run/user/{uid}",
             f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus",
             "pactl", "-f", "json", "list", "sinks"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return ""
        import json
        sinks = json.loads(result.stdout)
        for s in sinks:
            props = s.get("properties", {})
            card_name = props.get("alsa.card_name", "")
            if any(v in card_name for v in AUDIO_CARD_NAMES):
                return s.get("name", "")
    except Exception:
        pass
    return ""


def _set_pa_default_sink(sink_name: str) -> bool:
    """Set the PulseAudio default sink.

    Runs as the first non-root user (typically 'pi') via sudo.
    """
    import subprocess
    import pwd

    # Find a non-root user to run pactl as
    username = None
    uid = None
    for user in pwd.getpwall():
        if user.pw_uid >= 1000 and user.pw_uid < 65534:
            username = user.pw_name
            uid = user.pw_uid
            break
    if username is None:
        return False

    try:
        subprocess.run(
            ["sudo", "-u", username, "env",
             f"XDG_RUNTIME_DIR=/run/user/{uid}",
             f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus",
             "pactl", "set-default-sink", sink_name],
            capture_output=True, timeout=5,
        )
        return True
    except Exception:
        return False


def _fix_i2s_stuck() -> bool:
    """Attempt to fix a stuck I2S peripheral.

    Two-step fix for the "BCLK + LRCLK stuck HIGH / speaker hot" issue:

      1. **PulseAudio routing** — Ensure the default sink is the Fusion Hat
         card, not the built-in headphone jack.  When Pipewire/PulseAudio
         routes audio to the wrong card, the I2S clock never starts.

      2. **Trigger hw_params** — Play a brief tone via ``play`` (sox) to
         force the ALSA ``hw_params`` call which configures the I2S
         registers correctly.

    Returns:
        bool: True if PCM clock enable count increased after the fix.
    """
    import subprocess
    import time

    # ── Step 1: fix PulseAudio default sink ──────────────────────────
    sink = _get_fusion_hat_pa_sink()
    if sink:
        _set_pa_default_sink(sink)

    # ── Step 2: enable speaker + trigger hw_params ───────────────────
    speaker_path = os.path.join(DEVICE_PATH, "speaker")
    if os.path.exists(speaker_path):
        try:
            with open(speaker_path, "w") as f:
                f.write("1")
        except Exception:
            pass

    # Play a tone long enough to be caught by the clock check
    before = _read_pcm_enable_count()
    try:
        proc = subprocess.Popen(
            ["play", "-n", "synth", "0.5", "sin", "440"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(0.6)
        during = _read_pcm_enable_count()
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        return during > before
    except FileNotFoundError:
        pass
    except Exception:
        pass

    # Fallback: direct hw access via aplay
    try:
        result = subprocess.run(
            ["aplay", "-l"], capture_output=True, text=True, timeout=5
        )
        card_index = None
        for line in (result.stdout + result.stderr).split("\n"):
            if AUDIO_CARD_NAME in line:
                parts = line.split()
                if len(parts) > 1:
                    idx = parts[1].rstrip(":")
                    if idx.isdigit():
                        card_index = idx
                        break
        if card_index is None:
            return False

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name
        subprocess.run(
            ["sox", "-n", "-r", "48000", "-b", "32", "-c", "2",
             wav_path, "synth", "0.5", "sin", "440"],
            capture_output=True, timeout=5
        )
        if not os.path.isfile(wav_path):
            return False

        before2 = _read_pcm_enable_count()
        proc = subprocess.Popen(
            ["aplay", "-D", f"hw:{card_index},0", wav_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(0.6)
        during2 = _read_pcm_enable_count()
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        finally:
            try:
                os.unlink(wav_path)
            except OSError:
                pass
        return during2 > before2
    except Exception:
        return False


# TODO: re-enable when confirmed needed
# def _check_audio_modules() -> tuple:
#     """Check if WM8960 sound modules are loaded."""
#     from ._utils import run_command
#     _, out = run_command("lsmod 2>/dev/null")
#     missing = []
#     for mod in ["snd_soc_wm8960", "snd_soc_rpi_googlevoicehat"]:
#         if mod not in out:
#             missing.append(mod)
#     if missing:
#         return False, "missing: " + ", ".join(missing)
#     return True, ""


def doctor(fix_mode: bool = False) -> dict:
    """Live hardware health check — prints results as each check runs.

    Sections:
      Driver  — sysfs, module, I2C MCU, dtoverlay, module file
      Audio   — sound card, capture device, I2S clock health

    Args:
        fix_mode: If True, summary messages adapt for ``--fix`` mode
                  (don't suggest running ``--fix`` again).

    Returns:
        dict with keys: overall, driver_ok, audio_ok, results (per-check dict)
    """
    import sys
    from ._utils import run_command

    results = {}
    driver_ok = True
    audio_ok = True

    print("")
    print("=" * 50)
    print("  Fusion Hat Doctor")
    print("=" * 50)

    # ── Driver ──
    _print_section("Driver")

    checks = [
        ("sysfs interface",       _check_sysfs),
        ("kernel module loaded",  _check_module_loaded),
        ("I2C MCU (0x17)",        _check_i2c_mcu),
        ("dtoverlay in config.txt", _check_dtoverlay_driver),
        ("kernel module file",    _check_module_file),
    ]

    for name, func in checks:
        sys.stdout.write(f"  ... {name}\r")
        sys.stdout.flush()
        ok, detail = func()
        results[name] = ok
        if not ok:
            driver_ok = False
        _print_check(name, ok, detail)

    results["driver_ok"] = driver_ok

    # ── Audio ──
    _print_section("Audio")

    audio_checks = [
        ("sound card (speaker)",    _check_sound_card),
        ("capture device (mic)",    _check_capture_device),
        ("asound.conf",             _check_asound_conf),
        ("PulseAudio default sink", _check_pa_default_sink),
        ("ALSA speaker volume",     _check_alsa_volume),
        ("I2S clock (PCM)",         _check_i2s_clock),
    ]

    for name, func in audio_checks:
        sys.stdout.write(f"  ... {name}\r")
        sys.stdout.flush()
        ok, detail = func()
        results[name] = ok
        if not ok:
            audio_ok = False
        _print_check(name, ok, detail)

    i2s_ok = results.get("I2S clock (PCM)", True)
    if not i2s_ok:
        audio_ok = False
    results["audio_ok"] = audio_ok

    # ── Summary ──
    dtoverlay_ok = results.get("dtoverlay in config.txt", False)
    sysfs_ok = results.get("sysfs interface", False)
    overall = driver_ok and audio_ok
    results["overall"] = overall

    print("")
    if not dtoverlay_ok:
        print(f"  {YELLOW}dtoverlay not configured{RESET}")
        _print_fix_hint(fix_mode)
    elif not sysfs_ok:
        print(f"  {YELLOW}dtoverlay configured but reboot needed{RESET}")
        _print_fix_hint(fix_mode)
    else:
        if driver_ok and audio_ok:
            print(f"  {GREEN}All checks passed.{RESET}")
        else:
            if not driver_ok:
                print(f"  {YELLOW}Driver issues found.{RESET}")
            if not audio_ok:
                print(f"  {YELLOW}Audio issues found.{RESET}")
            _print_fix_hint(fix_mode)
    print("")
    print("=" * 50)
    print("")

    return results


def _print_fix_hint(fix_mode: bool = False):
    """Print a hint to run ``--fix``, or skip if already in fix mode."""
    if not fix_mode:
        print(f"  → Run: {BOLD}fusion_hat doctor --fix{RESET}")


def _find_driver_src() -> str:
    """Find the Fusion Hat driver source directory."""
    import platform
    candidates = []
    try:
        import fusion_hat
        pkg_dir = os.path.dirname(fusion_hat.__file__)
        repo = os.path.dirname(pkg_dir)
        candidates.append(os.path.join(repo, "driver"))
    except Exception:
        pass
    candidates += [
        "/home/pi/fusion-hat/driver",
        os.path.expanduser("~/fusion-hat/driver"),
    ]
    try:
        kv = platform.uname().release
        candidates.append(f"/usr/src/fusion_hat-{kv}")
    except Exception:
        pass
    for p in candidates:
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "Makefile")):
            return os.path.realpath(p)
    return ""


def doctor_fix() -> dict:
    """Run doctor and attempt to fix driver issues found.

    Handles: I2C enable, driver install, dtoverlay, modprobe.
    Returns dict with before, fixes, after, reboot.
    """
    from ._utils import run_command
    import time

    before = doctor(fix_mode=True)
    fixes = []
    reboot = False

    # ── audio auto-fix: PulseAudio default sink wrong ────────────────────
    if before.get("PulseAudio default sink") is False:
        print(f"\n  {YELLOW}PulseAudio default sink is wrong — fixing...{RESET}")
        sink = _get_fusion_hat_pa_sink()
        if sink and _set_pa_default_sink(sink):
            fixes.append(f"set PA default sink to {sink}")
            time.sleep(0.3)
            pa_after, _ = _check_pa_default_sink()
            if pa_after:
                print(f"  {GREEN}PulseAudio default sink fixed{RESET}")
            else:
                print(f"  {YELLOW}PA sink still wrong after retry{RESET}")
        else:
            fixes.append("failed to set PA default sink")

    # ── audio auto-fix: I2S clock stuck ──────────────────────────────────
    if before.get("I2S clock (PCM)") is False:
        print(f"\n  {YELLOW}I2S clock stuck — trying auto-fix (trigger hw_params)...{RESET}")
        if _fix_i2s_stuck():
            fixes.append("triggered I2S hw_params via playback")
            time.sleep(0.3)
            after_i2s = _check_i2s_clock()
            if after_i2s[0]:
                print(f"  {GREEN}I2S clock recovered{RESET}")
            else:
                print(f"  {YELLOW}I2S still stuck after retry — try 'fusion_hat speaker setup'{RESET}")
        else:
            fixes.append("failed to trigger I2S hw_params")

    if before["overall"]:
        return {"before": before, "fixes": fixes, "after": before, "fixed": True, "reboot": False}

    # I2C not enabled
    if not os.path.exists("/dev/i2c-1"):
        fixes.append("enable I2C")
        run_command("sudo raspi-config nonint do_i2c 0 2>/dev/null")
        run_command("sudo modprobe i2c-dev 2>/dev/null")

    # Module file missing
    if not before.get("kernel module file", True):
        driver_dir = _find_driver_src()
        if driver_dir:
            fixes.append(f"install driver from {driver_dir}")
            run_command(f"cd {driver_dir} && sudo make modules_install 2>/dev/null")
            run_command("sudo depmod -a 2>/dev/null")
        else:
            fixes.append("driver source not found — cannot auto-install")

    dtoverlay_ok = before.get("dtoverlay in config.txt", False)
    sysfs_ok = before.get("sysfs interface", False)
    module_loaded = before.get("kernel module loaded", False)

    # dtoverlay
    if not dtoverlay_ok:
        if _add_dtoverlay():
            fixes.append(f"dtoverlay={DTOVERLAY_NAME} added to config.txt")
            reboot = True
        else:
            fixes.append("failed to add dtoverlay to config.txt")
    # dtoverlay configured but sysfs not working → reboot needed
    if dtoverlay_ok and not sysfs_ok:
        fixes.append("dtoverlay configured, reboot required to activate")
        reboot = True
    else:
        # Module not loaded
        if not module_loaded:
            fixes.append("modprobe fusion_hat")
            run_command("sudo modprobe fusion_hat 2>/dev/null")
            if not os.path.exists("/sys/module/fusion_hat"):
                reboot = True

        # Module loaded but sysfs missing
        if module_loaded and not sysfs_ok:
            fixes.append("reload fusion_hat module")
            run_command("sudo rmmod fusion_hat 2>/dev/null")
            run_command("sudo modprobe fusion_hat 2>/dev/null")

    print(f"\n  --- Fixes ---")
    for action in fixes:
        print(f"  → {action}")

    # Quick re-check after fixes
    after = {
        "sysfs interface": os.path.exists("/sys/class/fusion_hat/"),
        "kernel module loaded": os.path.exists("/sys/module/fusion_hat"),
    }
    # Re-check I2C
    try:
        _, out = run_command("sudo i2cdetect -y 1 0x10 0x1f 2>/dev/null",
                             timeout=I2C_SCAN_TIMEOUT)
        i2c_ok = False
        for line in out.strip().split("\n"):
            if line.startswith("10:"):
                entries = line[3:].strip().split()
                if len(entries) > 7 and entries[7] in ("17", "UU"):
                    i2c_ok = True
                    break
        after["I2C MCU (0x17)"] = i2c_ok
    except Exception:
        after["I2C MCU (0x17)"] = False
    after["dtoverlay in config.txt"] = _has_dtoverlay()
    after["overall"] = all(after.values())

    if reboot and not after["overall"]:
        return {"before": before, "fixes": fixes, "after": after, "fixed": False, "reboot": True}

    return {"before": before, "fixes": fixes, "after": after, "fixed": after["overall"], "reboot": reboot}

def force_dt_overlay() -> bool:
    """Force-add dtoverlay=sunfounder-fusionhat to config.txt.

    This is the primary way to configure the Fusion HAT device-tree overlay.
    Required for the kernel driver to load and detect the HAT.

    Returns:
        bool: True if the line was added or already present
    """
    from ._utils import run_command

    if _has_dtoverlay():
        print("dtoverlay=sunfounder-fusionhat is already in config.txt.")
        return True
    if not _add_dtoverlay():
        print("Failed to write config.txt. Check permissions.")
        return False

    print("Added dtoverlay=sunfounder-fusionhat to config.txt.")
    try:
        answer = input("  Reboot now to apply? (y/N): ").strip().lower()
        if answer in ("y", "yes"):
            print("  Rebooting...")
            run_command("sudo reboot 2>&1")
        else:
            print("  Reboot later with: sudo reboot")
    except (KeyboardInterrupt, EOFError):
        print("")
        print("  Reboot later with: sudo reboot")
    return True


def remove_dt_overlay() -> bool:
    """Remove dtoverlay=sunfounder-fusionhat from config.txt.

    Returns:
        bool: True if the line was removed or not present
    """
    if not _has_dtoverlay():
        print("dtoverlay=sunfounder-fusionhat is not in config.txt.")
        return True
    if _remove_dtoverlay():
        print("Removed dtoverlay=sunfounder-fusionhat from config.txt.")
        print("Run 'sudo reboot' if the HAT was previously working via this overlay.")
        return True
    print("Failed to update config.txt. Check permissions.")
    return False


def uninstall() -> bool:
    """Uninstall Fusion HAT: driver, DKMS, overlay, config, Python package.

    Removes: loaded module, DKMS registration + source, .ko files,
    .dtbo overlay, dtoverlay from config.txt, and the Python package.

    Returns:
        bool: True if uninstall succeeded (or nothing to do)
    """
    import platform
    from ._utils import run_command

    print("")
    print("=" * 60)
    print("  Fusion HAT Uninstall")
    print("=" * 60)
    print("")

    kv = platform.uname().release
    ok = True

    # 1. Unload the module
    print("  [1/6] Unloading kernel module...")
    if os.path.exists("/sys/module/fusion_hat"):
        _, out = run_command("sudo rmmod fusion_hat 2>&1")
        if os.path.exists("/sys/module/fusion_hat"):
            print(f"  [FAIL] Could not unload fusion_hat: {out.strip()}")
            ok = False
        else:
            print("  [OK] fusion_hat module unloaded")
    else:
        print("  [OK] fusion_hat not loaded")

    # 2. DKMS uninstall
    print("  [2/6] Removing DKMS registration...")
    _, dkms_status = run_command("dkms status fusion_hat 2>/dev/null || true")
    if dkms_status.strip():
        for line in dkms_status.strip().split("\n"):
            ver = line.split("/")[1].split(",")[0].strip() if "/" in line else ""
            if ver:
                run_command(f"sudo dkms remove -m fusion_hat -v {ver} --all 2>/dev/null")
        _, dkms_after = run_command("dkms status fusion_hat 2>/dev/null || true")
        if not dkms_after.strip():
            print("  [OK] DKMS registration removed")
        else:
            print(f"  [!] DKMS may still have entries: {dkms_after.strip()}")
    else:
        print("  [OK] Not registered with DKMS")

    import glob as _glob
    for dkms_dir in _glob.glob("/usr/src/fusion_hat-*"):
        run_command(f"sudo rm -rf {dkms_dir} 2>/dev/null")

    # 3. Remove module files
    print("  [3/6] Removing kernel module files...")
    ko_paths = [
        f"/lib/modules/{kv}/extra/fusion_hat.ko",
        f"/lib/modules/{kv}/updates/fusion_hat.ko",
        f"/lib/modules/{kv}/extra/fusion_hat.ko.xz",
        f"/lib/modules/{kv}/updates/fusion_hat.ko.xz",
    ]
    removed = 0
    for p in ko_paths:
        if os.path.isfile(p):
            run_command(f"sudo rm -f {p} 2>/dev/null")
            if not os.path.isfile(p):
                removed += 1
    run_command("sudo depmod -a 2>/dev/null")
    print(f"  [OK] Removed {removed} module file(s)")

    # 4. Remove dtbo from overlays
    print("  [4/6] Removing device-tree overlay (.dtbo)...")
    dtbo_name = "sunfounder-fusionhat.dtbo"
    overlay_dirs = [
        "/boot/firmware/overlays",
        "/boot/overlays",
    ]
    dtbo_removed = False
    for d in overlay_dirs:
        p = os.path.join(d, dtbo_name)
        if os.path.isfile(p):
            run_command(f"sudo rm -f {p} 2>/dev/null")
            dtbo_removed = True
    print(f"  [OK] {'Removed' if dtbo_removed else 'Not found'}")

    # 5. Remove dtoverlay from config.txt
    print("  [5/6] Removing dtoverlay from config.txt...")
    if _has_dtoverlay():
        if _remove_dtoverlay():
            print("  [OK] dtoverlay removed from config.txt")
        else:
            print("  [FAIL] Could not remove dtoverlay from config.txt")
            ok = False
    else:
        print("  [OK] No dtoverlay in config.txt")

    # 6. Uninstall Python package
    print("  [6/6] Uninstall Python package...")
    _, pip_out = run_command(
        "pip show fusion-hat 2>/dev/null | grep -i location",
        timeout=10,
    )
    if pip_out.strip():
        _, out = run_command(
            "sudo pip uninstall -y fusion-hat --break-system-packages 2>&1",
            timeout=30,
        )
        if "Successfully uninstalled" in out:
            print("  [OK] Python package uninstalled")
        else:
            print(f"  [!] pip uninstall returned: {out.strip()[-120:]}")
    else:
        print("  [OK] Python package not found")

    print("")
    if ok:
        print("  Uninstall complete. Reboot to fully clean up.")
    else:
        print("  Uninstall completed with some issues. Check output above.")
    print("")
    print("=" * 60)
    print("")

    return ok


def require_fusion_hat(func: Callable[..., Any]) -> Callable[..., Any]:
    """ Decorator to require Fusion HAT

    Args:
        func (Callable[..., Any]): function to decorate

    Returns:
        Callable[..., Any]: decorated function
    """
    def wrapper(*arg, **kwargs):
        raise_if_fusion_hat_not_ready()
        return func(*arg, **kwargs)
    return wrapper

@require_fusion_hat
def enable_speaker() -> None:
    """ Enable speaker """
    PATH = DEVICE_PATH + "speaker"
    with open(PATH, "w") as f:
        f.write("1")

@require_fusion_hat
def disable_speaker() -> None:
    """ Disable speaker """
    PATH = DEVICE_PATH + "speaker"
    with open(PATH, "w") as f:
        f.write("0")

@require_fusion_hat
def get_speaker_state() -> bool:
    """ Get speaker state

    Returns:
        bool: True if enabled
    """
    PATH = DEVICE_PATH + "speaker"
    with open(PATH, "r") as f:
        state = f.read()[:-1] # [:-1] rm \n
        return state == "1"

@require_fusion_hat
def get_usr_btn() -> bool:
    """ Get user button state

    Returns:
        bool: True if pressed
    """
    PATH = DEVICE_PATH + "button"
    with open(PATH, "r") as f:
        state = f.read()[:-1] # [:-1] rm \n
        return state == "1"

@require_fusion_hat
def get_charge_state() -> bool:
    """ [Deprecated] Get charge state

    Returns:
        bool: True if charging
    """
    print("Warning: get_charge_state is deprecated, please use get_charge_state instead.")
    path = f"/sys/class/power_supply/fusion-hat/charge_state"
    with open(path, "r") as f:
        state = f.read()[:-1] # [:-1] rm \n
        return state == "1"

@require_fusion_hat
def get_battery_voltage() -> float:
    """ [Deprecated] Get battery voltage

    Returns:
        float: battery voltage(V)
    """
    print("Warning: get_battery_voltage is deprecated, please use get_battery_voltage instead.")
    path = f"/sys/class/power_supply/fusion-hat/voltage_now"
    with open(path, "r") as f:
        voltage = f.read().strip()
        voltage = float(voltage) / 1000
    return voltage

def get_shutdown_request() -> None:
    """ [Deprecated] Get shutdown request """
    raise NotImplementedError("get_shutdown_request is deprecated.")

@require_fusion_hat
def set_led(state: [int, bool]) -> None:
    """ Set led state

    Args:
        state (int or bool): 0:off, 1:on, True:on, False:off
    """
    path = f"{DEVICE_PATH}led"
    with open(path, "w") as f:
        f.write(str(int(state)))

@require_fusion_hat
def get_led() -> bool:
    """ Get led state

    Returns:
        bool: True if on
    """
    path = f"{DEVICE_PATH}led"
    with open(path, "r") as f:
        state = f.read().strip()
    return state == "1"

@require_fusion_hat
def get_firmware_version() -> str:
    """ Get firmware version

    Returns:
        str: firmware version
    """
    path = f"{DEVICE_PATH}firmware_version"
    with open(path, "r") as f:
        version = f.read().strip()
    return version

@require_fusion_hat
def get_driver_version() -> str:
    """ Get driver version
    
    Returns:
        str: driver version
    """
    path = f"{DEVICE_PATH}version"
    with open(path, "r") as f:
        version = f.read().strip()
    return version

def set_volume(value: int) -> None:
    """ Set volume

    Args:
        value (int): volume(0~100)
    """
    value = min(100, max(0, value))
    cmd = "sudo amixer -M sset 'fusion_hat speaker' %d%%" % value
    os.system(cmd)
