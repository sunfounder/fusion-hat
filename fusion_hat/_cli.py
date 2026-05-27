
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

def test_speaker():
    print(f"Test Fusion-HAT speaker.")
    from .device import enable_speaker, disable_speaker
    from ._utils import run_command
    try:
        enable_speaker()
        run_command("speaker-test -l3 -c2 -t wav")
    finally:
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
    print("  [1/3] git pull...")
    _, out = run_command(f"cd {repo_dir} && git pull 2>&1")
    print(out)
    if "Already up to date" in out:
        print("  Already up to date.")
        return

    # Reinstall Python package
    print("  [2/3] pip install...")
    _, out = run_command(
        f"cd {repo_dir} && sudo pip install . --break-system-packages --no-deps --no-build-isolation 2>&1"
    )
    for line in out.split("\n"):
        if "Successfully installed" in line or "error:" in line.lower():
            print(f"  {line.strip()}")

    # Build and install kernel driver
    driver_dir = _os.path.join(repo_dir, "driver")
    if _os.path.isdir(driver_dir) and _os.path.isfile(_os.path.join(driver_dir, "Makefile")):
        print("  [3/3] sudo make install (driver)...")
        _, out = run_command(
            f"cd {driver_dir} && sudo make install 2>&1"
        )
        # Show key lines
        for line in out.split("\n"):
            line = line.strip()
            if line and ("Installing" in line or "completed" in line.lower() or "error" in line.lower() or "DKMS" in line):
                print(f"  {line}")
    else:
        print("  [3/3] Driver not found, skipping.")

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
    # Prompt for sudo early so password prompt appears before the banner
    import os as _os
    _os.system("sudo -v 2>/dev/null")

    if fix:
        from fusion_hat.device import doctor_fix, force_dt_overlay, update_eeprom
        import os as _os
        result = doctor_fix()
        before = result["before"]
        after = result["after"]
        fixes = result["fixes"]
        needs_reboot = result.get("reboot", False)

        print("")
        print("=" * 50)
        print("  Fusion Hat Doctor (--fix)")
        print("=" * 50)
        print("")

        _show_doctor_result(before)

        # Handle EEPROM mismatch — ask user which fix to apply
        if fixes and "user must choose fix" in fixes[-1]:
            fixes.pop()
            print("  --- Choose fix ---")
            print("")
            print("  [1] Reflash EEPROM (only Fusion HAT installed)")
            print("  [2] Force device-tree overlay (multiple HATs conflict)")
            print("")
            try:
                choice = input("  Select (1 or 2): ").strip()
                if choice == "1":
                    print("")
                    update_eeprom(erase=True)
                    fixes.append("reflash EEPROM (erase + flash)")
                    needs_reboot = True
                elif choice == "2":
                    print("")
                    force_dt_overlay()  # prompts for reboot itself
                    fixes.append("force dtoverlay to bypass EEPROM")
                    needs_reboot = False
                else:
                    fixes.append("no action selected")
            except (KeyboardInterrupt, EOFError):
                print("")
                fixes.append("cancelled")
            print("")

        if fixes:
            print("  --- Fixes ---")
            for action in fixes:
                print(f"  → {action}")
            print("")

        if needs_reboot:
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

        print("=" * 50)
        print("")
    else:
        from fusion_hat.device import doctor
        print("")
        print("=" * 50)
        print("  Fusion Hat Driver Status")
        print("=" * 50)
        print("")
        result = doctor()
        _show_doctor_result(result)

        if not result["overall"]:
            eeprom_detail = result.get("eeprom_detail") or {}
            eeprom_timed_out = eeprom_detail.get("timed_out", False)
            eeprom_valid = result.get("eeprom_valid", False)
            eeprom_present = result.get("eeprom_present", False)
            eeprom_blank = eeprom_detail.get("data_is_blank", False)
            dtoverlay = result.get("dtoverlay", False)

            B = "\033[1m"
            Y = "\033[33m"
            C = "\033[36m"
            R = "\033[0m"

            if not result["detected"]:
                print("")
                if eeprom_timed_out:
                    print(f"  {B}══════════════════════════════════════════════{R}")
                    print(f"  {B}EEPROM scan timed out — possible I2C conflict{R}")
                    print(f"  {B}══════════════════════════════════════════════{R}")
                    print("")
                    print("  If you have multiple HATs installed, their EEPROM")
                    print("  addresses may clash. Force the device-tree overlay")
                    print("  to bypass EEPROM detection:")
                    print("")
                    print(f"      {C}fusion_hat force_dt_overlay{R}")
                    print("")
                elif not eeprom_present:
                    print(f"  {Y}[!]{R} EEPROM chip not found on I2C bus.")
                    print("      Check the HAT is properly seated on the GPIO header.")
                    if not dtoverlay:
                        print(f"      Or bypass: {C}fusion_hat force_dt_overlay{R}")
                    print("")
                elif eeprom_blank:
                    print(f"  {B}══════════════════════════════════════════════{R}")
                    print(f"  {B}EEPROM is blank — never programmed{R}")
                    print(f"  {B}══════════════════════════════════════════════{R}")
                    print("")
                    print("  The EEPROM chip is empty (all 0xFF).")
                    print("")
                    print(f"        {C}fusion_hat doctor --fix{R}")
                    print("")
                elif not eeprom_valid:
                    print(f"  {B}══════════════════════════════════════════════{R}")
                    print(f"  {B}EEPROM data mismatch — not Fusion HAT data{R}")
                    print(f"  {B}══════════════════════════════════════════════{R}")
                    print("")
                    print(f"  If you have {B}ONLY{R} Fusion HAT installed:")
                    print("    -> The EEPROM data may be corrupted. Reflash it:")
                    print("")
                    print(f"        {C}fusion_hat update_eeprom --erase{R}")
                    print("")
                    print(f"  If you have {B}MULTIPLE{R} HATs installed:")
                    print("    -> Their EEPROM I2C addresses likely conflict.")
                    print("       Force the overlay to bypass EEPROM:")
                    print("")
                    print(f"        {C}fusion_hat force_dt_overlay{R}")
                    print("")
                elif not dtoverlay:
                    print(f"  {B}══════════════════════════════════════════════{R}")
                    print(f"  {B}EEPROM data is correct — reboot to apply{R}")
                    print(f"  {B}══════════════════════════════════════════════{R}")
                    print("")
                    print("  The EEPROM has valid Fusion HAT data. The Pi needs")
                    print("  a reboot to read it and create the device-tree entry.")
                    print("")
                    print(f"        {C}sudo reboot{R}")
                    print("")
                else:
                    print("  EEPROM OK, dtoverlay configured.")
                    if not result["module_loaded"]:
                        print(f"  -> Run: {C}sudo modprobe fusion_hat{R}")
                    if not result["sysfs"]:
                        print(f"  -> Run: {C}sudo reboot{R}")
                    print("")
            else:
                print("  Some checks failed.")
                if not result["module_file"]:
                    print("  -> Run: cd driver && sudo make install")
                if not result["module_loaded"]:
                    print(f"  -> Run: {C}sudo modprobe fusion_hat{R}")
                if not result["sysfs"]:
                    print("  -> Driver may not be loaded or compatible with this kernel.")
                if not result["i2c_0x17"]:
                    print("  -> Onboard MCU not detected on I2C bus. Check: i2cdetect -y 1")

            # Show dmesg if HAT-related messages found
            dmesg_hat = result.get("dmesg_hat", "")
            if dmesg_hat:
                print("")
                print("  dmesg (HAT/EEPROM/I2C):")
                for line in dmesg_hat.strip().split("\n"):
                    print(f"    {line}")


        print("")
        print("=" * 50)
        print("")


def _show_detail_steps(steps, indent="      "):
    """Print diagnostic steps — shows all steps with pass/fail icons."""
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"

    for s in steps:
        ok = s["ok"]
        icon = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
        print(f"{indent}{icon} {s['step']}")
        detail = s.get("detail", "")
        if detail:
            for line in detail.split("\n"):
                print(f"{indent}   {line}")


def _show_doctor_result(result):
    """Render a single doctor result dict to stdout."""
    from fusion_hat.device import DTOVERLAY_NAME, EEPROM_SCAN_TIMEOUT
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"

    def _icon(ok):
        return f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"

    # ── Quick health summary ──
    print(f"  {_icon(result['sysfs'])} sysfs interface (/sys/class/fusion_hat)")
    print(f"  {_icon(result['module_loaded'])} Module loaded")
    print(f"  {_icon(result['i2c_0x17'])} I2C MCU (0x17)")

    if result["overall"]:
        print("")
        return

    # ── Deep diagnostic (driver not working) ──
    print("")
    print("  --- Deep diagnostic ---")

    # Device-tree detection
    hat_detail = result.get("hat_detail") or {}
    print(f"  {_icon(result['detected'])} HAT detected (device-tree)")
    if not result["detected"] and hat_detail.get("steps"):
        print("      HAT device-tree check:")
        _show_detail_steps(hat_detail["steps"])

    # EEPROM direct check
    eeprom_detail = result.get("eeprom_detail")
    if eeprom_detail:
        if eeprom_detail.get("timed_out"):
            print(f"      Direct EEPROM check: timed out (I2C bus conflict?)")
        else:
            eeprom_steps = eeprom_detail.get("steps", [])
            print(f"      Direct EEPROM check (bus 9, GPIO 0/1, {EEPROM_SCAN_TIMEOUT}s timeout):")
            _show_detail_steps(eeprom_steps)

    dtoverlay = result.get("dtoverlay", False)
    print(f"  {_icon(dtoverlay)} dtoverlay in config.txt ({DTOVERLAY_NAME})")
    if not dtoverlay and not result["detected"]:
        print("      Run 'fusion_hat force_dt_overlay' to bypass EEPROM.")

    # Module file + DKMS
    print(f"  {_icon(result['module_file'])} Module file")
    dkms = result.get("dkms_status", "")
    if dkms and dkms != "DKMS not installed":
        if dkms == "not registered":
            print(f"  {RED}✗{RESET} DKMS: {dkms}")
        else:
            lines = dkms.strip().split("\n")
            print(f"  {GREEN}✓{RESET} DKMS: {lines[0]}")

    print("")

def print_update_eeprom(erase: bool = False, erase_only: bool = False):
    import os as _os
    _os.system("sudo -v 2>/dev/null")
    print("Update Fusion-HAT EEPROM.")
    from .device import update_eeprom
    success = update_eeprom(erase=erase, erase_only=erase_only)
    if not success:
        print("EEPROM update did not complete successfully.")
        print("Check the output above for details.")

def setup_speaker(skip_test: bool = False):
    from ._utils import run_command
    import os
    script = os.path.join(os.path.dirname(__file__), "scripts", "setup_fusion_hat_audio.sh")
    if not os.path.isfile(script):
        print(f"Script not found: {script}")
        return
    print("Setting up speaker...")
    args = "--skip-test" if skip_test else ""
    status, output = run_command(f"sudo bash {script} {args} 2>&1")
    print(output)
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


def main():
    """ fusion_hat command line interface """

    CHOICES = {
        "enable_speaker": enable_speaker,
        "disable_speaker": disable_speaker,
        "test_speaker": test_speaker,
        "version": print_version,
        "update": update,
        "scan_i2c": scan_i2c,
        "info": print_info,
        "doctor": print_doctor,
        "update_eeprom": print_update_eeprom,
        "setup_speaker": setup_speaker,
        "force_dt_overlay": print_force_dt_overlay,
        "remove_dt_overlay": print_remove_dt_overlay,
        "uninstall": print_uninstall,
    }

    parser = argparse.ArgumentParser(description='fusion_hat command line interface')
    parser.add_argument('option', choices=CHOICES.keys(), help='option')
    parser.add_argument('--fix', action='store_true', help='auto fix driver issues (doctor only)')
    parser.add_argument('--erase', action='store_true', help='erase EEPROM before flashing (update_eeprom only)')
    parser.add_argument('--erase-only', action='store_true', help='only erase EEPROM, do not flash (update_eeprom only, for testing)')
    parser.add_argument('--skip-test', action='store_true', help='skip speaker test (setup_speaker only)')

    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    args = parser.parse_args()

    if args.fix and args.option != "doctor":
        parser.error("--fix is only valid with 'doctor'")
    if args.erase and args.option != "update_eeprom":
        parser.error("--erase is only valid with 'update_eeprom'")
    if args.erase_only and args.option != "update_eeprom":
        parser.error("--erase-only is only valid with 'update_eeprom'")
    if args.erase and args.erase_only:
        parser.error("--erase and --erase-only cannot be used together")
    if args.skip_test and args.option != "setup_speaker":
        parser.error("--skip-test is only valid with 'setup_speaker'")

    if args.option == "doctor":
        CHOICES[args.option](fix=args.fix)
    elif args.option == "update_eeprom":
        CHOICES[args.option](erase=args.erase, erase_only=args.erase_only)
    elif args.option == "setup_speaker":
        CHOICES[args.option](skip_test=args.skip_test)
    else:
        CHOICES[args.option]()
