# Changelog — Monotoba LK5 Pro Marlin Firmware Fork

This file tracks **changes introduced in the Monotoba fork**, not the
entire history of upstream Marlin or the original DreadedZombie project.
See [readme-fork.md](readme-fork.md) for the reasons for the fork, observed
hardware configuration, proposed development plan, and safety notes.

Record firmware changes under **Added**, **Changed**, **Fixed**,
**Documentation**, and **Tests / Verification** as applicable. For each
hardware-relevant change, distinguish successful compilation from
on-printer testing and link to the relevant commit or pull request.

## Unreleased

### Planned — not implemented

- Investigate BLTouch/3DTouch control and trigger pin choices on the MKS
  Robin E3 V1.1 as wired in the Longer LK5 Pro.
- Preserve the existing touchscreen and filament runout sensor where
  electrically and functionally possible.
- Add pin-conflict checks, reproducible firmware build tests, safe
  installation instructions, and probe validation procedures.

These items describe intentions only; they are **not released features**.

## 2026-10-10 — Fork documentation baseline

### Documentation

- Added [readme-fork.md](readme-fork.md) explaining the fork's origin,
  motivation, known hardware observations, planned verification, license,
  and documentation maintenance policy.
- Established this changelog to separate confirmed Monotoba changes
  from future planned firmware work.

### Tests / Verification

- Confirmed the fork is available under the `Monotoba` GitHub account
  and reviewed the existing repository README and GPL-3.0 license.
- **No firmware source changes, builds, electrical tests, or
  on-printer validation were performed for this documentation baseline.**

### Compatibility / release status

- **No new firmware release.** Do not treat this changelog entry as
  confirmation of working BLTouch support.

## 2026-10-11 — Documentation, diagrams and read-only tools

### Added
- Comprehensive [BLTouch installation article](docs/BLTOUCH-LK-SERIES-GUIDE.md) for original LK4, LGT_KIT_V1.0, and MKS Robin E3 V1.1, including UART design discussion, Marlin steps, glass-bed testing and firmware recovery.
- Vector timing diagram for the BLTouch PWM command pulses and two connector-retention designs in `docs/images/`.
- Guarded [read-only firmware backup helper](tools/backup/backup_readonly.py) and usage instructions with ArduinoISP / Blue Pill options.
- Eight unit tests and a GitHub Actions workflow for the helper.

### Verification
- Automated unit test workflow passed. No programmer, printer, BLTouch or Z-homing hardware test has been performed.
- No executable Marlin firmware changes, uploads or releases in this update.
