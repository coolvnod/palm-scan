# Wiring & Components Guide — source

Generates `docs/palm-scan-wiring-guide.pdf`: an illustrated, plain-language guide to every
connection and every part on the Rev 2.4 board, with an A3 fold-out wiring diagram.

| File | What |
|---|---|
| `parts.py` | SVG drawing primitives + component illustrations (adapter, sensor, screen, solenoid, connectors, …) |
| `master.py` | The A3 fold-out master wiring diagram |
| `cards.py` | Per-connection illustrations, power tree, scan timeline, part icons |
| `build.py` | Writes the HTML (CSS + prose + inline SVG) and prints it to PDF, two passes for page numbers |

```bash
python3 build.py        # → ../palm-scan-wiring-guide.pdf
```

Needs Python 3.10+, poppler-utils (`pdfinfo`, `pdftotext`) and a Chromium binary — it looks in
`~/.cache/ms-playwright/chromium-*/` by default; set `CHROME=/path/to/chrome` otherwise.
Fonts used if installed: Lato (headings, diagrams), P052 (body), Ubuntu Mono (pin names).

Pin numbers, net names and part values come from `docs/NETLIST.md`; if the schematic changes,
update the tables in `cards.py` / `build.py` and rebuild. Board component *positions* in the
fold-out are illustrative until the PCB layout exists.
