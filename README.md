# LK5 Pro - Dual Blower + BLTouch - Marlin 2.0 Firmware

Custom Marlin 2.0.x firmware for the Longer LK5 Pro with MKS Robin E3 v1.1 board.

**Original project:** [DreadedZombie](https://github.com/DreadedZombie) · **Field-tested BLTouch fork:** [Monotoba](https://github.com/Monotoba)

## Hardware Compatibility

**Board:** MAKERBASE MKS Robin E3 v1.1
**Printer:** Longer LK5 Pro

**Features Currently Enabled:**
- Dual part cooling fan configuration (synchronized blowers)
- DWIN 4.3" LCD serial touchscreen
- Filament runout sensor
- PID temperature control (hotend & bed)
- SD card printing

**Optional Features (can be enabled):**
- BLTouch/3D Touch auto bed leveling (**enabled in this fork**; check probe wiring and offsets before use)
- Bilinear auto bed leveling (enabled when BLTouch is active)

**Note:** This firmware is specifically configured for the newer LK5 Pro models with the MKS Robin E3 v1.1 board. If you have an older model with MKS Robin Nano v3.5, you'll need different firmware.

## Improvements Over Stock Firmware

This custom firmware includes advanced Marlin 2.0 features not available in the stock LONGER3D firmware:

### Print Quality Enhancements
- **Linear Advance** - Compensates for extruder pressure dynamics, improves line quality at corners and direction changes (M900 K-factor tunable)
- **S-Curve Acceleration** - Applies Bézier curve acceleration for smoother motion and reduced vibrations
- **Arc Support (G2/G3)** - Native arc commands for smoother curved geometry and smaller file sizes
- **Firmware Retraction** - Consistent retraction control independent of slicer settings

### Advanced Bed Leveling
- **Bilinear Auto Bed Leveling** - 6x6 mesh grid (36 points) for precise bed surface mapping
- **Probe Temperature Compensation** - Adjusts for probe offset changes during temperature variations
- **Leveling Fade Height** - Gradually removes mesh compensation as height increases
- **Manual Corner Leveling** - Guided 4-corner bed leveling with probe verification

### Safety & Reliability
- **Power Loss Recovery** - Automatically saves print state; resume after power interruption
- **Enhanced Thermal Protection** - Multi-layer protection for hotend, bed, and motherboard
- **Endstop Interrupts** - Hardware-based endstop detection for faster collision response
- **Cold Extrusion Prevention** - Blocks extrusion below safe temperature

### User Experience
- **Babystepping** - Real-time Z-offset adjustment during printing (0.1mm resolution)
- **EEPROM Settings** - All settings persist through power cycles (M500/M501)
- **Nozzle Park Feature** - Automatic safe parking during operations
- **Recent Files First** - SD card shows recently used files at the top

### Calibration & Tuning
- **Custom PID Values** - Hardware-specific tuning for LK5 Pro (Hotend: Kp=28.44, Ki=2.41, Kd=83.88)
- **Advanced Motion Control** - Classic Jerk configured for optimal speed/quality balance
- **Filament Runout Detection** - Automatic pause with custom LCD notification (M2003)

## Build

> **IMPORTANT — verified recovery lesson (October 2026):** The original upstream PlatformIO recipe also creates an XOR-transformed `Robin_e3.bin`. On the tested LK5 Pro with Robin E3 V1.1, writing that file after renaming it to `firmware.bin` completed the SD update but left the printer at the LONGER splash screen. Flashing the **raw** `firmware.bin`, linked at `0x08005000`, successfully started Marlin and the DWIN display. Always identify the exact PCB and bootloader first. Keep a proven recovery image. The repository's `FDM-LK5PRO-FW-1.0.3E3-BL-230905.zip` includes a raw `firmware.bin` reference; it is not the tested custom build.

> **Installed probe offsets are mount-specific.** This fork enables `WITH_Z_PROBE`, uses `X=-45`, `Y=-20` mm for the tested bracket, and leaves compiled Z at `0` pending on-machine calibration. The tested printer's final saved EEPROM offset was `M851 Z-2.22`; **do not hard-code or copy that Z value to other machines**.

For the hands-on installation, troubleshooting and Cura commands see [3D Touch installation and calibration](docs/3d-touch-installation.md).


As the firmware is based on Marlin 2.0.x which is built on the core of PlatformIO, the build compiling steps are the same as Marlin 2.0.x. You can directly use [PlatformIO Shell Commands](https://docs.platformio.org/en/latest/core/installation.html#piocore-install-shell-commands), or use IDEs with built-in PlatformIO Core (CLI), for example, [VSCode](https://docs.platformio.org/en/latest/integration/ide/vscode.html#ide-vscode) and [Atom](https://docs.platformio.org/en/latest/integration/ide/atom.html). VSCode is recommended.

**Build command:**
```bash
pio run -e mks_robin_e3_maple
```

## Update Firmware

This printer has **two separate firmwares** that can be updated independently:

### 1. Main Controller Firmware (Marlin)

Updates the motherboard (MKS Robin E3 v1.1) with your custom Marlin firmware:

1. Enter the `.pio\build\mks_robin_e3_maple` directory
2. **For the field-tested Longer LK5 Pro Robin E3 V1.1 bootloader, use the existing unencrypted `.pio/build/mks_robin_e3_maple/firmware.bin` directly. Do NOT rename the XOR-encoded `Robin_e3.bin`. This is bootloader-specific; other MKS boards may require encoded images.**
3. Copy `firmware.bin` to the **root directory** of your SD card
4. Insert the SD card into the motherboard
5. Power on the printer - you should see the update interface
6. Wait for update to complete (progress bar will show)

### 2. Display Firmware (DWIN Touchscreen)

Updates the graphics, icons, fonts, and UI elements on the 4.3" DWIN LCD touchscreen:

1. Format an SD card as FAT32
2. Copy all files from the `Firmware/assets/` folder to the **root directory** of the SD card
   - This includes all `bmp_*.bin` files (UI graphics/icons)
   - And `FontUNIGBK.bin` (font file)
3. Insert the SD card into the printer
4. Power on the printer
5. The display will automatically detect and update its graphics
6. Wait for the update to complete (may take a few minutes)

**Note:** You only need to update the display firmware if you've customized the UI graphics or if you're experiencing display issues. The display firmware is in the `Firmware/assets/` folder.

---

## Credits & Attribution

This firmware is based on and builds upon the excellent work of:

### Original Sources
- **[Marlin Firmware](https://github.com/MarlinFirmware/Marlin)** - The core 3D printer firmware (v2.0.x)
  - Copyright © 2020 MarlinFirmware
  - Licensed under GPL v3.0

- **[LONGER3D Official Firmware](https://github.com/LONGER3D/Mks-Robin-Nano-Marlin2.0-Firmware)** - Base configuration for LK5 Pro
  - MKS Robin Nano Marlin 2.0 firmware by LONGER3D
  - Provided configurations and pin definitions for Longer printers

- **[chaosoflife](https://github.com/chaosoflife/LK5-Dblower-BLtouch)** - Initial customization work
  - BLTouch integration and dual blower configuration
  - Hardware documentation and pin mapping

### This Fork
This repository adds:
- Updated README with comprehensive documentation
- Advanced Marlin 2.0 features (Linear Advance, S-Curve, Power Loss Recovery)
- Display firmware customization support
- WiFi module installation guide
- Enhanced build and flash instructions
- Custom PID tuning for LK5 Pro hardware

### License
This project maintains the **GNU General Public License v3.0** from the original Marlin firmware. See [LICENSE](LICENSE) file for details.

### Contributing
Found a bug or want to contribute? Open an issue or pull request!

### Support
For questions specific to this configuration, open an issue on this repository.
For general Marlin support, visit the [Marlin Documentation](https://marlinfw.org/).


## Monotoba fork: BLTouch installation research

This fork includes a [board-specific LK4/LK5 BLTouch installation and recovery guide](docs/BLTOUCH-LK-SERIES-GUIDE.md) with PWM and connector-release figures, and [read-only firmware backup tooling](tools/backup/README.md). The proposed Robin E3 V1.1 ESTOP/PB1 and Z-STOP/PC6 installation has **not yet been printer-verified**; do not flash firmware or home Z based solely on a source-code review. See [readme-fork.md](readme-fork.md) and [CHANGELOG.md](CHANGELOG.md).
