# Proposed release: LK5 Pro Robin E3 V1.1 — 3D Touch field-test

**Status: DRAFT — DO NOT PUBLISH WITHOUT THE EXACT TESTED BINARY.**

## Summary
- Enables 3D Touch / BLTouch support for the Longer LK5 Pro **MKS Robin E3 V1.1 (STM32F103RCT6)** configuration.
- Sets tested mounting bracket X/Y offsets to -45/-20 mm. Every printer requires its own Z offset calibration; no default -2.22 mm should be imposed.
- Reduces probing margin to 30 mm, retains 6×6 bilinear mesh.
- Documents startup, probe trigger checks, safe Z homing, paper Z offset, EEPROM settings, and Cura `M420 S1 Z4`.
- Corrects flashing documentation: for the **tested LK5 Pro bootloader**, use raw `.pio/build/mks_robin_e3_maple/firmware.bin`, **not** XOR-transformed `Robin_e3.bin`.

## Tested behavior
- DWIN touchscreen and serial response after flashing the raw image
- `M280` deploy and retract; `M119` Z_MIN open/triggered
- Two-pass Z homing and 36-point `G29` mesh
- 0.370 mm measured bed variation, mesh save and activation
- Five-square single-layer adhesion test (tested EEPROM Z offset -2.22 mm)

## Important limitations
- **MKS Robin E3 V1.1 only.** Not for Robin Nano V3.5 or AVR-based LK5 Pro.
- Different mounting brackets need different nozzle-to-probe X/Y offsets. Z offset is always machine-specific.
- `firmware.bin` must be from the tested or independently validated build. The upstream repository's precompiled `1.0.3E3` ZIP is a reference and must **not** be relabeled as the custom release.
- Preserve a compatible recovery image and `M503` settings before flashing.
- Other MKS bootloaders may expect the transformed image; this field result is not universally applicable.
- This repository revision has not yet been independently rebuilt/tested from GitHub's branch after the documentation/config commits.

## Release checklist
- [ ] Obtain exact **working** raw `firmware.bin` from the user's Ubuntu build
- [ ] SHA-256 verify that file and record it here
- [ ] Confirm binary vector table offset `0x08005000`
- [ ] Confirm current repository configuration reproduces it
- [ ] Publish GitHub release including the verified `firmware.bin`, README link, installation guide and provenance
