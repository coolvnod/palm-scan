# NETLIST.md — plain-words wiring table, palm-scan Rev 2

Read this before opening the schematic. If the schematic and this table disagree, one of them is wrong.
Net names are exactly what appears on the schematic labels.

## Power rails

| Net | Comes from | Feeds |
|---|---|---|
| `VIN_12V` | J1 pin 1 (+) or J8 centre pin | F1 only |
| `VIN_FUSED` | F1 pin 2 | D1 anode only |
| `+12V` | D1 cathode | C1, U2 in, U3 in, C5, C7, **J3 pin 1 + D2 cathode (lock)** — everything is behind the fuse and D1 |
| `+5V` | U3 out | C8, C12, CN1 pin 4 (sensor VCC) — **sensor only** |
| `+3V3` | U2 out | C2, C3, C6, U1 pin 2 (3V3), R1, R6, R7, J6 pin 1, **J4 pins 1 + 8 (display VCC + backlight)** |
| `VBUS` | J2 VBUS (A4 A9 B4 B9) | D3 pin 5, R11 (VBUS-present divider). Never powers anything. |
| `USB_DET` | R11/R12 divider | IO7 — 3.0 V when a USB host is plugged in |
| `GND` | J1 pin 2 (−) | everything |

## GPIO map (ESP32-S3-WROOM-1, module pin in brackets)

| GPIO | Net | Direction | Why this pin |
|---|---|---|---|
| EN [3] | `EN` | in | R1 10k → +3V3, C4 1µF → GND, S1 → GND |
| IO0 [27] | `BOOT` | in | strapping: S2 → GND, C10 100nF → GND. Internal pull-up. |
| IO4 [4] | `LOCK_EN` | out | R13 100Ω → `LOCK_G` → Q1 gate; R2 10k pulls `LOCK_G` low. Not a strapping pin, high-Z at reset. |
| IO7 [7] | `USB_DET` | in | VBUS ÷ (100k/150k) = 3.0 V when a USB host is present |
| IO5 [5] | `BUZZER` | out | R5 100Ω → BZ1 |
| IO6 [6] | `EXIT_BTN` | in | R6 10k → +3V3, C11 100nF → GND, R8 1k → `EXIT_SW` → J5 → GND |
| IO8 [12] | `TOUCH_IRQ` | in | optional, XPT2046 pen-down |
| IO9 [17] | `TOUCH_CS` | out | |
| IO10 [18] | `TFT_CS` | out | FSPICS0 (IOMUX, fastest) |
| IO11 [19] | `SPI_MOSI` | out | FSPID |
| IO12 [20] | `SPI_SCK` | out | FSPICLK |
| IO13 [21] | `SPI_MISO` | in | FSPIQ |
| IO14 [22] | `TFT_DC` | out | |
| IO17 [10] | `SEN_RX` | out | U1TXD → sensor's RX (CN1 pin 2, yellow) |
| IO18 [11] | `SEN_TX` | in | U1RXD ← sensor's TX (CN1 pin 3, green) |
| IO19 [13] | `USB_D-` | bidir | native USB |
| IO20 [14] | `USB_D+` | bidir | native USB |
| IO21 [23] | `TFT_RST` | out | |
| IO1 [39] | `LED_OK` | out | R9 150Ω → J7 pin 2 → panel green LED: palm recognised |
| IO2 [38] | `LED_DENY` | out | R10 150Ω → J7 pin 3 → panel red LED: not a member |
| IO43 [37] | `TXD0` | out | J6 debug header pin 2 |
| IO44 [36] | `RXD0` | in | J6 debug header pin 3 |
| IO3, IO45, IO46 | — | — | **strapping — left unconnected on purpose** |
| everything else | — | — | unconnected (no-connect flags in schematic) |

## Component-by-component

| Ref | Value | Footprint | Pin → Net |
|---|---|---|---|
| U1 | ESP32-S3-WROOM-1-N8R2 | RF_Module:ESP32-S3-WROOM-1 | 1 GND, 2 +3V3, 3 EN, 4 LOCK_EN, 5 BUZZER, 6 EXIT_BTN, 7 USB_DET, 10 SEN_RX, 11 SEN_TX, 12 TOUCH_IRQ, 13 USB_D-, 14 USB_D+, 17 TOUCH_CS, 18 TFT_CS, 19 SPI_MOSI, 20 SPI_SCK, 21 SPI_MISO, 22 TFT_DC, 23 TFT_RST, 27 BOOT, 36 RXD0, 37 TXD0, 38 LED_DENY, 39 LED_OK, 40 GND, 41 GND |
| U2 | R-78E3.3-1.0 | Converter_DCDC_RECOM_R-78E-0.5_THT | 1 +12V, 2 GND, 3 +3V3 |
| U3 | R-78E5.0-1.0 | Converter_DCDC_RECOM_R-78E-0.5_THT | 1 +12V, 2 GND, 3 +5V |
| F1 | Bourns MF-MSMF200/16 (2 A hold, 16 V) | Fuse_1812_4532Metric | 1 VIN_12V, 2 VIN_FUSED — **not** the MSMF110 (1.1 A), it would trip on every unlock |
| C1 | 470µF 25V | CP_Radial_D8.0mm_P3.50mm | + +12V, − GND |
| C2 | 100µF 10V | CP_Elec_6.3x5.4 (SMD electrolytic or polymer) | +3V3, GND — 100 µF MLCC does not exist in 0805 |
| C3 | 100nF | C_0603 | +3V3, GND — within 5 mm of U1 pin 2 |
| C4 | 1µF | C_0603 | EN, GND |
| C5 | 10µF 50V X7R | C_1210 | +12V, GND — at U2 pin 1. 50 V 10 µF MLCC needs 1210 and still loses ~40 % at 12 V bias |
| C6 | 10µF | C_0805 | +3V3, GND — at U2 pin 3 |
| C7 | 10µF 50V X7R | C_1210 | +12V, GND — at U3 pin 1 |
| C8 | 10µF | C_0805 | +5V, GND — at U3 pin 3 |
| C10 | 100nF | C_0603 | BOOT, GND — across S2 |
| C11 | 100nF | C_0603 | EXIT_BTN, GND — across J5 |
| R1 | 10k | R_0603 | +3V3, EN |
| R2 | 10k | R_0603 | LOCK_G, GND — gate pulldown, **safety** |
| R13 | 100Ω | R_0603 | LOCK_EN, LOCK_G — gate series, damps the switching edge |
| R11 | 100k | R_0603 | VBUS, USB_DET |
| R12 | 150k | R_0603 | USB_DET, GND |
| R3 | 5.1k | R_0603 | CC1, GND |
| R4 | 5.1k | R_0603 | CC2, GND |
| R5 | 220Ω | R_0603 | BUZZER, BZ_DRV — limits piezo edge current to ~15 mA |
| R6 | 10k | R_0603 | +3V3, EXIT_BTN |
| R7 | 1k | R_0603 | +3V3, LED_A |
| R8 | 1k | R_0603 | EXIT_SW, EXIT_BTN — series, protects IO6 from the wall wire |
| R9 | 150Ω | R_0603 | LED_OK, LED_OK_A — ~8 mA into a 5 mm green LED |
| R10 | 150Ω | R_0603 | LED_DENY, LED_DENY_A |
| J7 | PANEL LEDS 1x3 | PinHeader_1x03_P2.54mm_Vertical | 1 GND, 2 LED_OK_A, 3 LED_DENY_A — 5 mm LEDs on wires in the case; long leg (anode) to pin 2/3, short leg to pin 1 |
| C12 | 100µF 10V | CP_Elec_6.3x5.4 | +5V, GND — right at CN1, feeds the sensor's start-up spike |
| Q1 | AO3400A | SOT-23 | 1 G LOCK_G, 2 S GND, 3 D LOCK_SW |
| D1 | SS34 (SMA) | D_SMA | A VIN_FUSED, K +12V |
| D2 | SS54 (SMA) | D_SMA | A LOCK_SW, K +12V — flyback across lock, **safety** |
| D7 | SMAJ15A TVS | D_SMA | +12V, GND — clamps line transients at ~24 V, below Q1's 30 V |
| D4 | YELLOW LED 0603 | LED_0603_1608Metric | K GND, A LED_A — 3.3 V power indicator |

| D3 | USBLC6-2SC6 | SOT-23-6 | 1 USB_D-, 2 GND, 3 USB_D+, 4 USB_D+, 5 VBUS, 6 USB_D- |
| S1 | RESET | SW_Push_1P1T_NO_CK_KMR2 | EN, GND |
| S2 | BOOT | SW_Push_1P1T_NO_CK_KMR2 | BOOT, GND |
| J1 | 12V IN | MKDS-1,5-2-5.08 | 1 VIN_12V, 2 GND |
| J8 | DC JACK 5.5×2.1 | BarrelJack_Horizontal | 1 VIN_12V, 2 GND — pin 1 is the centre (+), pin 2 the sleeve; in parallel with J1, use either |
| J2 | USB-C | USB_C_Receptacle_HRO_TYPE-C-31-M-12 | VBUS×4 VBUS, GND×4+shell GND, D+ ×2 USB_D+, D− ×2 USB_D-, CC1 CC1, CC2 CC2, SBU NC |
| J3 | LOCK | MKDS-1,5-2-5.08 | 1 +12V, 2 LOCK_SW |
| J4 | DISPLAY 1x14 | PinSocket_1x14_P2.54mm_Vertical | 1 +3V3, 2 GND, 3 TFT_CS, 4 TFT_RST, 5 TFT_DC, 6 SPI_MOSI, 7 SPI_SCK, 8 +3V3, 9 NC, 10 SPI_SCK, 11 TOUCH_CS, 12 SPI_MOSI, 13 SPI_MISO, 14 TOUCH_IRQ |
| J5 | EXIT BTN | MKDS-1,5-2-5.08 | 1 EXIT_SW, 2 GND |
| J6 | DEBUG 1x4 | PinHeader_1x04_P2.54mm_Vertical | 1 +3V3, 2 TXD0, 3 RXD0, 4 GND — optional, recovery path if USB boot breaks |
| CN1 | AI10 sensor | Molex_PicoBlade_53047-0410 | 1 GND, 2 SEN_RX, 3 SEN_TX, 4 +5V |
| BZ1 | piezo | Buzzer_12x9.5RM7.6 | 1 BZ_DRV, 2 GND |

Total: 46 on-board parts + 2 panel LEDs.
Rev 2.4 (after Flux review): display moved to 3.3 V (no 5 V logic near the MCU; 5 V rail now feeds the sensor only); C2 → SMD electrolytic; C5/C7 → 1210; +R13 gate series; +D7 TVS on +12V; +R11/R12 VBUS-present divider on IO7.
Rev 2.3: Rev 2.3: status LEDs moved off-board to J7 (5 mm LEDs on wires), R9/R10 150Ω, +C12 100µF at the sensor, F1 = MF-MSMF200/16.
Rev 2.2: +green "recognised" on IO1, +red "denied" on IO2; D4 power LED now yellow.
Rev 2.1 notes: Rev 2.1 (after DESIGN_REVIEW.md): +F1 fuse, +D4/R7 power LED, +R8 exit-button series R, −C9 (redundant);
lock and D2 moved behind D1; sensor moved to 5 V; display SDO left unconnected.

## How the lock circuit works (low-side switch)

```
  +12V  ──┬───────────── J3.1 (lock +)      (after F1 and D1)
          │
        D2 (K)                      lock coil
          │                            │
        D2 (A) ───── LOCK_SW ──────── J3.2 (lock −)
                          │
                       Q1 drain
   IO4 ── LOCK_EN ──R13 100Ω── LOCK_G ── Q1 gate
                                  │        Q1 source ── GND
                                 R2 10k
              │
             GND
```

- Q1 sits on the *ground side* of the lock ("low-side switch"). The gate only needs 3.3 V above
  ground, which the ESP32 gives directly. A high-side switch would need a gate 12 V above ground → extra parts.
- R2 holds the gate at 0 V while the ESP32 is still booting (GPIOs are high-impedance for ~50 ms at reset).
  Without it the gate floats, picks up noise, and the lock can chatter or open at every power-up.
- D2 is reverse-biased in normal operation. When Q1 switches off, the coil's collapsing field tries to
  keep current flowing; D2 gives it a path back into the coil instead of forcing Q1's drain to hundreds of volts.
- The lock is fed from `+12V`, *after* F1 and D1. Rev 2.0 had it before D1 to keep inrush off C1 —
  that put Q1's body diode and D2 straight across a reversed adapter. D1 is rated 3 A; the lock's
  2 A inrush through it is fine, and C1 actually helps supply it.

## What is deliberately NOT here
- No relay, no optocoupler — MOSFET + shared ground does it.
- Nothing on the unprotected side of D1 except the fuse. Reverse the adapter and nothing conducts.
- No USB power path — see DATASHEETS.md §5.
- No pull-ups on IO45/IO46/IO3 — floating is the correct default for strapping pins we don't use.
