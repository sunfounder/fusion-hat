
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
    """Update fusion-hat by running the installer script."""
    import os as _os
    from ._version import __version__

    URL = "https://raw.githubusercontent.com/sunfounder/fusion-hat/main/install.sh"

    print("")
    print(f"  Current version: {__version__}")
    print(f"  Running installer: {URL}")
    print("")

    ret = _os.system(f"curl -fsSL {URL} | sudo bash")
    if ret != 0:
        print(f"\n  [FAIL] Installer exited with code {ret}")

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
