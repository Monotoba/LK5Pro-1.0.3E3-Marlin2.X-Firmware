# About the Monotoba Fork

> **Status: documentation baseline; no Monotoba firmware modifications have been validated.**
> This repository is **not** a tested, ready-to-flash BLTouch build. Do not flash it
> solely on the basis of the proposed wiring or pin assignments below.

## Origin and purpose

This repository was forked on 2026-10-10 from
[DreadedZombie/LK5Pro-1.0.3E3-Marlin2.X-Firmware](https://github.com/DreadedZombie/LK5Pro-1.0.3E3-Marlin2.X-Firmware)
to maintain and test changes for a **Longer LK5 Pro** equipped with a
**Makerbase MKS Robin E3 V1.1** controller, a **DWIN touchscreen**, and a
**filament-runout sensor**.

The immediate goal is to add support for a BLTouch-compatible/3DTouch-style
automatic bed-leveling probe **without unnecessarily sacrificing either the
factory touchscreen or the filament-runout sensor**. We also want an auditable,
reproducible build, documented wiring, and conservative verification before
any firmware is installed on a printer.

This fork exists because the LK5 Pro's use of the Robin E3 V1.1 connectors is
not necessarily the same as the board's generic Makerbase pinout. Applying a
generic BLTouch wiring guide risks disconnecting the screen or assigning a
probe signal to a pin already in use.

## Hardware observations motivating the fork

These observations describe **one owner's LK5 Pro** and are not a guarantee
for every LK5 Pro or every Robin board revision:

| Board function / connector | Observed use or state |
| --- | --- |
| NeoPixel-designated header | Connected to factory display wiring |
| BLTouch-designated control header | Connected to display wiring; cable marked `BLT` |
| Filament detection / `MTDET` | Occupied by filament-runout wiring |
| Dedicated BLTouch/probe-endstop header | Unoccupied when inspected |
| Additional candidate GPIO / `ESTOP` | **Not yet electrically or physically verified for probe use** |

An unbranded BLTouch-compatible probe and a split 3+2-wire cable are being
investigated. **Wire colors, connector order, power polarity, output voltage,
and probe behavior must be checked on the actual equipment before power is
applied.** No wiring diagram in this document should be treated as final.

## Work planned (not yet implemented)

1. **Audit pin definitions** across Marlin configuration and Robin E3 V1.1
   board header files; trace the selected board variant and all conditional
   definitions.
2. **Resolve shared-pin conflicts** among display communication, filament
   detection, probe control (servo/PWM), and probe trigger input. Consider
   alternative GPIO only after confirming connector pinout and electrical
   suitability against the appropriate hardware schematic.
3. **Implement a minimal, reversible firmware change** enabling the probe
   while retaining existing printer functionality wherever possible.
4. **Establish reproducible PlatformIO builds**, regression checks, and
   explicit checks against duplicate or conflicting pin assignments.
5. **Document verified hardware installation**: probe type, measured pinout,
   electrical test results, mounting, X/Y and Z offsets, safe-homing behavior,
   and probing reach.
6. **Validate on the printer in stages**: display and filament sensor;
   probe self-test and deployment; trigger state reporting; safe Z homing;
   bed mesh; and printing only after all preceding checks pass.

Any pin names, connector choices, and firmware settings discussed before
these tests are **hypotheses**, not confirmed instructions.

## Change tracking

- **[CHANGELOG.md](CHANGELOG.md)** is the chronological record of completed,
  committed changes, with dates and test/verification status.
- **This file** explains the fork's rationale, important hardware-specific
  design decisions, known limitations, compatibility, and departures from
  upstream. Update it whenever those facts change.
- Keep **planned**, **implemented**, **build-verified**, and
  **printer-verified** work clearly distinguished.
- Where possible, link changes to commits or pull requests and document
  relevant test commands/results. Firmware changes should include regression
  coverage and a descriptive commit message.
- Track upstream changes separately from modifications introduced by Monotoba.

## Build and installation caution

The upstream README documents a PlatformIO environment named
`mks_robin_e3_maple`:

```sh
pio run -e mks_robin_e3_maple
```

This command is an **upstream-documented build invocation**, not a statement
that the Monotoba fork currently builds or is safe to install. A successful
compile does not establish electrical safety or correct endstop operation.
Never initiate Z homing until the deployed probe and trigger state have been
verified with the toolhead safely above the bed.

## Upstream credit and licensing

The fork retains the upstream Git history and acknowledges
[DreadedZombie](https://github.com/DreadedZombie), the
[Marlin project](https://github.com/MarlinFirmware/Marlin), and other
contributors credited in the original [README.md](README.md).

The inherited Marlin firmware is licensed under the
**GNU General Public License version 3**; see [LICENSE](LICENSE).
Do not replace that license with an incompatible license when modifying
or redistributing derivative firmware. Changes made in this fork will be
documented and attributed separately from upstream contributions.

## Current fork-specific change summary

- **2026-10-10:** Fork created under `Monotoba` and this documentation
  established. **Documentation only; no probe-related source changes,
  validated builds, electrical tests, or printer tests have been completed
  as part of this fork's initial documentation work.**

For subsequent changes, consult [CHANGELOG.md](CHANGELOG.md).

## Documentation and read-only backup tooling added 2026-10-11

The [complete LK-series BLTouch installation article](docs/BLTOUCH-LK-SERIES-GUIDE.md) now documents the three researched motherboard families, a PWM timing illustration, connector depinning, alternative UART choices, beginning-to-end Marlin enablement, glass-bed testing, and recovery procedures. The [backup helper](tools/backup/README.md) supports guarded, repeat-verified **read-only** STM32CubeProgrammer/AVRDUDE operations, including ArduinoISP guidance and external Blue Pill debugger references. Eight hardware-free unit tests are included and run through GitHub Actions. **No printer firmware changes or real-hardware validation have occurred in this documentation/tooling work.**
