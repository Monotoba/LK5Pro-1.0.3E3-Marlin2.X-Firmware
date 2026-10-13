# Installing 3D Touch / BLTouch on Longer LK5 Pro (Robin E3 V1.1)

Field notes from a successful October 2026 installation. **Use only on the verified MKS Robin E3 V1.1 / STM32F103RCT6 / Longer DWIN serial-screen variant.** Older LK5 Pro controller generations are different. Proceed at your own risk, retain a known-working image, and never leave a new probe installation unattended.

## Hardware and wiring

| Signal | Tested connection |
| --- | --- |
| Servo / deploy control | PB1 via J12 (3-wire 3D Touch connector) |
| Probe trigger | PC6 / Z-MIN via J11 (2-wire connector) |
| Old mechanical Z-min switch | Disconnected in this tested installation |

Check signal names and actual connector orientation against **your PCB silkscreen**. A probe's wire colors alone do not establish its pinout. Power down and unplug before changing connections. Test probe self-test before homing.

## Build

Clone this repository. Set up PlatformIO and build:

```bash
python3 -m venv .venv
.venv/bin/pip install platformio
.venv/bin/pio run -e mks_robin_e3_maple
```

This fork enables `WITH_Z_PROBE`, `NOZZLE_TO_PROBE_OFFSET { -45, -20, 0 }` and `PROBING_MARGIN 30` in `Marlin/Configuration.h`. X and Y are **measurements from one bracket**, not universal dimensions. The Z value **must be calibrated on each printer**. Check that the probe reaches below the nozzle before any Z homing.

The linker script, vector relocation and STM32 upload configuration should remain at `0x08005000`. The built raw application is:

```
.pio/build/mks_robin_e3_maple/firmware.bin
```

The build also produces `Robin_e3.bin` using an MKS XOR transformation. **On the tested bootloader only the raw, unencrypted `firmware.bin` was demonstrated to boot.** The transformed file successfully programmed but left the touchscreen at the splash screen. Do not assume this applies to all MKS bootloaders.

## SD installation and recovery

1. Back up settings (`M503`) and preserve your current *known bootable* firmware before proceeding.
2. Format microSD FAT32. Copy the **raw** `firmware.bin` to the SD root, exactly lowercase.
3. With printer off, insert the card; power on. Wait for firmware update completion.
4. Power off, remove the card, then power on; confirm normal DWIN menu and `M115` output over serial (115200, 8N1).
5. If firmware starts with `EEPROM datasize error`, after saving your old calibration settings, run `M502`, `M500`, `M503`. Reapply appropriate machine-specific calibration.

The repository contains `FDM-LK5PRO-FW-1.0.3E3-BL-230905.zip`, whose `firmware.bin` is a raw, `0x08005000`-linked reference. Verify board compatibility before using it. The older LK5 Pro `0.4.0` HEX firmware is **not** compatible with this STM32 variant.

## Safety test: no bed movement yet

Power the probe and ensure no rapid flashing alarm. With the head clear above the bed:

```gcode
M280 P0 S10   ; deploy
M119          ; z_min should read open while untouched
M280 P0 S90   ; stow
```

Deploy again and gently trigger the pin; `M119` should read `z_min: TRIGGERED`. Since this can be transient, avoid forcing the retracting pin. For flashing alarm, `M280 P0 S160` can reset BLTouch alarm; verify behavior afterward. Do not home Z if input polarity or probe behavior is uncertain.

## Safe homing and Z offset

Once the nozzle and probe have adequate clearance, home X/Y (`G28 X Y`), then supervise `G28 Z`. The probe should touch the bed, stop Z descent, repeat probing if configured, and lift the toolhead. If the nozzle continues into the bed, cut power immediately.

Set your **measured** nozzle-to-probe X/Y offsets with `M851`, then calibrate Z using a sheet of paper and very small movements. Account for Marlin Z soft-endstop limits; never repeatedly force movement against Z=0. If you temporarily use `M211 S0` for below-zero calibration, restore `M211 S1` immediately afterward. Verify `M211` is ON and store settings with `M500`.

On the tested machine only: `M851 X-45 Y-20 Z-2.22` was the tuned value. Your machine's value will differ.

## Mesh leveling and Cura

After a successful `G28`, issue `G29` with the bed clear. The tested firmware probed a 6×6, 36-point bilinear grid. Save with `M500`, enable with `M420 S1`, and confirm with `M420 V`. The measured variation on the tested bed was 0.370 mm.

In Cura, open **Settings → Printer → Manage Printers → Machine Settings**, then insert immediately after `G28` in **Start G-code**:

```gcode
G28           ; home all axes
M420 S1 Z4    ; load/enable saved mesh with 4 mm fade
```

Keep your printer's other existing start commands and ensure heating and priming sequence remains correct. Inspect the generated sliced G-code. Five 0.2-mm-thick first-layer squares across the bed verified adhesion and bonded extrusion on the tested machine. Fine-tune rather than copying its Z offset.

## Common errors

- **Update 100% but stuck on LONGER splash:** file-format mismatch or bootloader/address incompatibility; on the tested bootloader this occurred using encoded `Robin_e3.bin`. A successful *write* does not guarantee a bootable application.
- **`Home XYZ First` on `G29`:** complete `G28` in the same powered session before starting probing.
- **`z_min: TRIGGERED` while probe is idle:** deploy before evaluating state; check alarm status and signal polarity.
- **`EEPROM datasize error`:** EEPROM layout changed; retain old `M503` backup before `M502`/`M500`.
- **Mesh not active after homing:** put `M420 S1 Z4` *after* `G28` in slicer Start G-code.

## Resources

- [This fork](https://github.com/Monotoba/LK5Pro-1.0.3E3-Marlin2.X-Firmware)
- [Original DreadedZombie repository](https://github.com/DreadedZombie/LK5Pro-1.0.3E3-Marlin2.X-Firmware)
- [BLTouch connector placement illustration](https://github.com/DreadedZombie/LK5Pro-1.0.3E3-Marlin2.X-Firmware/blob/main/LK5%20Pro%20BLtouch%20Pin%20Locations.png)
- [Marlin G-code reference](https://marlinfw.org/meta/gcode/)
- [PlatformIO documentation](https://docs.platformio.org/)
