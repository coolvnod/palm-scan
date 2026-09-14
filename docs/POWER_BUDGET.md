# POWER_BUDGET.md — palm-scan Rev 2.4

> **Rev 2.4 (2026-09-14, after Flux review):** display moved from +5V to **+3V3** → 3.3 V rail typ 250 mA / peak 620 mA of 1000 (38 % margin at peak);
> 5 V rail now sensor-only, typ 330 / worst 530 mA. D7 SMAJ15A TVS on +12V. C2 is now an SMD electrolytic (100 µF MLCC in 0805 does not exist);
> C5/C7 moved to 1210 (10 µF 50 V MLCC needs it; ~6 µF effective at 12 V bias, RECOM says input caps are optional anyway).
> R13 100 Ω gate series: adds 6 nC × … negligible; Q1 still fully on. R11/R12 VBUS divider draws 20 µA from the host.

> **Update 2026-09-13 (later):** solenoid confirmed from Robu listing — 12 V, **0.8 A**, 9.6 W, **intermittent duty**, 2.45 N (cabinet lock).
> Display confirmed 3.3–5 V input (on-board LDO). F1 specified as Bourns **MF-MSMF200/16** (the MSMF110 = 1.1 A hold is wrong).
> C12 100 µF added at CN1 for sensor inrush. Status LEDs moved to panel header J7, 150 Ω → ~8 mA each.
> Remaining UNKNOWN: sensor start-up inrush (mitigated by C12), display current (estimate), LED Vf (buy 5 mm red/green, ~2 V).

Every number is tagged with where it came from:
- **[DS]** = datasheet in `datasheets/` (or the DFRobot wiki for the sensor)
- **[CALC]** = calculated from [DS] numbers, formula shown
- **[EST]** = engineering estimate; the part has no datasheet number for this
- **UNKNOWN** = no source. Tells you which spec is needed.

Ambient assumed 25–45 °C (indoor wall, Bengaluru). Adapter assumed regulated switch-mode, 12 V ±5 %.

---

## 0. The picture

```
ADAPTER 12 V ──J1──F1(polyfuse)──D1(SS34)──┬── +12V ──┬── U2 R-78E3.3-1.0 ── +3V3 ── ESP32, LEDs, buzzer, pull-ups
                                           │          ├── U3 R-78E5.0-1.0 ── +5V  ── display, AI10 sensor
                                           │          └── J3 ── SOLENOID ── Q1 ── GND     (D2 flyback across solenoid)
                                           └── C1 470 µF
USB-C ── data only. VBUS goes nowhere.
```

---

## 1. Rail summary

| Rail | Source | Normal load | Worst steady | Peak (ms) | Source limit | Margin at worst |
|---|---|---|---|---|---|---|
| **+3V3** | U2, 1.0 A | 150 mA [CALC] | 200 mA | **520 mA** (Wi-Fi TX burst) | 1000 mA [DS] | 48 % at peak ✅ |
| **+5V** | U3, 1.0 A | 430 mA [CALC/EST] | **630 mA** | UNKNOWN (sensor inrush) | 1000 mA [DS] | 37 % steady ✅, inrush ⚠️ |
| **+12V** (electronics) | D1 | 250 mA [CALC] | 460 mA | — | 3 A [DS] | ✅ |
| **+12V** (incl. solenoid, ≤5 s) | D1 | 1.05 A [CALC] | **1.5 A** | 1.5 A | 3 A [DS] | 50 % ✅ |
| **VIN_12V** (through F1) | adapter | 1.05 A | 1.5 A | 1.5 A | 2 A hold [EST] | 25 % ⚠️ see §3 |

---

## 2. Recommended power supply

| | Value | Why |
|---|---|---|
| Voltage | **12 V DC, regulated** | Solenoid is 12 V. U2 needs ≥ 7 V, U3 needs ≥ 8 V [DS] — so 9 V adapters are **out**. |
| Current | **2 A** (1.5 A minimum) | Worst steady 1.5 A, for 5 s. 2 A covers it. (3 A was first recommended so the 4 A-trip polyfuse could act before the adapter — but a 2 A SMPS adapter simply protects itself on a short, which is fine; F1 then guards against an oversized adapter.) A reused router / LED-strip adapter labelled 12 V ≥ 1.5 A works. |
| Wattage | 24 W | 12 V × 2 A. Actual draw: **3 W idle, ~13 W while unlocking** [CALC]. |
| Connector | 5.5 × 2.1 mm barrel → screw terminal J1 | Label the polarity on the enclosure. D1 saves the board if it's wrong, but nothing will work. |
| Tolerance | ±5 % → 11.4–12.6 V | After F1 (−0.1 V) and D1 (−0.5 V): **+12V rail = 10.8–12.0 V.** Solenoid sees this. Check its minimum pull-in voltage — UNKNOWN. |

### Battery backup, if you want it (not on this schematic)
- **3S Li-ion / LiFePO₄** (9.0–12.6 V) or **12 V SLA 7 Ah**. Both stay above U3's 8 V minimum. [DS]
- Drain at idle: ~0.25 A at 12 V = **6 Ah per day** [CALC]. A 7 Ah SLA gives ~1 day; a 3S 5 Ah pack ~20 h.
- Needs its own charger + protection board + a diode-OR with the adapter — that's another 6–8 parts, a separate design.
- Note the lock is fail-secure: with no battery, power cut = door locked, opened by the inside handle. The battery only buys palm access during an outage.

---

## 3. Component-by-component

Columns: V in = voltage the part actually sees · I norm = typical · I peak = worst/inrush · Rating = datasheet maximum · P = dissipation · Verdict.

### Protection and input

| Part | V in | I norm | I peak | Rating | P | Verdict |
|---|---|---|---|---|---|---|
| **J1** screw terminal MKDS 1,5 | 12.6 V | 1.05 A | 1.5 A | ~8 A / 160 V [EST — Phoenix MKDS 1,5 family; confirm exact part] | 0 | ✅ |
| **F1** polyfuse 2 A hold | 12.6 V | 1.05 A | 1.5 A (≤ 5 s) | UNKNOWN — **no part chosen yet** | ~0.1 W [EST, 0.05 Ω] | ⚠️ see below |
| **D1** SS34 | 12.5 V reverse max | 1.05 A | 1.5 A (5 s) / C1 charging spike ≪ 100 A IFSM | 3 A avg, 100 A surge, 40 V [DS] | 0.5 V × 1.05 = **0.53 W** during unlock, ~0.13 W idle [CALC] | ✅ RθJL 17 °C/W [DS] → +9 °C. Needs the copper pour called out in DESIGN_REVIEW.md |
| **C1** 470 µF 25 V | 12.0 V | ripple from lock steps | plug-in surge, limited by adapter | 25 V → 48 % derating [CALC] | negligible | ✅ Buy **105 °C low-ESR** |

**F1 — what to buy and the trap.** Spec: **1812 SMD polyfuse, 2.0 A hold, 4.0 A trip, ≥ 16 V** (e.g. Littelfuse 1812L200/16, Bourns MF-MSMF200/16). Two things the number "2 A" hides:
1. Hold current derates with temperature: ~1.6 A at 50 °C [EST, typical PTC curve]. Worst load 1.5 A only lasts 5 s, so no nuisance trips — **but measure your solenoid**. If it's over 0.9 A, go to 2.5 A hold.
2. Trip needs **4 A**. A 2 A adapter cannot supply 4 A — it sags or hiccups first, and F1 never trips. That's why §2 says 3 A adapter. With a 3 A adapter, a hard short pulls 3 A+, F1 heats and trips in tens of seconds; the adapter's own limit covers the first seconds. Acceptable.

### Regulators

| Part | V in | I out norm | I out peak | Rating | P | Verdict |
|---|---|---|---|---|---|---|
| **U2** R-78E3.3-1.0 | 10.8–12.0 V (needs 7–28) [DS] | 150 mA | 520 mA (Wi-Fi TX) | 1.0 A [DS] | P_out 0.5 W ÷ 0.85 eff [EST at 15 % load] → **0.09 W** loss; at peak 1.7 W ÷ 0.88 → 0.23 W | ✅ 48 % margin. Output cap 110 µF ≤ 220 µF limit [DS] |
| **U3** R-78E5.0-1.0 | 10.8–12.0 V (needs 8–28) [DS] | 430 mA | 630 mA steady, inrush UNKNOWN | 1.0 A, SCP continuous auto-recovery [DS] | 3.15 W ÷ 0.90 [DS 93 % full load] → **0.35 W** loss | ✅ steady. ⚠️ sensor inrush — see AI10 |
| U2 input current at 12 V | — | 50 mA | 165 mA | — | — | [CALC: P_in ÷ 12 V] |
| U3 input current at 12 V | — | 200 mA | 290 mA | — | — | [CALC] |

Both are switching regulators — 570 kHz [DS]. No heatsink, no derating needed under 60 °C ambient [DS].

### Brain

| Part | V in | I norm | I peak | Rating | P | Verdict |
|---|---|---|---|---|---|---|
| **U1** ESP32-S3-WROOM-1-N8R2 | 3.3 V (3.0–3.6 OK, 3.6 abs max) [DS] | 90 mA [DS: 240 MHz dual core, 66–92 mA] + ~15 mA PSRAM [EST] + Wi-Fi RX 95 mA [DS] → **~130 mA** typical when connected | **355 mA** RF TX burst (802.11b @ 20.5 dBm) [DS] on top of CPU → design to **500 mA** [DS Table 6-2 says supply ≥ 0.5 A] | Supply must deliver ≥ 500 mA [DS] | 3.3 V × 0.13 = 0.43 W avg, spread over the module | ✅ U2 gives 1 A |
| Light-sleep (if firmware uses it) | | 240 µA [DS] | | | | not needed for a wall-powered lock |
| GPIO source per pin | | | | 40 mA IOH / 28 mA IOL [DS] | | LEDs 4 mA, buzzer 15 mA peak ✅ |

### Lock driver

| Part | V | I norm | I peak | Rating | P | Verdict |
|---|---|---|---|---|---|---|
| **Solenoid** (J3) | 10.8–12.0 V | **UNKNOWN** — spec says "under 1 A". Used 0.8 A below. | ~1.2× holding for the first 100 ms (cold coil) [EST]. **No 2 A "gulp"** — a DC solenoid's current ramps up L/R to V/R; it doesn't overshoot like a motor. COMPONENTS.md overstated it. | UNKNOWN — duty cycle rating (intermittent vs continuous) | 12 V × 0.8 A = **9.6 W in the coil** while energised | ⚠️ **Measure coil resistance: I = 12 V ÷ R.** Get the datasheet or listing: holding current, duty, min pull-in voltage, inductance. |
| **Q1** AO3400A | VDS 12.6 V max (12 V + D2's 0.55 V clamp) | 0.8 A | 1.0 A | 30 V, 5.7 A cont, 30 A pulsed, VGS ±12 V [DS] | 0.8² × 40 mΩ [DS, interpolated 2.5–4.5 V curve] = **26 mW** | ✅ +3 °C [DS RθJA 125 °C/W]. Gate 3.3 V vs VGS(th) max 1.45 V [DS] — fully on. |
| Q1 body diode (reverse-adapter case) | | 0 | 0 — D1 now blocks | 2 A [DS] | 0 | ✅ Rev 2.0 would have put 12 V across this. Fixed. |
| **D2** SS54 flyback | 12 V reverse | 0 (only conducts at turn-off) | 0.8–1 A decaying, ~ms | 40 V, 5 A, 150 A surge [secondary source — components101/Newark, **not** a manufacturer PDF] | ½·L·I² per unlock; L UNKNOWN (typ 10–50 mH → 3–25 mJ) — shared with coil resistance, diode gets a fraction of a mJ | ✅ 5× margin either way |
| **R2** 10 kΩ pull-down | 3.3 V | 0.33 mA | — | 0.1 W (0603) | 1 mW | ✅ |
| **J3** screw terminal | 12 V | 0.8 A | 1 A | ~8 A [EST] | 0 | ✅ |

### 5 V loads

| Part | V in | I norm | I peak | Rating | P | Verdict |
|---|---|---|---|---|---|---|
| **AI10 sensor** (CN1) | 5.0 V (spec 5–12 V) [DS wiki] | 320–330 mA **@ 8 V** [DS wiki]. At 5 V: if internal reg is linear → same 330 mA; if switching → 330 × 8/5 = **530 mA**. Used 530 (worst). | **UNKNOWN.** Cameras + AI SoCs commonly spike 1–2 A for a few ms at power-on. | UNKNOWN | ~2.6 W inside the sensor (wiki: "chip heating is normal") | ⚠️ **Need: DFRobot AI10 inrush / startup current, or measure with a scope + 0.1 Ω shunt.** Mitigation already possible: add **C12 100 µF on +5V at CN1** to feed the spike (U3's SCP would otherwise hiccup on a > 1 A spike). |
| Standby (auto-detect off) | | 120–130 mA @ 8 V [DS wiki] → ~200 mA at 5 V worst | | | | |
| **CN1** PicoBlade 53047 | 5 V | 530 mA | inrush UNKNOWN | 1.0 A per contact [EST — Molex PicoBlade family; confirm 53047-0410 sheet] | 0 | ✅ steady, ⚠️ inrush |
| **Display** SmartElex 2.4" ST7789 + XPT2046 (J4) | 5.0 V into on-board LDO [DS manual: VCC = 5 V] | **UNKNOWN in the manual.** [EST]: backlight 60–80 mA + ST7789 10 mA + XPT2046 1 mA + LDO 5 mA → **~100 mA** | ~120 mA (backlight cold) [EST] | UNKNOWN | 0.5 W, mostly backlight LEDs | ⚠️ Need: **module current spec, and confirm the on-board LDO exists**. Measure with a USB power meter — 2 minutes. |
| J4 pin 1 (VCC) + pin 8 (LED) | | ~20 mA / ~80 mA | | 3 A per pin (2.54 mm socket) [EST] | | ✅ |

### 3.3 V loads (besides ESP32)

| Part | V | I | Peak | Rating | P | Verdict |
|---|---|---|---|---|---|---|
| **D4** yellow power LED + R7 1 kΩ | 3.3 V | (3.3 − 2.0) ÷ 1k = **1.3 mA** [CALC, Vf UNKNOWN until part chosen — AlGaInP yellow ≈ 2.0 V] | — | 20 mA typ LED | 2.6 mW | ✅ dim but visible indoors |
| **D5** green + R9 330 Ω (IO1) | 3.3 V | (3.3 − 2.1) ÷ 330 = **3.6 mA** — **only if AlGaInP "yellow-green" (Vf ≈ 2.1 V)**. A true-green InGaN LED has Vf ≈ 3.0 V → 0.9 mA, nearly invisible. | — | 40 mA IOH [DS] | 5 mW | ⚠️ Vf UNKNOWN — buy Vf ≤ 2.2 V, or drop R9 to 100 Ω for InGaN |
| **D6** red + R10 330 Ω (IO2) | 3.3 V | (3.3 − 1.8) ÷ 330 = **4.5 mA** [CALC] | — | 40 mA IOH | 8 mW | ✅ |
| **BZ1** passive piezo + R5 220 Ω (IO5) | 3.3 V square wave, 2–4 kHz | avg ≈ 2·C·V·f = 2 × 20 nF × 3.3 × 4 kHz = **0.5 mA** [CALC, C UNKNOWN — typ 10–30 nF] | 3.3 ÷ 220 = **15 mA** at each edge, ns | 40 mA IOH [DS] | ~2 mW in R5 | ✅ **Only if it is a piezo.** Magnetic buzzer (16–42 Ω coil) → 100+ mA → GPIO damage. |
| R1, R6 pull-ups 10 kΩ | 3.3 V | 0.33 mA each, only while pressed | | | | ✅ |
| **J6** debug header | 3.3 V pin | 0 normally; a USB-UART dongle may *draw* ~10 mA if it's powered from J6 pin 1 | | | | ✅ don't power the board from J6 |

### USB

| Part | V | I | Rating | Verdict |
|---|---|---|---|---|
| **J2** USB-C 16-pin | VBUS 5 V present but **unused** | 0 A | 3 A VBUS [EST, HRO TYPE-C-31-M-12 family] | ✅ |
| **R3/R4** 5.1 kΩ CC | ≤ 5 V | source's Rp is 80–330 µA → 0.4–1.7 V on CC | 0.1 W | ✅ tells the host "sink, 5 V, ≤ 500 mA". We draw 0. |
| **D3** USBLC6-2SC6 | 5 V VBUS ref, 3.3 V data | ~µA leakage | 5.25 V working, ±15 kV ESD [from memory — **ST datasheet not fetched**, download timed out] | ✅ but mark as unverified |
| **U1** USB PHY | powered from 3.3 V internally | included in ESP32 figure | | ✅ |

---

## 4. Loss ledger (where the watts go, during an unlock)

| Where | W | Source |
|---|---|---|
| Solenoid coil | 9.6 | 12 V × 0.8 A [CALC] |
| AI10 sensor | 2.6 | 5 V × 0.53 A worst |
| Display | 0.5 | [EST] |
| ESP32 + LEDs + buzzer | 0.5 | 3.3 V × 0.15 A |
| D1 | 0.53 | 0.5 V × 1.05 A |
| U3 loss | 0.35 | 7 % of 3.15 W |
| U2 loss | 0.09 | |
| F1 | 0.1 | I²R, 0.05 Ω [EST] |
| Q1 | 0.03 | |
| **Total from adapter** | **~14 W → 1.2 A at 12 V** | vs 36 W available ✅ |
| Idle (door locked, sensor watching) | **~3 W → 0.25 A** | |

Nothing on the board dissipates more than 0.6 W. Nothing needs a heatsink. The two warm spots are **D1** (0.5 W, 5 s bursts) and **U3** (0.35 W continuous) — both handled by copper pours.

---

## 5. PCB traces and copper (2-layer, 1 oz / 35 µm)

IPC-2221 outer-layer rule of thumb, 10 °C rise [CALC]:

| Net | Current | Minimum width | **Use** |
|---|---|---|---|
| VIN_12V, VIN_FUSED, +12V trunk, J3, LOCK_SW, Q1 source → GND | 1.5 A | 0.7 mm | **1.5 mm**, or a pour |
| +12V to U2/U3 | 0.3 A | 0.2 mm | 0.6 mm |
| +5V trunk to CN1 | 0.63 A (+ inrush) | 0.35 mm | **1.0 mm** |
| +3V3 trunk | 0.52 A pk | 0.3 mm | 0.8 mm |
| GND | all of the above | — | **full bottom-layer pour**, stitched vias every 5 mm near Q1/D1/U2/U3 |
| Signals, LEDs, buzzer | ≤ 15 mA | 0.15 mm | 0.25 mm |
| USB D+/D− | — | — | 0.25 mm, **same length ±1 mm, 90 Ω diff** — or just keep them < 20 mm and parallel; USB 2.0 full-speed forgives a lot |

Vias: 0.3 mm drill / 0.6 mm pad carries ~1 A each. Lock path needs **≥ 2 vias** wherever it changes layer.

---

## 6. What could still burn or fail — ranked

| # | Risk | Likelihood | Consequence | Fix / what's needed |
|---|---|---|---|---|
| 1 | **Sensor inrush > 1 A trips U3's short-circuit protection → sensor reboots in a loop** | medium (unknown) | sensor never comes up, or comes up flaky | **UNKNOWN spec: AI10 startup current.** Measure it. Add C12 100 µF on +5V at CN1 regardless — ₹3. |
| 2 | **Solenoid is continuous-duty rated? min voltage?** | unknown | coil burns if firmware holds it; or won't pull in at 10.8 V | **UNKNOWN spec: solenoid datasheet** (R_coil, duty, pull-in V). Firmware 5 s cap + task watchdog. |
| 3 | 2 A adapter + 2 A polyfuse = fuse never trips on a short | certain | adapter hiccups/shuts down on its own — nothing burns. F1 still catches a wrong (oversized) adapter. | accepted; 2 A adapter is fine |
| 4 | Green LED is InGaN (Vf 3 V) → invisible | common ordering mistake | "green LED doesn't work" | buy Vf ≤ 2.2 V, or R9 = 100 Ω |
| 5 | Buzzer is magnetic, not piezo | common ordering mistake | IO5 damaged | listing must say **piezo, passive** |
| 6 | Display has no on-board LDO on this exact variant | low | 5 V into a 3.3 V controller → dead display | look for the SOT-223 regulator next to the header before power-up |
| 7 | D1 on a thin trace with no pour | layout error | D1 runs ~40 °C hot; survives, degrades | follow §5 |
| 8 | Cheap "12 V" adapter actually 13.5 V unloaded | common | everything still within ratings (C1 25 V, regs 28 V, Q1 30 V) | ✅ design tolerates it |
| 9 | ESP32 Wi-Fi burst while lock fires | normal operation | 0.52 A on 3.3 V + 1 A on 12 V simultaneously | ✅ separate regulators; U2 doesn't see the lock at all |

---

## 7. UNKNOWN list — get these before ordering

| Spec | Why it matters | Where to get it |
|---|---|---|
| **Solenoid**: coil resistance, holding current, duty cycle, min pull-in voltage, inductance | sizes F1, confirms Q1/D1 margins, firmware timing | seller listing / measure with a multimeter (R) |
| **AI10 sensor**: startup inrush, internal regulator type, current at 5 V input | U3 stability, C12 sizing | DFRobot support, or scope + 0.1 Ω shunt |
| **Display module**: total current at 5 V, on-board LDO present | U3 budget, safety of 5 V VCC | USB power meter + look at the board |
| **F1**: exact part | voltage rating, hold/trip, derating | choose 1812L200/16 or MF-MSMF200/16 and read its sheet |
| **LED Vf** (D4, D5, D6) | brightness, resistor values | pick parts on LCSC, read Vf @ 5 mA |
| **Piezo capacitance** | buzzer current (only matters if > 50 nF) | seller listing; usually 10–30 nF |
| **D2 SS54** manufacturer PDF | I used distributor summaries | Vishay/Diodes Inc SS54 PDF — any 40 V 3 A+ Schottky also works |
| **D3 USBLC6-2SC6** manufacturer PDF | pinout verified against the KiCad symbol, not the sheet | st.com (fetch timed out) |
| **CN1, J1/J3/J5, J2** exact current ratings | I used family-typical numbers | Molex 53047, Phoenix MKDS 1,5, HRO TYPE-C-31-M-12 sheets |
| **Adapter** regulation and unloaded voltage | +12V rail range | measure yours — 30 seconds with a multimeter |
