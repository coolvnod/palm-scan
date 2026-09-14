# DATASHEETS.md — reference facts for the palm-scan Rev 2 schematic

Every number here was pulled from the manufacturer document (or the vendor
wiki) on 2026-09-13. Local copies live in `datasheets/`. When something is
from memory or a secondary source it is marked **(unverified)**.

---

## 1. Power parts

### U2 — RECOM R-78E3.3-1.0  (`datasheets/R-78E-1.0.pdf`)
- Input 7–28 V, output 3.3 V @ 1.0 A, efficiency 91 % at full load.
- Pins (SIP-3, 2.54 mm pitch): **1 = +Vin, 2 = GND, 3 = +Vout**. Same as a 7805.
- Quiescent 1.5 mA, switching at 570 kHz. No heat-sink needed.
- Input/output caps are *optional* per RECOM: 10 µF MLCC each. We fit them anyway.
- **Max capacitive load on the output: 220 µF.** Our C2 (100 µF) is inside that.
- Minimum load 2 % — the ESP32 alone is far above that.

### U3 — RECOM R-78E5.0-0.5  (`datasheets/R-78E-0.5.pdf`)
- Input 7–28 V, output 5 V @ 0.5 A, efficiency 92 %.
- Same pinout as U2. Same 10 µF in/out caps. Same 220 µF output limit.

### Q1 — AOS AO3400A, N-channel MOSFET  (`datasheets/AO3400A.pdf`)
- VDS 30 V, ID 5.7 A continuous (25 °C), 30 A pulsed. Package SOT-23.
- **RDS(on) < 48 mΩ at VGS = 2.5 V** → at our 3.3 V gate it is fully on.
- VGS(th) 0.65–1.45 V. Qg 6 nC — tiny, the GPIO can drive it directly.
- Pinout SOT-23: **1 = G, 2 = S, 3 = D** (standard).
- At 1 A lock current: P = 1² × 0.05 = 50 mW. Stays cold. ✅

### D1 — SS34 Schottky, reverse-polarity + reservoir isolation  (`datasheets/SS34.pdf`, Vishay)
- VRRM 40 V, IF 3 A, VF ≈ 0.5 V at 3 A.
- **Package: SMA (DO-214AC)** — the JLCPCB-stocked version (LCSC C8678). Vishay's PDF here is the SMC
  variant; electrical specs are the same, SMA is thermally a bit worse.
- Heat check (Rev 2.3): everything incl. the lock goes through D1 → 1.05 A for ≤ 5 s → 0.53 W bursts, 0.13 W idle.
  SMA ≈ 90 °C/W on a minimal pad → +12 °C idle; bursts are too short to matter. Give it a copper pour anyway.

### D2 — SS54 Schottky, lock flyback  **(secondary source — components101, Newark)**
- VRRM 40 V, IF 5 A, VF ≈ 0.55 V, surge 150 A, package SMC (DO-214AB).
- Any 40 V / ≥3 A Schottky works here. SS34 would also do; SS54 is just more margin.

### C1 / C2 / C3 — generic; only ratings matter
- C1 470 µF 25 V electrolytic on the 12 V input (after D1). Ripple-current rated, low ESR.
- C2 100 µF 16 V on 3.3 V (≤ 220 µF limit above). Ceramic or polymer, not a cheap electrolytic.
- C3 100 nF 0603 X7R at the module's 3V3 pin — Espressif requires this.
- **Added by the datasheets, not in COMPONENTS.md:** 4 × 10 µF MLCC (U2/U3 in+out) and
  1 × 1 µF on EN. See §2.

---

## 2. ESP32-S3-WROOM-1  (`datasheets/esp32-s3-wroom-1.pdf`, v1.8)

- 41 pins (40 + EPAD). 3V3 on pin 2, GND on 1 / 40 / EPAD. EN on pin 3.
- Supply: 3.0–3.6 V, **≥ 500 mA** recommended. Wi-Fi TX peaks ≈ 350–400 mA.
- GPIO drive: IOH 40 mA, IOL 28 mA per pin.
- **EN pin: Espressif requires R = 10 kΩ pull-up + C = 1 µF to GND** (RC delay so
  3V3 is stable before the chip releases reset). COMPONENTS.md had only the resistor. Add C4 = 1 µF.
- Do not leave EN floating. Reset button = EN to GND.

### Strapping pins — keep these free or know what you're doing
| GPIO | Controls | Default | Our use |
|---|---|---|---|
| 0  | boot mode | pull-up (normal boot) | BOOT button to GND (S2) — this is its intended use |
| 3  | JTAG source | — | **leave unconnected** |
| 45 | VDD_SPI voltage | pull-down (3.3 V) | **leave unconnected** — pulling high sets flash to 1.8 V and bricks boot |
| 46 | boot mode + ROM print | pull-down | **leave unconnected** |

### Pins we cannot use
- IO26–IO32 are internal (flash) and not on the module. IO35/36/37 are PSRAM on R8 modules.
- IO19 / IO20 = **USB D− / D+**. Reserved for J2.
- IO43 / IO44 = UART0 TX/RX (boot messages). Keep free for debugging, or reuse for the sensor? → **No**, ROM prints garbage on it at boot and the sensor would see it. Use UART1.

### Module pin numbers we will wire (module pin → GPIO)
- pin 4 IO4, 5 IO5, 6 IO6, 7 IO7, 8 IO15, 9 IO16, 10 IO17, 11 IO18, 12 IO8,
  13 IO19 (USB D−), 14 IO20 (USB D+), 15 IO3, 16 IO46, 17 IO9, 18 IO10, 19 IO11, 20 IO12,
  21 IO13, 22 IO14, 23 IO21, 24 IO47, 25 IO48, 26 IO45, 27 IO0, 28 IO35, 29 IO36, 30 IO37,
  31 IO38, 32 IO39, 33 IO40, 34 IO41, 35 IO42, 36 RXD0/IO44, 37 TXD0/IO43, 38 IO2, 39 IO1.

---

## 3. Display — SmartElex 2.4" ST7789V + XPT2046 resistive touch  (`datasheets/smartelex-2.4-touch.pdf`)

- 240 × 320, RGB565, SPI. Driver ST7789V. Touch controller XPT2046 (also SPI).
- 14-pin 2.54 mm header, in this order (this is the standard "red board" layout):

| Pin | Name | Goes to |
|---|---|---|
| 1 | VCC | 5 V (module has on-board 3.3 V LDO) |
| 2 | GND | GND |
| 3 | CS | ESP32 GPIO (TFT_CS) |
| 4 | RESET | ESP32 GPIO (TFT_RST) |
| 5 | DC | ESP32 GPIO (TFT_DC) |
| 6 | SDI (MOSI) | SPI MOSI |
| 7 | SCK | SPI SCK |
| 8 | LED | backlight, 5 V (or 3.3 V, dimmer) |
| 9 | SDO (MISO) | SPI MISO |
| 10 | T_CLK | SPI SCK (shared) |
| 11 | T_CS | ESP32 GPIO (TOUCH_CS) |
| 12 | T_DIN | SPI MOSI (shared) |
| 13 | T_DO | SPI MISO (shared) |
| 14 | T_IRQ | ESP32 GPIO, optional (manual says "not required") |

- Logic is 3.3 V; the on-board LDO makes 3.3 V from the 5 V VCC. ESP32 SPI drives it directly.
- **Correction to COMPONENTS.md:** the 5 V rail feeds VCC *and* LED, not "only the backlight".
- **Design option (decide in III):** these boards run fine with VCC = 3.3 V and LED = 3.3 V.
  That would delete U3 and its two caps (3 parts) and put ~100 mA more on U2's 1 A rail.
  Backlight is dimmer at 3.3 V. Keeping U3 for now; flagged.
- SPI: ST7789 tolerates 40–80 MHz; XPT2046 must be clocked ≤ 2.5 MHz — the firmware
  switches SPI speed per chip-select, hardware doesn't care.

---

## 4. Palm sensor — DFRobot AI10 (SEN0677)  (wiki.dfrobot.com/sen0677/ + `datasheets/SEN0677_AI10_protocol_manual_V1.0.pdf`)

- The PDF is the **software protocol manual only** (frame format, every command, flowcharts). It has no electrical data. Everything below is from the wiki.
- Supply **5–12 V**. Operating 320–330 mA @ 8 V. Standby 120–130 mA. Rev 2.4 feeds it from **+5V** (U3, 1 A).
- UART, **115200 baud**. Protocol: `EF AA CMD LenH LenL payload XOR`. On power-up the module sends `NOTE:READY` — firmware must wait for it before sending commands.
- UART logic level is **NOT documented anywhere**. Assumed 3.3 V because DFRobot's library lists 3.3 V-only boards (FireBeetle-ESP32/ESP8266/M0) as wired directly. **Bring-up rule: measure the green TX wire idle level before connecting CN1 — must be ≤ 3.6 V.** If it reads 5 V, add a 1k/2k divider on SEN_TX → U1RXD.
- UART connector, 4-pin 1.25 mm (PicoBlade-style), pinout:

| Pin | Colour | Function | Wire to |
|---|---|---|---|
| 1 | Black | GND | GND |
| 2 | Yellow | UART_RX (sensor listens) | ESP32 **TX** (U1TXD) |
| 3 | Green | UART_TX (sensor talks) | ESP32 **RX** (U1RXD) |
| 4 | Red | VCC 5–12 V | +5V (U3 output) |

- Crossed naming is the #1 wiring mistake here — sensor RX ← ESP TX. Label the schematic nets
  `SEN_RX` / `SEN_TX` from the *sensor's* point of view, like the upstream firmware does.
- Has a separate USB port (UVC camera) needing 5 V — we do not wire it. Wiki: "chip heating is normal".
- Recognition distance: palm 15 cm. Dimensions 57.8 × 20 × 10.12 mm.
- **(unverified)** Exact mating header part number. Molex 53047-0410 (PicoBlade 1.25 mm, 4-way,
  vertical THT) is the standard choice. Check the pitch on the physical sensor cable before ordering.

---

## 5. USB-C, ESD, connectors, switches

### J2 — USB-C receptacle, 16-pin USB 2.0 only
- Part: HRO TYPE-C-31-M-12 (JLCPCB C165948) or GCT USB4105-GF-A. **(unverified — confirm stock)**
- Wire: VBUS ×4 → 5 V_USB net; GND ×4 + shell → GND; D+ (A6 and B6 tied) → IO20; D− (A7, B7 tied) → IO19.
- CC1 → R3 5.1 kΩ → GND; CC2 → R4 5.1 kΩ → GND. This advertises "sink, default USB power".
- SBU1/SBU2 unconnected.
- USB VBUS must **not** feed the 3.3 V regulator (its minimum input is 7 V). Desk power over USB
  needs its own path — see design decision in III.

### D3 — ST USBLC6-2SC6, USB ESD array  **(pinout from memory — verify against the KiCad symbol)**
- SOT-23-6. Pin 1 = I/O1, 2 = GND, 3 = I/O2, 4 = I/O2, 5 = VBUS, 6 = I/O1.
- I/O1 pair and I/O2 pair are internally the same node — use one pin of each, or route through.
- Place within 5 mm of the connector, on the D+/D− traces.

### CN1 — Molex PicoBlade 53047-0410  (1.25 mm, 4-way, vertical THT)
- 1 A per contact, plenty for 330 mA. KiCad footprint exists in the standard library.

### J1 / J3 / J5 — screw terminals
- J1 (12 V in) and J3 (lock): **5.08 mm pitch** (KF301 / Phoenix MKDS type) — takes 18 AWG.
- J5 (exit button): 5.08 mm too, so one screwdriver fits all. Two wires, no polarity.

### J4 — 1×14 female header, 2.54 mm
- Standard. Display plugs in perpendicular or via a 14-way ribbon.

### S1 / S2 — tactile 3 × 4 × 2 mm side-actuated SMD
- Any 2-pin SMD tact. Add 100 nF across each for debounce (standard on Espressif devkits).

### BZ1 — passive piezo element
- Capacitive load, few mA at 2–4 kHz. Drives straight from a GPIO through a 100 Ω series R
  to blunt the edge current. Loud enough for a door; not loud enough for a hallway.
  If you want loud, that's a magnetic buzzer + transistor + flyback diode = 3 more parts.

---

## Part-count delta vs COMPONENTS.md

| Added | Why |
|---|---|
| C4 1 µF on EN | Espressif requirement |
| C5–C8 10 µF ×4 | RECOM in/out caps for U2, U3 |
| C9, C10 100 nF ×2 | button debounce |
| R5 100 Ω | buzzer series |

23 → 31 parts. All passives, all 0603/0805. Still one-fifth of the original board.
