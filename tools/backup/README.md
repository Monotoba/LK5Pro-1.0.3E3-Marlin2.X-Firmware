# Read-only firmware backup helpers

This directory contains original, standard-library Python code to help owners
read and verify *existing* LK-series controller firmware. The tools **do not
erase, write, unprotect, modify option bytes, or restore firmware**.

The helper requires Python 3.10+ and an installed external programmer client
(STM32CubeProgrammer's STM32_Programmer_CLI or AVRDUDE). It is a wrapper around
the vendors' own read commands, not a hardware debugger itself.

For the complete beginner installation article, see
[BLTouch / 3DTouch on Longer LK-series](../../docs/BLTOUCH-LK-SERIES-GUIDE.md).

## First: inspect the hardware

Record the printer/PCB revision, MCU marking, and target voltage. Confirm
SWD or AVR ISP connections against the **exact board** schematic. Never
attach a 5 V Arduino output to a 3.3 V STM32 SWD input.

If the STM32 reports readout protection, do **not** clear protection merely
to try to extract firmware: STM32F1 RDP Level 1 removal erases flash.

## Dry run first — no files, no programmer access

For an MKS Robin E3 V1.1 **with verified STM32F103RCT6**:

~~~sh
python3 tools/backup/backup_readonly.py \
  --board robin-e3-v1.1 \
  --output backups/robin-original
~~~

Review the printed read commands and pin/power warnings.

Only after confirming the part and attaching a suitable ST-LINK:

~~~sh
python3 tools/backup/backup_readonly.py \
  --board robin-e3-v1.1 \
  --output backups/robin-original \
  --execute --confirm-mcu STM32F103RCT6
~~~

For an **actual verified STM32F103VET6 original LK4**:

~~~sh
python3 tools/backup/backup_readonly.py \
  --board original-lk4-f103ve \
  --output backups/lk4-original \
  --execute --confirm-mcu STM32F103VET6
~~~

Do not assume every LK4 has the listed chip. The helper refuses to
execute with a different expected MCU name.

For an LGT_KIT_V1.0 ATmega2560 using a **classic Arduino Uno/Nano loaded with
ArduinoISP**, and serial port /dev/ttyUSB0:

~~~sh
python3 tools/backup/backup_readonly.py \
  --board lgt-kit-v1.0-arduinoisp --port /dev/ttyUSB0 \
  --output backups/lgt-original \
  --execute --confirm-mcu ATmega2560
~~~

This uses AVRDUDE stk500v1 at 19200 baud. The Uno/Nano must have the
Arduino IDE's built-in **File → Examples → 11.ArduinoISP → ArduinoISP** sketch
uploaded **before** wiring to the ATmega2560 target. Target ISP signals:
RESET, MOSI, MISO, SCK, GND, correct voltage/reference. Arduino D10 is target
RESET, D11 MOSI, D12 MISO, D13 SCK. Do not press **Burn Bootloader** during
backup.

A possible serial bootloader read can instead be attempted with
--board lgt-kit-v1.0-usb --port /dev/ttyUSB0, but the bootloader may not
support a complete flash or EEPROM read. It is **not** automatically a
full-chip recovery image.

The helper refuses to overwrite any existing output directory. It makes two
read passes and verifies the length and SHA-256 checksums of both before
creating manifest.json. A validated hash does **not** prove the bootloader,
external EEPROM, option bytes, or touchscreen assets were accessible.

Do not commit extracted firmware binaries, passwords, serial numbers, or
personal printer data into a public Git repository without reviewing their
contents and distribution rights. Backup files belong offline.

## Can an STM32 Blue Pill replace ST-LINK?

A standard Uno/Nano ArduinoISP sketch is **AVR ISP only**, not STM32 SWD.
A separate Blue Pill can be flashed with suitable [Black Magic Debug](https://black-magic.org/docs/intro/hardware/)
firmware to act as an SWD probe. It can then use arm-none-eabi-gdb's
**dump binary memory** to back up *unprotected* STM32 internal flash.
Examples and board-dependent setup are linked in the article.

Third-party ST, AVRDUDE, Arduino and Black Magic tools are **not rehosted**
here; follow their official downloads, source code, and license terms.
Only the original backup helper and tests in this repository are maintained
as fork-specific software.

## Run tests locally

~~~sh
python3 -m unittest discover -s tests -p test_backup_readonly.py -v
~~~

The GitHub Actions workflow **Read-only backup helper tests** runs these
tests on pull requests and matching pushes without connecting to hardware.
Hardware-specific backups still require real-world validation.

## Restoration policy

The helper deliberately has **no restore operation**. A full STM32 chip
dump and a bootloader SD-update application binary are not interchangeable.
Restoration is board-specific and potentially destructive, and should follow
the procedures and warnings in the installation article.
