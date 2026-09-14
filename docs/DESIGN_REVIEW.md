# DESIGN_REVIEW.md — Rev 2 schematic, senior design review (2026-09-13)

> **Status: all 7 fixes applied → Rev 2.1.** ERC 0/0, netlist 131/131, scripted pass 2 clean. Layout notes below still apply.

Two passes: (1) block-by-block read as a reviewer, (2) scripted checks on KiCad's own
exported netlist (`../hardware/kicad/check_netlist.py` + ad-hoc checks). ERC 0/0. Netlist 125/125.

Severity: 🔴 will break hardware  🟠 will cause a bug you'll chase for days  🟡 should fix  🟢 fine

---

## 🔴 1. Plugging the adapter in backwards destroys Q1 and D2

**What happens.** D1 protects the "+12V" rail. But the lock is fed from `VIN_12V` — *before* D1.
Reverse the adapter and current flows: GND → Q1's body diode → LOCK_SW → D2 → VIN_12V.
That's a dead short across the adapter through two tiny parts. They die in under a second.

**Why it slipped in.** COMPONENTS.md wanted the lock's inrush kept away from C1. Good idea,
wrong place — it moved the lock outside the protection.

**Fix.** Feed the lock from `+12V` (after D1). D1 is rated 3 A; the lock's 2 A inrush is fine.
Change J3 pin 1 and D2 cathode from `VIN_12V` → `+12V`. Zero new parts.

**Also add a fuse.** F1, 2 A resettable polyfuse, in series right after J1. ₹5. Without it, any
short on the board (including this one) relies on the adapter's protection, which cheap adapters don't have.

## 🟠 2. Display and touch fight over MISO

`SPI_MISO` goes to both the ST7789 (J4 pin 9, SDO) and the XPT2046 touch (J4 pin 13, T_DO).
On these red display boards the ST7789's SDO does **not** release the line when its CS is high.
Result: touch reads garbage, or the screen stops updating after the first touch. Very well-known
problem with this exact module; people spend days on it.

**Fix.** Leave J4 pin 9 unconnected. The firmware never reads from the display. Touch keeps MISO.

## 🟠 3. Sensor is at the very top of its voltage range

AI10 spec: 5–12 V. We give it 12 V. Cheap "12 V" adapters give 12.5–13.5 V with light load.
The sensor's internal regulator then runs hot ("chip heating is normal" says the wiki — at 12 V it's hotter).

**Fix, recommended.** Make U3 a `R-78E5.0-1.0` (1 A, same footprint, same pins) and feed the sensor
from `+5V`. CN1 pin 4 → `+5V`. 5 V rail total ≈ 650 mA, inside 1 A. Sensor runs cool, and the
adapter's exact voltage stops mattering.

## 🟠 4. Solenoid can cook itself if firmware hangs with the lock open

Most 12 V solenoid locks are **intermittent duty** — energised for 10 s max, then they overheat.
If the ESP32 crashes with `LOCK_EN` high, the coil stays on until it burns.

**Fix.** Two layers:
- Firmware: hardware task watchdog (built into ESP-IDF) + a hard cap of 5 s on any unlock.
- Buy: a solenoid rated **continuous duty** if you ever need "hold open". Check the listing.

Also **fail-secure means power cut = door locked.** The door MUST be openable from inside by a
handle. That's a fire-safety rule, not a preference. Never fit this on a door without one.

## 🟡 5. No sign of life if the MCU doesn't boot

"The screen replaces the LEDs" — only after the MCU boots. First power-up with a dead 3.3 V rail
shows nothing at all. One LED + resistor on +3V3 (2 parts, ₹2) tells you the regulator works.

**Fix.** Add D4 (green 0603) + R7 (1 kΩ) from +3V3 to GND.

## 🟡 6. Exit-button wire has no surge protection

The exit button wire runs to the other side of the wall. It's an antenna for static and for
whatever the electrician ran next to it. R6/C11 debounce it; nothing limits current into IO6.

**Fix.** R8, 1 kΩ in series between J5 pin 1 and the IO6 net. Costs ₹1, saves the GPIO.

## 🟡 7. C9 is redundant

C9 (100 nF across RESET) is on the same net as C4 (1 µF, EN to GND). C4 already does the job.
**Fix.** Delete C9. −1 part.

## 🟢 Verified correct (both passes)

- D1 orientation, D2 orientation, Q1 low-side wiring, R2 gate pull-down.
- USB-C: CC1/CC2 5.1 kΩ, D+/D− on IO20/IO19, ESD array, VBUS isolated.
- EN: 10 kΩ + 1 µF per Espressif. BOOT on IO0. Strapping pins IO3/45/46 floating.
- UART crossing: ESP TX → sensor RX (yellow), ESP RX → sensor TX (green). 3.3 V logic both sides.
- 3.3 V rail: 110 µF total, under RECOM's 220 µF limit. C3 on the module's 3V3 pin.
- Every net has ≥2 connections; every GPIO net touches exactly one ESP32 pin.
- R-78E input 7–28 V; 12 V adapter fine. Regulators run cool.

## Things that only matter at PCB layout — write these down for Flux

1. **Antenna keep-out.** ESP32-S3-WROOM-1 antenna end must hang off the board edge, or sit over a
   15 mm no-copper zone on *all* layers. Ignore this and WiFi range drops to a metre.
2. **C3 within 5 mm of U1 pin 2.** Not "nearby". 5 mm.
3. **Lock current traces ≥ 1 mm wide** (J1 → F1 → D1 → J3 → Q1 → GND). 2 A inrush.
4. **Q1 source straight to J1 GND**, not through the ESP32's ground area. Lock return current
   through the MCU ground = resets when the lock fires.
5. **D3 within 5 mm of the USB connector**, on the D+/D− traces, before they go anywhere else.
6. **D1 on a big copper pour** — it's the only part that gets warm.
7. **Display ribbon under 10 cm** or drop SPI to 20 MHz. 40 MHz over a long ribbon = garbage pixels.
8. **PicoBlade CN1 near the board edge** the sensor cable comes from — cable is short.
9. **M3 holes in the corners**, 3.2 mm, with 6 mm keep-out.

## How this project can still fail after all the above (honest list)

| Failure | How likely | What stops it |
|---|---|---|
| Wrong adapter (9 V or 19 V laptop brick) | common | 9 V: sensor and regs OK. 19 V: C1 is 25 V, regs 28 V — survives. Label the socket. |
| Adapter dies at 2 am, door locked | certain, eventually | Inside handle. Non-negotiable. |
| Sensor doesn't recognise wet/cold hands | happens | Firmware fallback: exit button, and long-term a keypad. Hardware can't fix it. |
| Someone unplugs the sensor cable while powered | user error | PicoBlade tolerates hot-plug. Firmware must re-init the sensor when it comes back. |
| Water on the board | outdoor install | Enclosure IP rating. Conformal coat is ₹200. |
| Firmware bug opens the lock | code error | Upstream design: `loop()` is the only path that can unlock. Keep that. |
| Flash corrupted, USB boot dead | rare | J6 UART header. That's why it's there. |
| Solenoid rated wrong (AC, or 24 V) | ordering error | Buy 12 V DC, ≤1 A, continuous duty, and read the listing twice. |
| Board ordered before sim/bring-up plan | you | Bring-up order: power only → check rails → add MCU → USB flash → add display → add sensor → add lock last. |

---

## About Flux

Flux imports **KiCad part libraries only** — not schematics, not projects. There is no
"open the KiCad file in Flux". You would redraw all 34 parts in Flux by hand from NETLIST.md.

Options, ranked:
1. **PCB in KiCad.** Schematic is already here, ERC-clean, footprints assigned. One click to PCB.
   Zero rework. Best choice unless you specifically want Flux's autorouter/AI.
2. **Flux, redraw from NETLIST.md.** ~1–2 hours. Then you have two sources of truth and every
   change must be made twice. Only worth it if you want to learn Flux itself.

## Changes to apply, in one go

| # | Change | Parts |
|---|---|---|
| 1 | Lock + D2 cathode fed from `+12V` instead of `VIN_12V` | 0 |
| 1 | F1 2 A polyfuse after J1 | +1 |
| 2 | J4 pin 9 (display SDO) → no-connect | 0 |
| 3 | U3 → R-78E5.0-1.0; CN1 pin 4 → `+5V` | 0 |
| 5 | D4 LED + R7 1 kΩ on +3V3 | +2 |
| 6 | R8 1 kΩ series on exit button | +1 |
| 7 | Delete C9 | −1 |

Net: 34 → 37 parts.

---

## Appendix — checklist verification (2026-09-13, Rev 2.1)

| Item | Result | Evidence |
|---|---|---|
| D1 polarity | ✅ | KiCad netlist: D1 pin 1 (K) = `+12V`, pin 2 (A) = `VIN_FUSED`. Current flows adapter → F1 → A → K → board. |
| 2 A polyfuse vs solenoid | ✅ with a spec | Steady load ≈ 1.35 A (lock 1 A + regulators 0.35 A); inrush ≈ 2.4 A for < 100 ms. A 2 A-hold / 4 A-trip 1812 polyfuse (e.g. Littelfuse 1812L200/16) needs seconds at 2× to trip. Buy one rated ≥ 16 V. If the solenoid measures > 0.8 A, go to 3 A hold. |
| BOOT cap / pull-up | ✅ | IO0: S2 to GND + C10 100 nF; pull-up is the chip's internal strap pull-up (Espressif devkit does the same). EN RC (10 ms) is longer than IO0's RC (~4.5 ms), so IO0 is high before the strap is sampled. |
| ST7789 voltage | ✅ (module not in hand) | VCC = 5 V → module's on-board LDO → 3.3 V logic. ESP32 3.3 V SPI matches. Manual specifies 5 V VCC. **Physically confirm the LDO on the board before power-up**; if absent, VCC must move to +3V3. |
| Buzzer type & driver | ✅ after change | Must be a **passive piezo element** (capacitive load). R5 changed 100 Ω → 220 Ω: edge current 15 mA vs IOH 40 mA. A magnetic buzzer (coil) would need a transistor — don't buy one. |
| GPIO conflicts | ✅ | 18 GPIOs used, none twice. USB on IO19/20 only. FSPI on IO10–13 (IOMUX, fastest). Strapping IO0 = BOOT only; IO3/45/46 floating. JTAG IO39–42 free. UART0 IO43/44 only on J6. No ADC2 use (would conflict with Wi-Fi). N8R2 quad PSRAM uses no GPIO. |
| Power / ground / decoupling | ✅ | +3V3: C2 100 µF, C3 100 nF, C6 10 µF. +5V: C8 10 µF. +12V: C1 470 µF, C5, C7 10 µF. EN: C4 1 µF. U1 GND on pins 1, 40, 41 (EPAD). U2/U3 GND pin 2. VBUS: no cap needed (data-only). |
| MOSFET + flyback ratings | ✅ | AO3400A: 30 V ≥ 12.5 V clamped, 5.7 A ≥ 2 A inrush, VGS(th) max 1.45 V < 3.3 V drive, RDS(on) ≈ 40 mΩ → 40 mW. SS54: 40 V ≥ 12 V, 5 A ≥ 1 A, 150 A surge. R2 10 kΩ keeps gate low through reset. |
| USB-C CC / ESD | ✅ | CC1 → R3 5.1 kΩ → GND, CC2 → R4 5.1 kΩ → GND (sink, both orientations). D+ on A6+B6, D− on A7+B7. USBLC6-2SC6: pins 1/6 = I/O1 on D−, pins 3/4 = I/O2 on D+, pin 2 GND, pin 5 VBUS — matches the KiCad symbol's pin names. |
| **PCB fabrication-ready** | ❌ **No** | There is no PCB. The **schematic** is ready for layout. Fabrication-ready means Gerbers that pass DRC — that's the next project phase. |

---

## Response to the Flux review (2026-09-14) → Rev 2.4

Flux found 12 items. Verdict on each, with evidence:

| # | Flux finding | Verdict | What was done |
|---|---|---|---|
| 1 | AI10 UART level unconfirmed | **Valid — not in the wiki.** Evidence it is 3.3 V: DFRobot's own library lists FireBeetle-ESP32, ESP8266 and M0 (all 3.3 V-only, non-5 V-tolerant) as "works well" wired directly; the techiesms build drives a classic ESP32 directly. Net naming is from the *sensor's* view (SEN_RX = sensor RX ← ESP TX), checked in the netlist. | No change. **Bring-up step added:** before plugging CN1 into the board, power the sensor and measure its TX (green) wire — UART idle is HIGH, must read ≤ 3.6 V. |
| 2 | Display pinout/levels unconfirmed | **Partly valid.** Pin *order* is the standard 2.4" red-board order (manual lists names, not positions) — must be checked against the silkscreen when the module arrives. Level risk: real if any module output ran at 5 V. | **Display moved to 3.3 V** (J4 pins 1 and 8 → +3V3; module is rated 3.3–5 V per Robu). Now nothing near the MCU carries 5 V. Backlight slightly dimmer. 5 V rail is sensor-only. |
| 3 | C2 100 µF/16 V in 0805 unrealistic | **Correct, my mistake.** No such MLCC exists; 100 µF MLCC starts at 1210/6.3 V and halves under bias. | C2 → **100 µF 10 V SMD electrolytic/polymer, 6.3 × 5.4** (same part as C12). Still within RECOM's 220 µF limit (110 µF total). |
| 4 | R-78E 1.0 A footprint vs 0.5 A | **Checked — identical package.** Both datasheets: 11.6 × 8.5 × 10.4 mm, 2.54 mm pitch, 0.51 mm pins. Footprint drill 1.0 mm. | No change. |
| 5 | No VBUS sensing | **Valid for USB compliance**; harmless in practice. | Added **R11 100k / R12 150k divider → IO7 (`USB_DET`, 3.0 V)**. Firmware can show "USB connected" and hold off D+ pull-up when absent. |
| 6 | No gate series resistor | **Valid, cheap.** | Added **R13 100 Ω** IO4 → gate. R2 10k stays gate-to-source. |
| 7 | No TVS on 12 V | **Valid** — lock cable is an antenna, Q1 is only 30 V. | Added **D7 SMAJ15A** across +12V/GND (15 V standoff, ~24 V clamp). |
| 8 | F1 vs 2 A adapter | **Already analysed** in POWER_BUDGET §3: with a 2 A adapter F1 never trips on a short — the adapter self-protects; F1 guards against an oversized adapter. | Documented, no change. |
| 9 | C5/C7 10 µF 50 V in 0805 | **Correct, my mistake.** | C5/C7 → **1210 X7R**. Effective ~6 µF at 12 V bias; RECOM marks these caps optional and C1 470 µF is on the same rail. |
| 10 | J1/J8 paralleled, needs warning | **Valid.** | Text added on the schematic page: "Use J1 OR J8 — never both. Centre pin of J8 is +." Will go on silkscreen too. |
| 11 | USB shield straight to GND | **Acceptable for a prototype**; RC to chassis is an EMC-lab refinement. | Documented decision, no change. |
| 12 | Exit-button cable ESD | **Acceptable** — R8 1k + C11 100 nF + ESP32 internal clamps. | Documented. Layout rule: exit-button cable must not run alongside lock wiring. |

Procurement checks Flux listed (CN1 pitch, J4 pin-1 orientation, J8 footprint vs the bought DC-005, U2/U3 body, C2 exact part, F1 variant, piezo vs magnetic, USB-C MPN) are all already in COMPONENTS.md / POWER_BUDGET §7 as "verify against the physical part before ordering the PCB".

**Rev 2.4 verification:** ERC 0/0 across 10 sheets; NETLIST.md ↔ KiCad netlist 153/153 pins; 27 scripted end-to-end checks pass (see session log / `check_netlist.py`). 46 on-board parts, 38 nets.
