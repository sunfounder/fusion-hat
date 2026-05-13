# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Fusion Hat is a Python library for the SunFounder Fusion HAT — a Raspberry Pi expansion board with an onboard MCU that provides PWM output, ADC input, a motor driver chip, I2S audio, a mono speaker, and exposed GPIOs. The repo also contains a Linux kernel driver (C) that exposes the HAT's hardware via sysfs.

## Commands

**Build and install the kernel driver:**
```bash
cd driver && make all && sudo make install
```

**Install the Python package locally (for development):**
```bash
sudo pip install ~/fusion-hat/ --break-system-packages --no-deps --no-build-isolation
```

**Build docs:**
```bash
cd docs
sphinx-apidoc -f -d 1 -e -M -P -T -o source/api ../fusion_hat
```

**CLI commands (available via `fusion_hat` entry point):**
```bash
fusion_hat info           # Show device info, battery, button, speaker state
fusion_hat version        # Print library version
fusion_hat scan_i2c       # Scan I2C bus for devices
fusion_hat enable_speaker|disable_speaker|test_speaker
```

There is no test suite or linter configured in this repo.

## Architecture

### Two-layer communication

The Python library talks to hardware through two paths:

1. **sysfs files** at `/sys/class/fusion_hat/fusion_hat/` — exposed by the kernel driver (`driver/`). Used by `device.py`, `pwm.py`, `battery.py`, `adc.py` for speaker, PWM channels, LED, button state, battery, firmware/driver version.
2. **I2C** via smbus2 — wrapped by `_i2c.py`. Used by many `modules/` sensors (MPU6050, ADXL345, magnetometer, etc.).

### Key files

| File | Role |
|------|------|
| `fusion_hat/_base.py` | Base class providing a `self.log` Logger to all hardware classes |
| `fusion_hat/_utils.py` | Utilities: `mapping()`, `constrain()`, `retry` decorator, `run_command()` |
| `fusion_hat/_i2c.py` | I2C bus wrapper with auto-retry on OSError (5 attempts) |
| `fusion_hat/device.py` | Device identity constants, detection (`is_detected`, `is_driver_loaded`), and the `@require_fusion_hat` decorator that gates hardware access |
| `fusion_hat/pin.py` | GPIO pin wrapper around `RPi.GPIO` with active-state abstraction and interrupt callbacks |
| `fusion_hat/pwm.py` | PWM channel control via sysfs; `Servo` extends this |
| `fusion_hat/motor.py` | DC motors — maps motor names (M0-M3) to PWM pin pairs, handles direction via two channels |
| `fusion_hat/adc.py` | ADC via IIO sysfs (`/sys/bus/iio/devices/iio:deviceN/`) |
| `fusion_hat/battery.py` | Battery/charging state via `/sys/class/power_supply/fusion-hat/` |
| `fusion_hat/user_button.py` | Physical button using `evdev` (Linux input subsystem), runs event listener in a daemon thread |
| `fusion_hat/config.py` | JSON file config with dict-like access |
| `fusion_hat/_cli.py` | CLI entry point registered as `fusion_hat` console script |
| `fusion_hat/voice_assistant.py` | Monkey-patches `sunfounder-voice-assistant` to enable speaker on init |
| `fusion_hat/stt.py`, `tts.py`, `llm.py` | Thin re-exports from `sunfounder-voice-assistant` |
| `fusion_hat/modules/` | Hardware sensor/display modules (MPU6050, ADXL345, ultrasonic, LCD1602, LED matrix, RFID, etc.) — all use `_base` and `_i2c` |

### Design patterns

- **All hardware classes inherit `_Base`** for consistent logging. Constructor accepts `log=` and `log_level=` kwargs.
- **Device readiness guard**: `raise_if_fusion_hat_not_ready()` checks both EEPROM detection and driver load. The `@require_fusion_hat` decorator applies this check transparently. Almost every hardware class calls this in `__init__`.
- **I2C retry**: The `@retry(5)` decorator on I2C methods retries on `OSError` — handles transient bus contention.
- **Deprecation pattern**: Deprecated functions print warnings and delegate to the replacement. Several exist in `device.py`, `motor.py`, `pwm.py`, `user_button.py`.

### Version management

Version is stored in `fusion_hat/_version.py` as `__version__`. `pyproject.toml` reads it dynamically via `[tool.setuptools.dynamic] version`.

## Development workflow

**Branching**: Create a new branch for each feature or fix from `main`. Use a short, descriptive branch name:
```
git checkout -b <scope>/<short-description>
```
Examples: `driver/dkms-support`, `cli/add-doctor`, `pwm/fix-init`

**Commits**: Use conventional commits. Scopes mirror the key files / module areas:
```
feat(<scope>): <imperative description>
fix(<scope>): <imperative description>
refactor(<scope>): <imperative description>
chore: <description>
```
Common scopes: `driver`, `cli`, `device`, `pwm`, `motor`, `battery`, `adc`, `pin`, `config`, `i2c`, `docs`.

**Commit message rules**:
- Keep the summary under 72 characters
- Use imperative mood ("add" not "added", "fix" not "fixed")
- No period at end of summary
- If there are multiple independent changes, make multiple focused commits — don't squash unrelated work

**Push**: After committing, push the branch and open a PR:
```
git push -u origin <branch-name>
gh pr create --title "<pr title>" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points>

## Test plan
[Checklist of what was tested]

EOF
)"
```

**Before pushing**: Verify the branch is clean (`git status`), commits are well-formed (`git log`), and changes are focused on the task. Don't push to `main` directly — always go through a branch.
