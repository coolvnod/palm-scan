"""Per-connection illustrations, the power-flow picture and the scan timeline.

Each `card_*` returns an SVG string sized to its own content. All pin numbers and
net names come from docs/NETLIST.md.
"""

from parts import *  # noqa: F401,F403

PIN_DY = 24          # vertical spacing between pins in a pin block


def pin_block(x, y, pins, title, kind="header", wire_from_x=None, wire_colors=None, plain=True):
    """A zoomed connector: body with numbered pins, net name and plain-words job per pin.

    pins: list of (number, net, plain_words) — plain_words may be "".
    wire_from_x: if given, a coloured wire is drawn from that x into each pin.
    """
    n = len(pins)
    body_h = n * PIN_DY + 14
    o = ""
    # connector body
    if kind == "screw":
        o += rrect(x, y, 44, body_h, r=4, fill=TERMINAL_GREEN, stroke="#1d5f33", sw=1.2)
    elif kind == "picoblade":
        o += rrect(x, y, 44, body_h, r=3, fill="#f4f1e8", stroke="#9a9484", sw=1.2)
    elif kind == "barrel":
        o += rrect(x, y, 44, body_h, r=4, fill="url(#gPlastic)", stroke="#000", sw=1.2)
    elif kind == "usb":
        o += rrect(x, y, 44, body_h, r=8, fill="url(#gMetal)", stroke="#4d5257", sw=1.2)
    else:
        o += rrect(x, y, 44, body_h, r=3, fill="url(#gPlastic)", stroke="#000", sw=1.2)
    o += text(x + 22, y - 8, title, size=11, weight=700, anchor="middle")
    for i, (num, net, words) in enumerate(pins):
        cy = y + 7 + PIN_DY / 2 + i * PIN_DY
        if wire_from_x is not None and wire_colors is not None and wire_colors[i]:
            o += wire(f"M{wire_from_x},{cy} L{x - 2},{cy}", wire_colors[i], width=4.5)
        # pin contact
        if kind == "screw":
            o += circle(x + 22, cy, 7, fill="url(#gMetal)", stroke="#555", sw=0.9)
            o += line(x + 17.5, cy, x + 26.5, cy, stroke="#444", sw=1.6)
            o += rrect(x - 8, cy - 5.5, 8, 11, r=1, fill="#0f3d1f", stroke="#0a2a15", sw=0.6)
        elif kind == "picoblade":
            o += rrect(x + 14, cy - 4, 16, 8, r=1, fill="url(#gCopper)", stroke="#8a6a1e", sw=0.6)
        elif kind == "usb":
            o += rrect(x + 10, cy - 3.5, 24, 7, r=2, fill="#111", stroke="none")
        elif kind == "barrel":
            if i == 0:
                o += circle(x + 22, cy, 8, fill="#0d0d0d", stroke="#666", sw=1)
                o += circle(x + 22, cy, 3, fill="url(#gMetal)", stroke="#333", sw=0.6)
            else:
                o += rrect(x + 8, cy - 4, 28, 8, r=2, fill="url(#gMetal)", stroke="#555", sw=0.8)
        else:
            o += rrect(x + 16, cy - 4, 12, 8, r=1, fill="url(#gCopper)", stroke="#8a6a1e", sw=0.6)
        o += mono(x + 22, cy + 3.5, str(num), size=9, fill="#ffffff" if kind not in ("picoblade", "usb") else INK,
                  anchor="middle", weight=700)
        # labels to the right
        o += mono(x + 56, cy + 4, net, size=11, weight=700)
        if words:
            o += text(x + 150, cy + 4, words, size=10.5, fill=LABEL)
    return o, body_h


def frame(w, h, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" '
            f'style="font-family:{SANS}">' + defs() +
            f'<rect width="{w}" height="{h}" fill="{PAPER}"/>' + inner + "</svg>")


# ------------------------------------------------------------------ 4.1 power in
def card_power() -> str:
    o = wall_adapter(30, 50)
    o += wire("M184,97 C230,97 250,103 300,103", "#2b2b2b", width=6)
    o += barrel_plug(302, 103, facing="right")
    o += text(105, 170, "12 V ⎓ 2 A, plug 5.5 × 2.1 mm, centre ⊕", size=10.5, fill=LABEL, anchor="middle")
    # J8 zoom
    blk, h = pin_block(400, 60, [("◎", "VIN_12V", "centre pin — 12 V positive (+)"),
                                  ("○", "GND", "outer sleeve — ground (−)")],
                       "J8  barrel jack", kind="barrel")
    o += blk
    # J1 alternative
    blk2, h2 = pin_block(400, 172, [("1", "VIN_12V", "bare wire, + (red)"),
                                    ("2", "GND", "bare wire, − (black)")],
                         "J1  screw terminal (alternative)", kind="screw", wire_from_x=330,
                         wire_colors=[WIRE["12V"], WIRE["GND"]])
    o += blk2
    o += text(330, 244, "Use J8 or J1 — never both.", size=10.5, weight=700, fill="#a33", anchor="end")
    return frame(780, 262, o)


# ------------------------------------------------------------------ 4.2 sensor
def card_sensor() -> str:
    o = sensor_module(30, 70, conn_side="right")
    cols = [WIRE["GND"], WIRE["YEL"], WIRE["GRN"], WIRE["12V"]]
    pins = [("1", "GND", "black — ground, the shared return"),
            ("2", "SEN_RX", "yellow — board talks → sensor listens"),
            ("3", "SEN_TX", "green — sensor talks → board listens"),
            ("4", "+5V", "red — 5 V power for the sensor")]
    # sheath from the sensor connector, then fan out
    o += wire("M216,103 C260,103 270,110 300,110", "#8a8f94", width=11)
    blk, h = pin_block(400, 60, pins, "CN1  sensor socket", kind="picoblade")
    o += blk
    for i, c in enumerate(cols):
        cy = 60 + 7 + PIN_DY / 2 + i * PIN_DY
        o += wire(f"M300,110 C330,110 340,{cy} 398,{cy}", c, width=4)
    # direction arrows on the two data wires
    o += flow_arrow(560, 47, 620, 47, color=WIRE["YEL"], sw=3)
    o += text(628, 51, "questions go this way (yellow)", size=9.5, fill=MUTED)
    o += text(120, 190, "Cable comes fitted to the sensor.", size=10.5, fill=LABEL, anchor="middle")
    o += text(120, 206, "Only the plug goes on the board.", size=10.5, fill=LABEL, anchor="middle")
    return frame(780, 230, o)


# ------------------------------------------------------------------ 4.3 display
def card_display() -> str:
    pins = [("1", "+3V3", "power for the screen"),
            ("2", "GND", "ground"),
            ("3", "TFT_CS", "“I’m talking to the screen”"),
            ("4", "TFT_RST", "reset the screen"),
            ("5", "TFT_DC", "command or picture data?"),
            ("6", "SPI_MOSI", "picture data → screen"),
            ("7", "SPI_SCK", "the clock (metronome)"),
            ("8", "+3V3", "backlight power"),
            ("9", "—", "not connected (on purpose)"),
            ("10", "SPI_SCK", "the same clock, for touch"),
            ("11", "TOUCH_CS", "“I’m talking to the touch”"),
            ("12", "SPI_MOSI", "touch commands → touch chip"),
            ("13", "SPI_MISO", "touch position → board"),
            ("14", "TOUCH_IRQ", "“someone touched me”")]
    o = f'<g transform="translate(20,40) scale(1.1)">' + display_module(0, 0) + "</g>"
    # 14 straight gold pins into the header
    blk, h = pin_block(400, 40, pins, "J4  14-pin socket  (screen’s pins go straight in)")
    o += blk
    for i in range(14):
        cy = 40 + 7 + PIN_DY / 2 + i * PIN_DY
        o += line(268, cy, 398, cy, stroke=COPPER, sw=3)
        o += line(268, cy, 398, cy, stroke="#7a5a12", sw=0.7)
    o += text(140, 250, "Pin 1 on the screen must meet pin 1 on the board.", size=10.5, weight=700, anchor="middle")
    o += text(140, 266, "The board’s pin 1 has a square pad.", size=10.5, fill=LABEL, anchor="middle")
    return frame(780, 40 + h + 30, o)


# ------------------------------------------------------------------ 4.4 solenoid
def card_lock() -> str:
    o = f'<g transform="translate(30,120)">' + solenoid_lock(0, 0) + "</g>"
    pins = [("1", "+12V", "always 12 V (after fuse & valve)"),
            ("2", "LOCK_SW", "the board connects this to ground to fire the bolt")]
    blk, h = pin_block(400, 70, pins, "J3  lock terminal", kind="screw")
    o += blk
    p1, p2 = 70 + 7 + PIN_DY / 2, 70 + 7 + PIN_DY / 2 + PIN_DY
    o += wire(f"M70,134 V{p1} H398", WIRE["12V"], width=4.5)
    o += wire(f"M95,134 V{p2} H398", "#e8e8e8", width=4.5)
    o += text(30, 250, "Two wires, either way round. The board switches the − side (a “low-side switch”).",
              size=10.5, fill=LABEL)
    return frame(780, 270, o)


# ------------------------------------------------------------------ 4.5 exit button
def card_exit() -> str:
    o = push_button(110, 120)
    pins = [("1", "EXIT_SW", "goes to the brain through a 1 kΩ guard"),
            ("2", "GND", "ground")]
    blk, h = pin_block(400, 90, pins, "J5  exit-button terminal", kind="screw", wire_from_x=170,
                       wire_colors=["#e8e8e8", WIRE["GND"]])
    o += blk
    o += text(30, 190, "Any momentary push button.", size=10.5, fill=LABEL)
    o += text(30, 206, "Pressed = the two wires touch = the board sees it.", size=10.5, fill=LABEL)
    return frame(780, 230, o)


# ------------------------------------------------------------------ 4.6 panel LEDs
def card_leds() -> str:
    o = ""
    pins = [("1", "GND", "both short legs (−) join here"),
            ("2", "LED_OK_A", "green long leg (+) — “recognised”"),
            ("3", "LED_DENY_A", "red long leg (+) — “not recognised”")]
    blk, h = pin_block(400, 70, pins, "J7  panel LED header", kind="header")
    o += blk
    p1, p2, p3 = (70 + 7 + PIN_DY / 2 + i * PIN_DY for i in range(3))
    # LEDs lie on their side, legs pointing at the header: long leg (+) below, short leg (−) above
    gx, gy = 250, 104
    rx, ry = 130, 150
    o += f'<g transform="rotate(-90 {gx} {gy})">' + led_5mm(gx, gy, "#3aa655") + "</g>"
    o += f'<g transform="rotate(-90 {rx} {ry})">' + led_5mm(rx, ry, "#d62828") + "</g>"
    o += text(gx - 22, gy + 4, "green", size=10, fill=MUTED, anchor="end")
    o += text(rx - 22, ry + 4, "red", size=10, fill=MUTED, anchor="end")
    # green: short leg (−) tip (gx+24, gy-4) → pin 1 ; long leg (+) tip (gx+30, gy+4) → pin 2
    o += wire(f"M{gx+24},{gy-4} H300 V{p1} H398", WIRE["GND"], width=3.5)
    o += wire(f"M{gx+30},{gy+4} H320 V{p2} H398", WIRE["GRN"], width=3.5)
    # red: long leg (+) tip → pin 3 straight ; short leg (−) tip → up and over, joins the black at pin 1
    o += wire(f"M{rx+30},{ry+4} H340 V{p3} H398", "#d62828", width=3.5)
    o += wire(f"M{rx+24},{ry-4} H170 V40 H350 V{p1}", WIRE["GND"], width=3.5)
    o += circle(350, p1, 4, fill="#222", stroke="#fff", sw=1)
    o += text(260, 32, "the two − wires join into one", size=9, fill=MUTED, anchor="middle")
    o += text(30, 215, "Long leg = +. No resistor needed in the wire — the board already has them (150 Ω each).",
              size=10.5, fill=LABEL)
    return frame(780, 235, o)


# ------------------------------------------------------------------ 4.7 USB-C
def card_usb() -> str:
    o = laptop(30, 60)
    o += wire("M184,110 C230,110 250,118 300,118", WIRE["USB"], width=5.5)
    o += rrect(298, 112, 26, 12, r=5, fill="url(#gMetal)", stroke="#4d5257", sw=0.9)
    pins = [("A/B", "VBUS", "5 V from the laptop — sensed, not used as power"),
            ("A/B", "USB_D+ / D−", "the data pair, protected by D3"),
            ("A5/B5", "CC1 / CC2", "5.1 kΩ each — tells the laptop “I’m a device”"),
            ("—", "GND / shield", "ground")]
    blk, h = pin_block(400, 60, pins, "J2  USB-C socket", kind="usb")
    o += blk
    o += text(105, 190, "Either way up. Programming, logs, updates.", size=10.5, fill=LABEL, anchor="middle")
    return frame(780, 215, o)


# ------------------------------------------------------------------ 4.8 debug header
def card_debug() -> str:
    o = usb_serial_dongle(60, 100)
    pins = [("1", "+3V3", "reference only — do NOT feed power in here"),
            ("2", "TXD0", "board talks → dongle’s RX"),
            ("3", "RXD0", "dongle’s TX → board listens"),
            ("4", "GND", "ground")]
    blk, h = pin_block(400, 60, pins, "J6  debug header (optional)", kind="header", wire_from_x=140,
                       wire_colors=[WIRE["3V3"], WIRE["GRN"], "#e8e8e8", WIRE["GND"]])
    o += blk
    o += text(95, 160, "Only if USB ever stops working.", size=10.5, fill=LABEL, anchor="middle")
    o += text(95, 176, "Dongle must be a 3.3 V type.", size=10.5, weight=700, fill="#a33", anchor="middle")
    return frame(780, 200, o)


# ------------------------------------------------------------------ 6. power flow
def power_tree() -> str:
    W, H = 900, 420
    o = ""

    def node(x, y, w, h, title, sub, fill="#f5f5f5", stroke="#999"):
        s = rrect(x, y, w, h, r=8, fill=fill, stroke=stroke, sw=1.2)
        s += text(x + w / 2, y + 22, title, size=13, weight=700, anchor="middle")
        s += text(x + w / 2, y + 40, sub, size=10.5, fill=LABEL, anchor="middle")
        return s

    def pipe(x1, y1, x2, y2, color, width, label=""):
        s = wire(f"M{x1},{y1} L{x2},{y2}", color, width=width, outline=False)
        if label:
            s += text((x1 + x2) / 2, (y1 + y2) / 2 - 9, label, size=10.5, fill=MUTED, anchor="middle")
        return s

    # source
    o += node(20, 170, 130, 56, "Wall adapter", "12 V · up to 2 A", fill="#ffffff")
    o += pipe(150, 198, 190, 198, WIRE["12V"], 10, "≤ 1.5 A")
    o += node(190, 170, 90, 56, "F1", "fuse", fill="#fff3e0", stroke="#e0a040")
    o += pipe(280, 198, 310, 198, WIRE["12V"], 10)
    o += node(310, 170, 90, 56, "D1", "one-way valve", fill="#fff3e0", stroke="#e0a040")
    o += pipe(400, 198, 440, 198, WIRE["12V"], 10)
    # 12 V bus (vertical bar)
    o += rrect(440, 60, 14, 290, r=4, fill=WIRE["12V"], stroke="none")
    o += text(447, 48, "+12 V rail", size=10.5, weight=700, anchor="middle")
    o += pipe(440, 300, 400, 300, WIRE["12V"], 6)
    o += node(270, 272, 130, 56, "C1  470 µF tank", "smooths the rail", fill="#e8f4ff", stroke="#7aa7d9")
    o += pipe(440, 340, 260, 340, WIRE["12V"], 6)
    o += node(140, 312, 120, 56, "D7  surge clamp", "sits across the rail", fill="#fff3e0", stroke="#e0a040")
    # branches
    o += pipe(454, 90, 500, 90, WIRE["12V"], 8, "0.3 A")
    o += node(500, 62, 100, 56, "U2", "12 V → 3.3 V", fill="#e8f5e9", stroke="#4caf50")
    o += pipe(600, 90, 680, 90, WIRE["3V3"], 8, "0.15 – 0.5 A")
    o += node(680, 62, 200, 56, "3.3 V rail", "brain · screen · LEDs · beeper", fill="#fffbe6", stroke="#e9c46a")

    o += pipe(454, 170, 500, 170, WIRE["12V"], 8, "0.3 A")
    o += node(500, 142, 100, 56, "U3", "12 V → 5 V", fill="#e8f5e9", stroke="#4caf50")
    o += pipe(600, 170, 680, 170, WIRE["5V"], 8, "0.35 – 0.65 A")
    o += node(680, 142, 200, 56, "5 V rail", "palm sensor only", fill="#fff1e0", stroke="#f77f00")

    o += pipe(454, 240, 680, 240, WIRE["12V"], 8, "0.8 – 1 A, ≤ 5 s at a time")
    o += node(680, 212, 200, 56, "Solenoid", "through Q1, the electronic switch", fill="#f3f3f3", stroke="#999")

    o += text(20, 396, "Everything right of D1 is protected: reversed adapter → nothing flows; short on the board → F1 opens, then resets when cool.", size=10.5, fill=LABEL)
    o += text(20, 414, "At the adapter: ≈ 0.25 A idle, ≈ 1.2 A while the bolt is pulled — well inside a 2 A adapter.", size=10.5, fill=LABEL)
    return frame(W, H, o)


# ------------------------------------------------------------------ 7. scan timeline
def scan_timeline() -> str:
    W, H = 900, 300
    o = ""
    steps = [
        ("Power on", "yellow light on\nthe board; screen\nshows “starting”", "#f4c20d"),
        ("Sensor ready", "sensor sends READY\non the green wire", "#3aa655"),
        ("Waiting", "screen: “hold your\npalm” — sensor\nwatches for a hand", "#457b9d"),
        ("Palm seen", "board asks VERIFY\non the yellow wire", "#f4c20d"),
        ("Answer", "sensor replies:\nwho + score\n(about 1 second)", "#3aa655"),
        ("Match", "green LED · 1 beep\n“Welcome, <name>”\nbolt pulled for 5 s", "#2a9d8f"),
        ("No match", "red LED · 2 beeps\n“Not recognised”", "#d62828"),
    ]
    x0, y0, w, gap = 14, 52, 118, 8
    o += line(x0, y0 + 30, x0 + 7 * (w + gap) - gap, y0 + 30, stroke="#bbb", sw=2, extra='marker-end="url(#arrowMuted)"')
    for i, (title, sub, col) in enumerate(steps):
        x = x0 + i * (w + gap)
        o += circle(x + w / 2, y0 + 30, 9, fill=col, stroke="#fff", sw=2)
        o += rrect(x, y0 + 60, w, 104, r=8, fill="#fafafa", stroke="#ddd", sw=1)
        o += rrect(x, y0 + 60, w, 6, r=3, fill=col, stroke="none")
        o += text(x + w / 2, y0 + 88, title, size=12.5, weight=700, anchor="middle")
        for j, ln in enumerate(sub.split("\n")):
            o += text(x + w / 2, y0 + 110 + j * 15, ln, size=10.2, fill=LABEL, anchor="middle")
    o += path(f"M{x0 + 5 * (w + gap) + w / 2},{y0 + 164} v18", stroke="#2a9d8f", sw=2)
    o += path(f"M{x0 + 6 * (w + gap) + w / 2},{y0 + 164} v18", stroke="#d62828", sw=2)
    o += text(x0 + 5 * (w + gap) + w / 2, y0 + 196, "→ back to Waiting", size=10, fill=MUTED, anchor="middle")
    o += text(x0 + 6 * (w + gap) + w / 2, y0 + 196, "→ back to Waiting", size=10, fill=MUTED, anchor="middle")
    o += text(14, 28, "One scan, start to finish", size=14, weight=700)
    return frame(W, 262, o)


if __name__ == "__main__":
    import sys
    fn = sys.argv[1]
    sys.stdout.write(globals()[fn]())


# ------------------------------------------------------------------ 5. part icons
def icon(kind: str) -> str:
    """A small 'what it looks like' picture for the parts table (64×40 viewBox)."""
    o = ""
    if kind == "module":
        o += rrect(6, 4, 52, 32, r=2, fill="#cfd3d7", stroke="#6a6f74", sw=0.8)
        o += rrect(6, 4, 52, 8, r=2, fill="#0f3a25", stroke="none")
        o += path("M10,10 h4 v-3 h4 v3 h4 v-3 h4 v3 h4 v-3 h4 v3 h4 v-3 h4 v3 h4 v-3 h4 v3", stroke=COPPER, sw=1)
        o += rrect(10, 15, 44, 18, r=1, fill="url(#gMetal)", stroke="#5c6166", sw=0.6)
    elif kind == "regulator":
        o += rrect(14, 4, 36, 24, r=2, fill="#1b1b1b", stroke="#000", sw=0.7)
        o += mono(32, 19, "R-78E", size=7, fill="#fff", anchor="middle", weight=700)
        for i in range(3):
            o += rrect(21 + i * 10, 28, 3, 8, r=0.5, fill=METAL, stroke="none")
    elif kind == "fuse":
        o += rrect(14, 12, 36, 16, r=1.5, fill="#e8dcc0", stroke="#8a7a50", sw=0.7)
        o += rrect(14, 12, 7, 16, r=1, fill=METAL, stroke="none")
        o += rrect(43, 12, 7, 16, r=1, fill=METAL, stroke="none")
    elif kind == "diode":
        o += rrect(14, 12, 36, 16, r=1.5, fill="#151515", stroke="#000", sw=0.7)
        o += rrect(14, 12, 6, 16, r=1, fill=METAL, stroke="none")
        o += rrect(44, 12, 6, 16, r=1, fill=METAL, stroke="none")
        o += rrect(22, 12, 4, 16, r=0, fill="#eee", stroke="none")
    elif kind == "cap_big":
        o += electrolytic(32, 20, r=15, label="470µ")
    elif kind == "cap_small":
        o += electrolytic(32, 20, r=11, label="100µ")
    elif kind == "ceramics":
        for i, w in enumerate((10, 14, 18)):
            o += rrect(8 + i * 18, 20 - w / 4, w, w / 2, r=0.8, fill="#c8b48a", stroke="#7a6a45", sw=0.5)
    elif kind == "mosfet":
        o += rrect(20, 8, 24, 20, r=1.5, fill="#151515", stroke="#000", sw=0.7)
        for x in (24, 38):
            o += rrect(x, 28, 3, 6, r=0.4, fill=METAL, stroke="none")
        o += rrect(31, 2, 3, 6, r=0.4, fill=METAL, stroke="none")
    elif kind == "esd":
        o += rrect(20, 8, 24, 20, r=1.5, fill="#151515", stroke="#000", sw=0.7)
        for x in (23, 31, 39):
            o += rrect(x, 28, 3, 6, r=0.4, fill=METAL, stroke="none")
            o += rrect(x, 2, 3, 6, r=0.4, fill=METAL, stroke="none")
    elif kind == "resistor":
        o += rrect(16, 14, 32, 12, r=1, fill="#222", stroke="#000", sw=0.6)
        o += rrect(16, 14, 6, 12, r=0.8, fill=METAL, stroke="none")
        o += rrect(42, 14, 6, 12, r=0.8, fill=METAL, stroke="none")
        o += mono(32, 24, "103", size=7, fill="#ddd", anchor="middle")
    elif kind == "buzzer":
        o += buzzer(32, 20, r=16)
    elif kind == "buttons":
        o += tact_button(10, 10, size=18)
        o += tact_button(36, 10, size=18)
    elif kind == "led":
        o += led_0603(26, 16, "#f4c20d")
        o += circle(29, 18, 9, fill="#f4c20d", stroke="none", extra='fill-opacity="0.25"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 40" width="64" height="40" '
            f'style="display:block">{defs()}{o}</svg>')
