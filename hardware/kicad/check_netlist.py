#!/usr/bin/env python3
"""Cross-check KiCad's exported netlist against ../../docs/NETLIST.md (independent source)."""
import re
from pathlib import Path

net = Path("palm-scan.net").read_text()
kicad = {}
for chunk in net[net.index("(nets"):].split("\n    (net ")[1:]:
    name = re.search(r'\(name "([^"]+)"\)', chunk).group(1).lstrip("/")
    for ref, pin in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', chunk):
        kicad[(ref, pin)] = name

md = Path("../../docs/NETLIST.md").read_text()
table = md[md.index("## Component-by-component"):md.index("## How the lock circuit")]
doc = {}
for line in table.splitlines():
    if not line.startswith("| ") or line.startswith("| Ref") or line.startswith("|---"):
        continue
    ref, value, fp, pins = [c.strip() for c in line.strip("|").split("|")]
    if ref == "J2":
        continue
    seq = 1
    for item in pins.split("—")[0].split(","):
        t = item.split()
        if not t:
            continue
        pin, netname = (str(seq), t[0]) if len(t) == 1 else (t[0], t[-1])
        pin = {"K": "1", "A": "2", "+": "1", "−": "2"}.get(pin, pin)
        doc[(ref, pin)] = netname
        seq += 1

bad = 0
for key, n in sorted(doc.items()):
    k = kicad.get(key)
    if k is None:
        print(f"MISSING in KiCad: {key} (doc says {n})"); bad += 1
    elif k != n and not (n == "NC" and k.startswith("unconnected")):
        print(f"MISMATCH {key}: doc={n} kicad={k}"); bad += 1
for key, k in sorted(kicad.items()):
    if key[0] == "J2" or key[0].startswith("#") or k.startswith("unconnected"):
        continue
    if key not in doc:
        print(f"NOT IN DOC: {key} = {k}"); bad += 1
j2 = {k[1]: v for k, v in kicad.items() if k[0] == "J2"}
exp = {"A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS", "A6": "USB_D+", "B6": "USB_D+",
       "A7": "USB_D-", "B7": "USB_D-", "A5": "CC1", "B5": "CC2", "A1": "GND", "A12": "GND",
       "B1": "GND", "B12": "GND", "S1": "GND"}
for p, n in exp.items():
    if j2.get(p) != n:
        print(f"J2 MISMATCH {p}: expected {n}, kicad {j2.get(p)}"); bad += 1
print(f"checked {len(doc)} doc pins + {len(exp)} J2 pins; {bad} problems")
nets = sorted(set(v for v in kicad.values() if not v.startswith("unconnected")))
print(len(nets), "nets:", ", ".join(nets))
for p, g in (("15", "IO3"), ("26", "IO45"), ("16", "IO46")):
    print(f"U1 pin {p} ({g}, strapping) -> {kicad.get(('U1', p))}")
