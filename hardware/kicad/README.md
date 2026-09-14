# kicad/ — palm-scan Rev 2 schematic

| File | What |
|---|---|
| `palm-scan.kicad_pro` / `.kicad_sch` | Root sheet. Open with `kicad palm-scan.kicad_pro` |
| `power_in`, `power_reg`, `mcu`, `reset_boot`, `usb`, `lock`, `display`, `exit`, `buzzer` `.kicad_sch` | Sub-sheets (pages 2–10), A4 |
| `palmscan.kicad_sym` + `sym-lib-table` | Project symbol library: stock KiCad symbols scaled 1.5× for readability. Footprints are unchanged. |
| `palm-scan.pdf` | Rendered schematic, 10 pages |
| `palm-scan.net` | KiCad's exported netlist |
| `erc.txt` | Last ERC report (0 errors, 0 warnings) |
| `gen_schematic.py` | Generator. The `PARTS` list is the netlist. |
| `check_netlist.py` | Diffs `palm-scan.net` against `../../docs/NETLIST.md` |

## Regenerate after a change

```
python3 gen_schematic.py
kicad-cli sch erc --output erc.txt palm-scan.kicad_sch
kicad-cli sch export netlist --format kicadsexpr --output palm-scan.net palm-scan.kicad_sch
python3 check_netlist.py
kicad-cli sch export pdf --output palm-scan.pdf palm-scan.kicad_sch
```

Nets are **global labels** — the same name on any page is the same wire.
Pages are defined in `PAGES`; a box that does not fit its page fails loudly.

Edit `PARTS` in the generator *and* the table in `../../docs/NETLIST.md` — the checker
exists precisely so the two can't drift apart silently.

## If you edit in the KiCad GUI instead

Fine — but then stop running the generator, it will overwrite your edits.
Move the wires around, keep the net names.

## One-sheet wiring diagram

`palm-scan-wiring.pdf` / `.svg` — every connection drawn as a wire, ESP32 in the middle.
Generated from `palm-scan.net` by `make_wiring_diagram.py` (needs `netlistsvg` from npm and
`cairosvg` from pip; `wiring_skin.svg` is the box/tag style). Not editable in KiCad — it is a
*picture* of the netlist and can never disagree with the schematic. Regenerate after any change:

```
kicad-cli sch export netlist --format kicadsexpr --output palm-scan.net palm-scan.kicad_sch
python3 make_wiring_diagram.py /path/to/node_modules/.bin/netlistsvg
```
