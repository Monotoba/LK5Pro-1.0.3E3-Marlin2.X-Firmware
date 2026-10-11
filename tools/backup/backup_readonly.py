#!/usr/bin/env python3
"""Read-only firmware backup helper for documented LK-series motherboards.

This program NEVER sends firmware write/erase/unprotect commands. It can only
request memory reads through STM32CubeProgrammer or AVRDUDE. Device IDs and
target power must be confirmed by the human operator before execution.

Python 3.10+; standard library only. Use --help.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

BOARDS = {
    "robin-e3-v1.1": {
        "mcu": "STM32F103RCT6",
        "tool": "STM32_Programmer_CLI",
        "start": "0x08000000",
        "size": 0x40000,
    },
    "original-lk4-f103ve": {
        "mcu": "STM32F103VET6",
        "tool": "STM32_Programmer_CLI",
        "start": "0x08000000",
        "size": 0x80000,
    },
    "lgt-kit-v1.0-arduinoisp": {
        "mcu": "ATmega2560",
        "tool": "avrdude",
        "size": 0x40000,
        "eeprom_size": 4096,
        "protocol": "stk500v1",
        "baud": 19200,
        "coverage": "External AVR ISP; bootloader bytes may be locked.",
    },
    "lgt-kit-v1.0-usb": {
        "mcu": "ATmega2560",
        "tool": "avrdude",
        "size": 0x40000,
        "eeprom_size": 4096,
        "protocol": "wiring",
        "baud": 115200,
        "coverage": "USB bootloader read may be incomplete; verify its capabilities.",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def commands(args: argparse.Namespace, cfg: dict, output: Path) -> list[list[str]]:
    result = []
    for run in (1, 2):
        flash = output / f"flash-{run}.bin"
        if "start" in cfg:
            result.append([
                args.tool or cfg["tool"],
                "-c", "port=SWD",
                "--upload", cfg["start"], hex(cfg["size"]), str(flash),
            ])
        else:
            eeprom = output / f"eeprom-{run}.bin"
            result.append([
                args.tool or cfg["tool"],
                "-p", "m2560",
                "-c", cfg["protocol"],
                "-P", args.port,
                "-b", str(args.baud or cfg["baud"]),
                "-n",
                "-U", f"flash:r:{flash}:r",
                "-U", f"eeprom:r:{eeprom}:r",
            ])
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", choices=BOARDS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--port", help="AVR programmer serial port, e.g. /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, help="Override AVR programmer baud rate")
    parser.add_argument("--tool", help="Override tool executable path")
    parser.add_argument("--execute", action="store_true",
                        help="Run read commands (default is dry run)")
    parser.add_argument("--confirm-mcu",
                        help="Exact printed MCU part number; REQUIRED with --execute")
    args = parser.parse_args(argv)
    cfg = BOARDS[args.board]
    if "protocol" in cfg and not args.port:
        parser.error("--port is required for AVR methods")
    if args.execute and args.confirm_mcu != cfg["mcu"]:
        parser.error("--execute requires --confirm-mcu " + cfg["mcu"])
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cfg = BOARDS[args.board]
    output = args.output.expanduser().resolve()
    steps = commands(args, cfg, output)
    print("Board:", args.board, "Expected MCU:", cfg["mcu"])
    print("WARNING: Check physical MCU, readout/lock protection, SWD/ISP pinout and power.")
    if "coverage" in cfg:
        print("NOTE:", cfg["coverage"])
    for command in steps:
        print("Read command:", " ".join(command))
    if not args.execute:
        print("DRY RUN: no program executed and no files created.")
        return 0

    # Never overwrite backups, including if the process was partially run.
    if output.exists():
        print("ERROR: Output directory already exists; choose a new one.", file=sys.stderr)
        return 2
    executable = args.tool or cfg["tool"]
    if not shutil.which(executable):
        print(f"ERROR: {executable} not found; install it first.", file=sys.stderr)
        return 2
    output.mkdir(parents=True)
    try:
        for command in steps:
            subprocess.run(command, check=True)
        expected_sizes = {"flash": cfg["size"]}
        if "eeprom_size" in cfg:
            expected_sizes["eeprom"] = cfg["eeprom_size"]
        checksums: dict[str, str] = {}
        for kind, expected in expected_sizes.items():
            first = output / f"{kind}-1.bin"
            second = output / f"{kind}-2.bin"
            for path in (first, second):
                actual = path.stat().st_size
                if actual != expected:
                    raise ValueError(
                        f"{path.name}: {actual} bytes, expected {expected}; "
                        "readback not accepted"
                    )
            if sha256(first) != sha256(second):
                raise ValueError(f"{kind}: repeated reads differ")
            checksums[kind] = sha256(first)
        manifest = {
            "date_utc": datetime.now(timezone.utc).isoformat(),
            "board": args.board,
            "reported_expected_mcu": cfg["mcu"],
            "interface": "SWD" if "start" in cfg else cfg["protocol"],
            "read_only": True,
            "verified_two_reads_same_bytes": True,
            "sha256": checksums,
            "caveat": "A consistent read does not prove bootloader, external EEPROM, "
                      "option bytes, display resources, or protected regions were obtained.",
        }
        (output / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print("Readback complete; checksums match. Save a second offline copy.")
        return 0
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        print("BACKUP NOT VERIFIED:", exc, file=sys.stderr)
        print("Retain the partial files for diagnosis. Do not flash them.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
