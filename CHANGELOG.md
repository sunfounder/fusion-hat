# Changelog

All notable changes to this project are documented in this file.

This file starts at release 1.14.0 (2026-09-18). Releases up to 1.13.1 were not
tracked here; refer to the git tags (v1.7.0 ... v1.12.0) for their contents.

## [1.14.0] - 2026-09-18

### Fixed

- **PWM output frequency can now be set exactly from 1 Hz to 1 MHz.** The
  kernel driver used to write only the prescaler and keep the auto-reload
  register (ARR) fixed at 65535, so the frequency could only take the discrete
  values `72 MHz / ((PSC + 1) * 65536)`. A requested 500 Hz came out as
  549.32 Hz, and a period of 909 µs or less underflowed the unsigned prescaler
  arithmetic and was clamped to 65535, leaving the channel at 0.0168 Hz.
  The period is now decomposed into a matching PSC/ARR pair, and the prescaler
  register is written as `ratio - 1` while the divider ratio is `ratio = PSC + 1`.
- The duty-cycle compare value is derived from the current full scale
  (`ARR + 1`) instead of the hard-coded 65535, and is saturated at 100%
  instead of wrapping, so a frequency change no longer distorts the pulse
  width. Both the pulse width and the period are handled with 64-bit
  intermediate values.
- `enable` re-applies the period last written to the channel instead of
  forcing ARR = 65535 and PSC = 22 (which produced 47.77 Hz and silently
  overrode the user's frequency).
- Writing the period of one channel refreshes the compare value of every
  enabled channel in the same timer group, because PWM0-3, PWM4-7 and PWM8-11
  each share a single PSC/ARR pair. Disabled channels are left untouched.
- Invalid `period` values (0, or greater than 1000000 µs) are clamped to the
  valid range with a rate-limited warning instead of dividing by zero, and the
  clamped value is what the attribute reads back.

### Changed

- `fusion_hat.pwm.PWM(channel, freq)` now applies its `freq` argument; it was
  accepted but ignored before, so the driver kept its stored period. The
  default remains 50 Hz and `freq=None` leaves the period untouched.
- `read_period`, `write_period`, `read_duty_cycle`, `write_duty_cycle`,
  `duty_cycle` and `pulse_width` docstrings now state the real unit
  (microseconds, not milliseconds). `freq()` reports the frequency of the
  integer microsecond period that was actually written.
- Library version 1.13.1 -> 1.14.0, kernel driver version 1.0.2 -> 1.1.0.

### Documentation

- Corrected the stale default PWM prescaler/period values in
  `docs/source/hardware/onboard_mcu.rst` and documented how the driver solves
  PSC and ARR together, the microsecond period unit and the 1 Hz - 1 MHz range.
