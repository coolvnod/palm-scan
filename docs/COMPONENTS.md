# Components — palm-scan Rev 2.4

**What we're building:** a box next to your door. You show your hand, the door opens.

This is the buying list. Wiring is in `NETLIST.md`, currents in `POWER_BUDGET.md`, the schematic in `../hardware/kicad/palm-scan.pdf`.
The old Rev 2 list (23 parts, no fuse, lock before the diode) is gone — it had a real fault, see `DESIGN_REVIEW.md`.

**Three lists:**
- **A — PCB maker assembles.** Small surface-mount parts. JLCPCB solders them for you. You never touch these.
- **B — You solder.** Through-hole parts with big legs. 10 minutes with an iron. (JLCPCB *can* do these too for extra money — see the note at the end.)
- **C — You buy, lives outside the board.** Sensor, screen, lock, adapter, case.

LCSC numbers marked ✅ are ones I'm confident of. Others say *search* — type the part name into jlcpcb.com/parts and pick the one marked "Basic" if there is one (no extra fee).

---

## A — PCB maker assembles (32 parts on the board)

| Ref | What | Value / part | Package | Qty | LCSC | Plain words |
|---|---|---|---|---|---|---|
| U1 | ESP32-S3-WROOM-1-N8R2 | Espressif module | module | 1 | *search "ESP32-S3-WROOM-1-N8R2"* | **The brain.** Wi-Fi and USB built in. |
| Q1 | MOSFET | AO3400A | SOT-23 | 1 | C20917 ✅ | **The strong arm** that switches the lock. |
| D1 | Schottky diode | SS34, 40 V 3 A | SMA | 1 | C8678 ✅ | Blocks a backwards adapter. |
| D2 | Schottky diode | SS54, 40 V 5 A | SMA | 1 | *search "SS54 SMA"* | Absorbs the lock's kick-back. **Safety.** |
| D3 | USB ESD protector | USBLC6-2SC6 | SOT-23-6 | 1 | C7519 ✅ | Takes static shocks from the USB plug. |
| D7 | TVS diode | SMAJ15A | SMA | 1 | *search "SMAJ15A"* | Swallows voltage spikes on the 12 V line (long lock cable). |
| D4 | LED, yellow | 0603 | 0603 | 1 | *search "0603 LED yellow"* | Power-on light (for you, not users). |
| F1 | Resettable fuse | Bourns MF-MSMF200/16 — 2 A hold, 16 V | 1812 | 1 | *search "MF-MSMF200/16"* — **not** MSMF110 | Self-resetting fuse. |
| R1 | Resistor | 10 kΩ | 0603 | 1 | basic | Keeps the brain awake (EN pull-up). |
| R2 | Resistor | 10 kΩ | 0603 | 1 | basic | Holds the lock OFF during boot. **Safety.** |
| R3, R4 | Resistor | 5.1 kΩ | 0603 | 2 | basic | Tells the laptop "I'm a USB device". |
| R5 | Resistor | 220 Ω | 0603 | 1 | basic | Buzzer current limit. |
| R6 | Resistor | 10 kΩ | 0603 | 1 | basic | Exit-button pull-up. |
| R7 | Resistor | 1 kΩ | 0603 | 1 | basic | Power LED current limit. |
| R8 | Resistor | 1 kΩ | 0603 | 1 | basic | Protects the exit-button pin from the wall wire. |
| R9, R10 | Resistor | 150 Ω | 0603 | 2 | basic | Green/red LED current limit. |
| R11 | Resistor | 100 kΩ | 0603 | 1 | basic | USB-plugged-in detector (top). |
| R12 | Resistor | 150 kΩ | 0603 | 1 | basic | USB-plugged-in detector (bottom). |
| R13 | Resistor | 100 Ω | 0603 | 1 | basic | MOSFET gate resistor, softens the switching edge. |
| C2 | Capacitor, electrolytic/polymer | 100 µF 10 V | SMD 6.3 × 5.4 | 1 | *search "100uF 10V SMD electrolytic 6.3x5.4"* (same as C12) | 3.3 V tank for Wi-Fi bursts. |
| C3 | Capacitor | 100 nF | 0603 | 1 | basic | Noise filter at the brain's power pin. |
| C4 | Capacitor | 1 µF | 0603 | 1 | basic | Clean reset at power-up (Espressif requirement). |
| C5, C7 | Capacitor | 10 µF 50 V X7R | **1210** | 2 | *search "10uF 50V 1210 X7R"* | Regulator input caps. 50 V MLCC only exists this big. |
| C6, C8 | Capacitor | 10 µF 16 V | 0805 | 2 | basic | Regulator output caps. |
| C10, C11 | Capacitor | 100 nF | 0603 | 2 | basic | Button debounce. |
| C12 | Capacitor, electrolytic | 100 µF 10 V | SMD 6.3 × 5.4 | 1 | *search "100uF 10V SMD electrolytic 6.3x5.4"* | Feeds the sensor's start-up gulp. |
| S1, S2 | Tactile switch | C&K KMR2 type, side-push | 4.2 × 2.8 SMD | 2 | *search "KMR2"* | RESET and BOOT buttons. |
| J2 | USB-C socket | HRO TYPE-C-31-M-12, 16-pin | SMD | 1 | C165948 ✅ | Plug your laptop in here. |

**Count: 32.** All SMD. Estimated JLCPCB assembly cost for this: setup ~₹700 + parts ~₹600 for 5 boards (the ESP32 module is most of it). Rough numbers — check the quote.

---

## B — You solder (14 parts on the board)

All through-hole, big pins, beginner-friendly. Buy from Robu / LCSC / local.

| Ref | What | Value / part | Qty | Plain words |
|---|---|---|---|---|
| U2 | 3.3 V regulator | RECOM R-78E3.3-1.0 (3 pins) | 1 | 12 V → 3.3 V for the brain. Runs cold. |
| U3 | 5 V regulator | RECOM R-78E5.0-1.0 (3 pins) | 1 | 12 V → 5 V for the sensor only. **Must be the 1.0 A version.** Same body as the 0.5 A part. |
| C1 | Capacitor, electrolytic | 470 µF 25 V, low-ESR 105 °C, 8 mm dia | 1 | **The big water tank** on 12 V. Long leg = +. |
| J1 | Screw terminal | 2-pin, 5.08 mm pitch (KF301 / Phoenix MKDS 1,5) | 1 | 12 V in, bare wires. Alternative to J8. |
| J8 | DC barrel jack | 5.5 × 2.1 mm, through-hole (DC-005) | 1 | 12 V in, the adapter's plug goes straight in. Centre pin = +. |
| J3 | Screw terminal | 2-pin, 5.08 mm | 1 | Lock wires. |
| J5 | Screw terminal | 2-pin, 5.08 mm | 1 | Exit button wires. |
| J4 | Female header | 1 × 14, 2.54 mm | 1 | Screen plugs in. |
| J6 | Male header | 1 × 4, 2.54 mm | 1 | Debug / recovery UART. Optional. |
| J7 | Male header | 1 × 3, 2.54 mm | 1 | Green + red panel LEDs plug in. |
| CN1 | PicoBlade socket | Molex 53047-0410, 4-pin 1.25 mm, vertical | 1 | Sensor cable plugs in. **Check the pitch on your sensor's cable first.** |
| BZ1 | Buzzer | **Passive piezo**, 12 mm, 7.6 mm pin pitch | 1 | Beeps. Must say *passive* and *piezo*. |

**Count: 14** (U2, U3, C1, J1, J3, J4, J5, J6, J7, J8, CN1, BZ1).

Budget alternatives, if the RECOM parts (~₹250 each) hurt: any "78xx-compatible switching regulator module" with the same 3-pin SIP footprint — e.g. **K7803-1000R3** (3.3 V, 1 A) and **K7805-1000R3** (5 V, 1 A), ~₹80 each. Same pins: 1 = in, 2 = GND, 3 = out. Check the input range covers 12 V (they do, 6.5–36 V).

---

## C — You buy, off the board

| Item | What | Have it? | Plain words |
|---|---|---|---|
| Palm sensor | DFRobot AI10 (SEN0677) | ✅ yes | The eye. Comes with its cable. |
| Screen | SmartElex 2.4" TFT 240×320, ST7789/ILI9341, resistive touch, 14-pin | found on Robu | Shows messages, tap to enrol. Runs on 3.3 V from our board. |
| Solenoid lock | Robu "DC 12V Cabinet Door Lock", 0.8 A, intermittent | found on Robu | The bolt. Cabinet-strength — fine for the prototype. |
| Power adapter | 12 V 2 A, 5.5 mm plug, **centre-positive** | found on Robu | Feeds everything. Plugs into J8. Check the label shows ⊕ on the centre. |
| Panel LEDs | 5 mm LED, green ×1, red ×1 | — | Face-of-the-box lights. Wired to J7. |
| Exit button | Any push button (momentary, normally-open) | — | Open from inside. Wired to J5. |
| Wires | Hookup wire, 22 AWG; LED wires can be thinner | — | Adapter, lock, button, LEDs. |
| Enclosure | 3D printed | — | Holes for screen, sensor, 2 LEDs, cable. |
| Standoffs + screws | M3, ×4 each | — | Board sits on 4 corner holes. |
| Iron + solder | — | ✅ presumably | For list B. |
| Multimeter | any ₹300 one | — | Not optional. Checks the adapter, the coil, the rails. |

---

## Totals

| | Count |
|---|---|
| A — assembled by JLCPCB | 32 |
| B — you solder | 14 |
| **On the board** | **46** |
| C — off-board | 11 items |

Rev 2.4 added D7, R11, R12, R13 after the Flux review. Old Rev 2 had 23 on-board parts. The extra 18 are: fuse, 4 regulator caps, EN cap, 2 debounce caps, sensor cap, 3 LED resistors + 1 LED, exit-button resistor, 2 headers, and a 3rd screw terminal. Every one has a reason in `DESIGN_REVIEW.md` or `POWER_BUDGET.md`.

---

## Do not skip these three

- **R2** — stops the door opening by itself when power comes back.
- **D2** — stops the lock killing Q1.
- **F1** — stops a wiring mistake burning the board.

About ₹15 together.

---

## Notes on ordering from JLCPCB

- Order **5 boards** (their minimum). Assemble **2** — that's the minimum assembly quantity, and you get spares.
- Choose **2-layer, 1.6 mm, HASL** — cheapest, fine for this.
- When uploading, they'll ask for three files from KiCad: **Gerbers**, **BOM (CSV)**, **CPL (placement CSV)**. We'll generate these at the end of PCB layout — not yet.
- **THT assembly:** JLCPCB can also solder list B for roughly ₹300–500 extra, but they must stock each part, and RECOM/Molex often aren't. Hand-soldering B is the safer bet the first time.
- **Parts they don't stock** show as "shortfall" in the quote. Anything from list A that's short: move it to list B and buy it yourself. The only awkward one would be the ESP32 module (it's SMD with an exposed pad) — if JLC has no stock, wait for stock rather than hand-soldering it.

---

## Choices we made, and why (unchanged from Rev 2, still true)

| Choice | What we picked | Why |
|---|---|---|
| Mains on the board? | **No** — external 12 V adapter | 230 V next to 3.3 V logic on a hobby board is a shock and fire risk. |
| Relay or MOSFET? | **MOSFET** | Shared ground, no isolation needed. Silent, no contacts to wear. 1 part instead of 8. |
| Which brain? | **ESP32-S3** | USB built in — no USB-serial chip. |
| Sensor voltage? | **5 V** (was 12 V) | 12 V is the very top of its range; cheap adapters overshoot. |
| USB power? | **Data only** | The regulators need ≥ 7 V. Desk work = plug the adapter too. |
| Screen backlight dimming? | No | 4 extra parts for nothing. |
| Status lights? | **Screen + 2 panel LEDs** | LEDs are readable from across the room; the screen isn't. |
