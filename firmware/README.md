# firmware

ESP-IDF application for the palm-scan controller. Not started.

Planned modules, in build order:
1. `ai10/` — UART driver for the DFRobot AI10: frame codec (`EF AA id len data xor`), `RESET`, `GET_STATUS`, `VERIFY`, `ENROLL`, `DEL_USER`, `SNAP&UPLOAD_IMAGE`. Wait for `NOTE:READY` after power-up before sending anything.
2. `lock/` — solenoid state machine. Hard 5 s cap per unlock, task watchdog, `LOCK_EN` low on any fault or reset.
3. `ui/` — LVGL on the 2.4" TFT (ST7789/ILI9341 autodetect) + XPT2046 touch. Screens: idle, recognised, denied, enrol, user list.
4. `app/` — glue: exit button, panel LEDs, buzzer, USB detect, logging.

Develop on an ESP32-S3 devkit + breadboard first; the custom PCB is not required for any of this.
