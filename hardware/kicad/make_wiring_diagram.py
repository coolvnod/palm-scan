#!/usr/bin/env python3
"""One-sheet wiring diagram (real drawn wires) from KiCad's exported netlist.

Reads palm-scan.net, writes wiring.json (Yosys/netlistsvg format), then runs
netlistsvg -> wiring.svg -> wiring.pdf.  Power rails (GND, +3V3, +5V, +12V,
VIN_12V, VIN_FUSED) are drawn as small rail tags at each pin, like Vbat/GND
tags on a hand-drawn schematic; everything else is a drawn wire.

    python3 make_wiring_diagram.py /path/to/node_modules/.bin/netlistsvg
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
NET = HERE / "palm-scan.net"
RAILS = {"GND", "+3V3", "+5V", "+12V"}

# Which side of a box a pin sits on.  "in" = left, "out" = right.  Chosen for
# left-to-right reading (power -> MCU -> peripherals), not electrical direction.
MCU_LEFT = {"3V3", "GND", "EN", "IO0", "USB_D-", "USB_D+", "RXD0", "TXD0", "IO7"}
LEFT_OF_MCU_REFS = {"J2", "D3", "R3", "R4", "R11", "R12", "S1", "S2", "R1", "C4", "C10", "J6"}


def side(ref: str, pin: str, func: str, net: str) -> str:
    if ref == "U1":
        return "input" if func in MCU_LEFT else "output"
    if ref in ("R3", "R4"):
        return "input" if net not in RAILS else "output"
    if ref in LEFT_OF_MCU_REFS:
        return "output" if net not in RAILS else "input"
    # power chain reads left -> right
    if ref in ("J1", "J8"):
        return "output"
    if ref == "F1":
        return "input" if pin == "1" else "output"
    if ref == "D1":
        return "input" if func == "A" else "output"
    if ref in ("U2", "U3"):
        return "input" if func in ("IN", "GND") else "output"
    # peripherals: MCU-facing signals on the left, rails on the right
    return "output" if net in RAILS else "input"


def main() -> None:
    netlistsvg = sys.argv[1] if len(sys.argv) > 1 else "netlistsvg"
    text = NET.read_text()

    values = {}
    for m in re.finditer(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', text):
        values[m.group(1)] = m.group(2)

    pins = defaultdict(list)          # ref -> [(pin, func, net)]
    for chunk in text[text.index("(nets"):].split("\n    (net ")[1:]:
        net = re.search(r'\(name "([^"]+)"\)', chunk).group(1)
        for ref, pin, rest in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)([^\n]*)', chunk):
            fn = re.search(r'pinfunction "([^"]+)"', rest)
            pins[ref].append((pin, fn.group(1) if fn else "", net))

    bit = {}
    next_bit = [2]

    def net_bit(name: str) -> int:
        if name not in bit:
            bit[name] = next_bit[0]
            next_bit[0] += 1
        return bit[name]

    cells = {}
    rail_n = 0
    for ref, plist in sorted(pins.items()):
        if ref.startswith("#"):
            continue
        dirs, conns = {}, {}
        for pin, func, net in sorted(plist, key=lambda t: (len(t[0]), t[0])):
            if net.startswith("unconnected"):
                continue
            label = f"{pin} {func}".strip() if func and func != f"Pin_{pin}" else pin
            if ref in ("J4", "CN1", "J6", "J7", "J3", "J5", "J1", "J8"):
                label = f"{pin} {net}" if net not in RAILS else f"{pin} {net}"
            s = side(ref, pin, func, net)
            dirs[label] = s
            if net in RAILS:
                # private net to a rail tag placed on the opposite side
                rail_n += 1
                b = next_bit[0]; next_bit[0] += 1
                conns[label] = [b]
                tag_port = "R" if s == "input" else "L"       # tag sits opposite the pin
                cells[f"{net}_{rail_n}"] = {
                    "type": net,
                    "port_directions": {tag_port: "output" if s == "input" else "input"},
                    "connections": {tag_port: [b]},
                }
            else:
                conns[label] = [net_bit(net)]
        cells[ref] = {
            "type": f"{ref}  {values.get(ref, '')}",
            "port_directions": dirs,
            "connections": conns,
        }

    module = {"modules": {"palm-scan": {"ports": {}, "cells": cells,
                                        "netnames": {n: {"bits": [b]} for n, b in bit.items()}}}}
    (HERE / "wiring.json").write_text(json.dumps(module, indent=1))
    subprocess.run([netlistsvg, str(HERE / "wiring.json"), "--skin", str(HERE / "wiring_skin.svg"),
                    "-o", str(HERE / "wiring.svg")], check=True)
    print(f"{len(cells)} boxes, {len(bit)} signal nets, {rail_n} rail tags -> wiring.svg")


if __name__ == "__main__":
    main()
