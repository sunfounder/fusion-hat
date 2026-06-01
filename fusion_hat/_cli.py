
# PYTHON_ARGCOMPLETE_OK
import argparse

def enable_speaker():
    print(f"Enable Fusion-HAT speaker.")
    from .device import enable_speaker
    enable_speaker()

def disable_speaker():
    print(f"Disable Fusion-HAT speaker.")
    from .device import disable_speaker
    disable_speaker()

def _get_pa_volume():
    """Get current PulseAudio sink volume (first percentage), or None."""
    import re as _re
    import os as _os
    try:
        raw = _os.popen("pactl get-sink-volume @DEFAULT_SINK@ 2>/dev/null").read()
        m = _re.search(r"(\d+)%", raw)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def test_speaker():
    print(f"Test Fusion-HAT speaker.")
    import os as _os
    from .device import enable_speaker, disable_speaker

    saved = _get_pa_volume()

    try:
        enable_speaker()
        if saved:
            _os.system("pactl set-sink-volume @DEFAULT_SINK@ 80% >/dev/null 2>/dev/null")
        _os.system("aplay -q /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null")
    finally:
        if saved:
            _os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {saved}% >/dev/null 2>/dev/null")
        disable_speaker()

def print_version():
    from ._version import __version__
    print(f"Fusion HAT library version: {__version__}")

def update():
    """Update fusion-hat from git and reinstall."""
    import os as _os
    from ._utils import run_command
    from ._version import __version__

    # Find the repo directory (parent of the installed package)
    repo_dir = _os.path.dirname(_os.path.dirname(__file__))
    if not _os.path.isdir(_os.path.join(repo_dir, ".git")):
        # Fallback: try standard locations
        for d in ["/home/pi/fusion-hat", _os.path.expanduser("~/fusion-hat")]:
            if _os.path.isdir(_os.path.join(d, ".git")):
                repo_dir = d
                break
        else:
            print("[FAIL] Cannot find fusion-hat git repository.")
            print("  Clone it first: git clone https://github.com/sunfounder/fusion-hat ~/fusion-hat")
            return

    print(f"  Repository: {repo_dir}")
    print(f"  Current version: {__version__}")
    print("")

    # Pull
    print("  [1/4] git pull...")
    _, out = run_command(f"cd {repo_dir} && git pull 2>&1")
    print(out)
    if "Already up to date" in out:
        print("  Already up to date.")
        return

    # Reinstall Python package
    print("  [2/4] pip install...")
    _, out = run_command(
        f"cd {repo_dir} && sudo pip install . --break-system-packages --no-deps --no-build-isolation 2>&1"
    )
    for line in out.split("\n"):
        if "Successfully installed" in line or "error:" in line.lower():
            print(f"  {line.strip()}")

    # Build and install kernel driver
    driver_dir = _os.path.join(repo_dir, "driver")
    if _os.path.isdir(driver_dir) and _os.path.isfile(_os.path.join(driver_dir, "Makefile")):
        print("  [3/4] sudo make install (driver)...")
        _, out = run_command(
            f"cd {driver_dir} && sudo make install 2>&1"
        )
        # Show key lines
        for line in out.split("\n"):
            line = line.strip()
            if line and ("Installing" in line or "completed" in line.lower() or "error" in line.lower() or "DKMS" in line):
                print(f"  {line}")
    else:
        print("  [3/4] Driver not found, skipping.")

    # Add dtoverlay to config.txt
    print("  [4/4] Configure dtoverlay in config.txt...")
    from .device import _add_dtoverlay, _has_dtoverlay
    if _has_dtoverlay():
        print("  dtoverlay already configured.")
    elif _add_dtoverlay():
        print("  Added dtoverlay=sunfounder-fusionhat to config.txt.")
        print("  Reboot to activate: sudo reboot")
    else:
        print("  [FAIL] Could not write to config.txt.")

    # Read new version from disk (current process still has old import)
    new_ver = __version__
    try:
        ver_file = _os.path.join(_os.path.dirname(__file__), "_version.py")
        with open(ver_file, "r") as f:
            content = f.read()
        import re as _re
        m = _re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", content)
        if m:
            new_ver = m.group(1)
    except Exception:
        pass

    print("")
    if new_ver != __version__:
        print(f"  Updated: {__version__} -> {new_ver}")
    else:
        print(f"  Version: {new_ver} (up to date)")
    print("  Run: fusion_hat doctor")

def scan_i2c():
    print(f"Scan I2C bus.")
    from ._i2c import I2C
    i2c = I2C()
    devices = i2c.scan()
    devices = ["0x{:02X}".format(device) for device in devices]
    print(f"Found devices: {devices}")

def print_doctor(fix: bool = False):
    import os as _os
    _os.system("sudo -v 2>/dev/null")

    if fix:
        from fusion_hat.device import doctor_fix
        result = doctor_fix()
        needs_reboot = result.get("reboot", False)

        if result["fixed"]:
            print(f"  \033[32mAll checks pass now!\033[0m\n")
        elif needs_reboot:
            print("  A reboot is needed for changes to take effect.")
            try:
                answer = input("  Reboot now? (y/N): ").strip().lower()
                if answer in ("y", "yes"):
                    print("  Rebooting...")
                    _os.system("sudo reboot 2>&1")
                else:
                    print("  Reboot later with: sudo reboot")
            except (KeyboardInterrupt, EOFError):
                print("")
                print("  Reboot later with: sudo reboot")
            print("")
    else:
        from fusion_hat.device import doctor
        doctor()

def setup_speaker(skip_test: bool = False):
    import os as _os
    script = _os.path.join(_os.path.dirname(__file__), "scripts", "setup_fusion_hat_audio.sh")
    if not _os.path.isfile(script):
        print(f"Script not found: {script}")
        return
    print("Setting up speaker...")
    args = "--skip-test" if skip_test else ""
    status = _os.system(f"sudo bash {script} {args}")
    if status is not None and status != 0:
        print(f"Setup speaker failed with exit code {status}.")
    else:
        print("Speaker setup complete.")

def print_info():
    from fusion_hat._version import __version__
    from fusion_hat.device import NAME
    from fusion_hat.device import is_driver_loaded
    from fusion_hat.device import get_speaker_state
    from fusion_hat.device import get_usr_btn
    from fusion_hat.device import get_firmware_version
    from fusion_hat.device import get_driver_version
    from fusion_hat.device import get_led
    from fusion_hat.battery import Battery

    hw_ready = is_driver_loaded()

    datas = {
        "Name": NAME,
        "Library Version": __version__,
    }

    if hw_ready:
        datas.update({
            "Firmware Version": get_firmware_version(),
            "Driver Version": get_driver_version(),
            "User Button State": "Pressed" if get_usr_btn() else "Released",
            "Speaker State": "Enabled" if get_speaker_state() else "Disabled",
            "User LED State": "On" if get_led() else "Off",
        })
        try:
            battery = Battery()
            datas.update({
                "Battery level": f"{battery.capacity}%",
                "Battery voltage": f"{battery.voltage} V",
                "Battery charging": "Yes" if battery.is_charging else "No",
            })
        except Exception:
            pass

    print("")
    print("=" * 50)
    print("  Fusion Hat Device Info")
    print("=" * 50)
    print("")
    for key, value in datas.items():
        print(f"  {key:>18}: {value}")
    print("")
    print("=" * 50)
    print("")

def print_force_dt_overlay():
    import os as _os
    _os.system("sudo -v 2>/dev/null")
    print("Force device-tree overlay for Fusion HAT...")
    from fusion_hat.device import force_dt_overlay
    force_dt_overlay()


def print_remove_dt_overlay():
    import os as _os
    _os.system("sudo -v 2>/dev/null")
    print("Remove device-tree overlay for Fusion HAT...")
    from fusion_hat.device import remove_dt_overlay
    remove_dt_overlay()


def print_uninstall():
    import os as _os
    _os.system("sudo -v 2>/dev/null")
    from fusion_hat.device import uninstall
    uninstall()


def _deprecated(old, new):
    import sys
    print(f"[WARN] '{old}' is deprecated, use '{new}' instead.", file=sys.stderr)


def main():
    """ fusion_hat command line interface """

    parser = argparse.ArgumentParser(description='fusion_hat command line interface')
    sub = parser.add_subparsers(dest='option')

    # ── speaker subcommand group ──
    speaker_parser = sub.add_parser('speaker', help='Speaker control')
    speaker_sub = speaker_parser.add_subparsers(dest='speaker_action')

    sp = speaker_sub.add_parser('enable', help='Enable speaker')
    sp.set_defaults(_func=lambda a: enable_speaker())

    sp = speaker_sub.add_parser('disable', help='Disable speaker')
    sp.set_defaults(_func=lambda a: disable_speaker())

    sp = speaker_sub.add_parser('test', help='Test speaker')
    sp.set_defaults(_func=lambda a: test_speaker())

    sp = speaker_sub.add_parser('setup', help='Run audio setup')
    sp.add_argument('--skip-test', action='store_true', help='skip speaker test')
    sp.set_defaults(_func=lambda a: setup_speaker(skip_test=a.skip_test))

    # ── deprecated speaker commands (top-level) ──
    p = sub.add_parser('enable_speaker', help='[deprecated] use "speaker enable"')
    p.set_defaults(_func=lambda a: (
        _deprecated('enable_speaker', 'speaker enable'), enable_speaker()
    ))

    p = sub.add_parser('disable_speaker', help='[deprecated] use "speaker disable"')
    p.set_defaults(_func=lambda a: (
        _deprecated('disable_speaker', 'speaker disable'), disable_speaker()
    ))

    p = sub.add_parser('test_speaker', help='[deprecated] use "speaker test"')
    p.set_defaults(_func=lambda a: (
        _deprecated('test_speaker', 'speaker test'), test_speaker()
    ))

    p = sub.add_parser('setup_speaker', help='[deprecated] use "speaker setup"')
    p.add_argument('--skip-test', action='store_true', help='skip speaker test')
    p.set_defaults(_func=lambda a: (
        _deprecated('setup_speaker', 'speaker setup'), setup_speaker(skip_test=a.skip_test)
    ))

    p = sub.add_parser('version', help='Print library version')
    p.set_defaults(_func=lambda a: print_version())

    p = sub.add_parser('update', help='Self-update from git')
    p.set_defaults(_func=lambda a: update())

    p = sub.add_parser('scan_i2c', help='Scan I2C bus')
    p.set_defaults(_func=lambda a: scan_i2c())

    p = sub.add_parser('info', help='Show device info')
    p.set_defaults(_func=lambda a: print_info())

    p = sub.add_parser('doctor', help='Run hardware health checks')
    p.add_argument('--fix', action='store_true', help='auto fix driver issues')
    p.set_defaults(_func=lambda a: print_doctor(fix=a.fix))

    p = sub.add_parser('force_dt_overlay', help='Force device-tree overlay')
    p.set_defaults(_func=lambda a: print_force_dt_overlay())

    p = sub.add_parser('remove_dt_overlay', help='Remove device-tree overlay')
    p.set_defaults(_func=lambda a: print_remove_dt_overlay())

    p = sub.add_parser('uninstall', help='Uninstall fusion-hat')
    p.set_defaults(_func=lambda a: print_uninstall())

    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    args = parser.parse_args()

    if args.option is None:
        parser.print_help()
        return

    if args.option == 'speaker' and getattr(args, 'speaker_action', None) is None:
        speaker_parser.print_help()
        return

    args._func(args)
