"""The fold-out master wiring diagram (A3 landscape).

Everything a person plugs into the palm-scan board, drawn as the physical
objects with real wire colours. Numbered badges ①–⑧ match the section numbers
in the guide. Board component positions are illustrative — the PCB layout is a
later phase — but every connector, pin and wire is taken from docs/NETLIST.md.
"""

from parts import *  # noqa: F401,F403

W, H = 1500, 1040

# Board rectangle
BX, BY, BW, BH = 470, 300, 560, 440


def board() -> str:
    o = rrect(BX, BY, BW, BH, r=10, fill="url(#gBoard)", stroke=BOARD_EDGE, sw=2.2, extra='filter="url(#shadow)"')
    # copper ground pour hint + silkscreen border
    o += rrect(BX + 10, BY + 10, BW - 20, BH - 20, r=6, fill="none", stroke=SILK, sw=0.8, extra='stroke-opacity="0.6"')
    for (hx, hy) in ((BX + 16, BY + 16), (BX + BW - 16, BY + 16), (BX + 16, BY + BH - 16), (BX + BW - 16, BY + BH - 16)):
        o += circle(hx, hy, 5.5, fill=PAPER, stroke=COPPER, sw=2.2)
    o += text(BX + 26, BY + BH - 30, "palm-scan · Rev 2.4", size=9, weight=700, fill=SILK, anchor="start")
    return o


def silk(x, y, s, size=8.5, anchor="middle", weight=700) -> str:
    return text(x, y, s, size=size, weight=weight, fill=SILK, anchor=anchor)


def plain(x, y, s, size=8, anchor="middle") -> str:
    """Plain-words caption on the board, under the silkscreen name."""
    return text(x, y, s, size=size, weight=400, fill="#cfe8d8", anchor=anchor, italic=True)


def on_board() -> str:
    o = ""
    # --- ESP32 module, antenna on the top edge (keep-out hatch around it)
    mx, my = 700, BY + 2
    o += rrect(mx - 14, my, 146, 30, r=4, fill="url(#hatch)", stroke="none")
    o += esp32_module(mx, my)
    o += silk(mx + 59, my + 98, "U1")
    o += plain(mx + 59, my + 109, "the brain — runs everything")

    # --- Display header J4 (14-pin female) on the top edge, left of the module
    o += pin_header(482, BY + 4, 14, pitch=9, female=True, numbers=True, num_side="below", label_only={1, 14})
    o += rrect(486, BY + 7.5, 5, 5, r=0, fill="none", stroke=SILK, sw=0.9)   # square pad marks pin 1
    o += silk(547, BY + 40, "J4  DISPLAY")
    o += plain(547, BY + 51, "screen plugs straight in")

    # --- power entry: J8 barrel + J1 screw terminal on the left edge
    o += barrel_jack(BX - 6, 340, facing="left")
    o += silk(BX + 12, 382, "J8  12 V IN", anchor="start")
    o += screw_terminal(BX + 2, 398, n=2, pitch=18, facing="left")
    o += mono(BX + 27, 410, "1 +", size=8, fill=SILK)
    o += mono(BX + 27, 428, "2 −", size=8, fill=SILK)
    o += silk(BX + 48, 421, "J1  12 V IN (alt.)", anchor="start")

    # protection chain: F1 fuse, D1 one-way diode, D7 surge clamp
    o += smd_chip(600, 372, 22, 12, "F1")
    o += smd_chip(630, 372, 22, 12, "D1")
    o += smd_chip(660, 372, 22, 12, "D7")
    o += path("M622,378 h8 M652,378 h8", stroke=COPPER, sw=1.6)
    o += plain(641, 396, "fuse · one-way valve · surge clamp", size=7.5)

    # bulk capacitor C1 + the two regulators
    o += electrolytic(600, 425, r=14, label="470µ")
    o += silk(600, 452, "C1")
    o += plain(600, 463, "energy tank", size=7.5)
    o += sip_regulator(505, 480, "3.3 V")
    o += silk(525, 526, "U2")
    o += plain(525, 537, "12 V → 3.3 V", size=7.5)
    o += sip_regulator(560, 480, "5.0 V")
    o += silk(580, 526, "U3")
    o += plain(580, 537, "12 V → 5 V (sensor)", size=7.5)
    o += led_0603(640, 484, "#f4c20d")
    o += silk(643, 500, "D4", size=7.5)
    o += plain(643, 510, "power light", size=7)

    # --- USB-C on the left edge bottom, with its ESD guard D3
    o += usb_c(BX - 4, 660, facing="left")
    o += silk(BX + 30, 669, "J2  USB-C", anchor="start")
    o += smd_chip(BX + 92, 662, 18, 10, "D3")
    o += plain(BX + 101, 685, "static guard", size=7.5)

    # --- sensor socket CN1 on the right edge top (vertical 4-pin)
    o += picoblade(BX + BW - 16, 330, n=4, pitch=8, vertical=True)
    for i, n in enumerate("1234"):
        o += mono(BX + BW - 22, 341 + i * 8, n, size=7.5, fill=SILK, anchor="end")
    o += silk(BX + BW - 30, 328, "CN1  SENSOR", anchor="end")
    o += electrolytic(BX + BW - 60, 380, r=10, label="100µ")
    o += silk(BX + BW - 60, 400, "C12", size=7.5)

    # --- panel LED header J7 on the right edge middle (vertical 3-pin)
    o += pin_header(BX + BW - 14, 470, 3, pitch=9, vertical=True, numbers=True, num_side="left")
    o += silk(BX + BW - 30, 466, "J7  PANEL LEDS", anchor="end")
    o += smd_chip(BX + BW - 70, 476, 14, 8, "R9")
    o += smd_chip(BX + BW - 70, 490, 14, 8, "R10")

    # --- lock terminal J3 on the right edge bottom, with switch Q1 and flyback D2
    o += screw_terminal(BX + BW - 22, 612, n=2, pitch=18, facing="right")
    o += mono(BX + BW - 40, 624, "1 +12", size=7.5, fill=SILK, anchor="end")
    o += mono(BX + BW - 40, 642, "2 SW", size=7.5, fill=SILK, anchor="end")
    o += silk(BX + BW - 30, 608, "J3  LOCK", anchor="end")
    o += smd_chip(922, 656, 20, 12, "D2")
    o += smd_chip(952, 656, 16, 12, "Q1")
    o += plain(945, 680, "kick-back diode · electronic switch", size=7.5)

    # --- bottom edge: J5 exit button terminal, J6 debug header
    o += f'<g transform="translate(600,{BY + BH - 22}) rotate(-90)">' + screw_terminal(0, 0, n=2, pitch=18, facing="left") + "</g>"
    o += silk(618, BY + BH - 48, "J5  EXIT")
    o += pin_header(800, BY + BH - 16, 4, pitch=9, numbers=True, num_side="above")
    o += silk(820, BY + BH - 22, "J6  DEBUG")

    # --- reset / boot buttons, buzzer
    o += tact_button(840, 580)
    o += silk(847, 606, "S1", size=7.5)
    o += plain(847, 616, "reset", size=7)
    o += tact_button(872, 580)
    o += silk(879, 606, "S2", size=7.5)
    o += plain(879, 616, "boot", size=7)
    o += buzzer(760, 560, r=15)
    o += silk(760, 588, "BZ1")
    o += plain(760, 599, "beeper", size=7.5)
    return o


def off_board() -> str:
    o = ""
    # ---------------- ① wall adapter → J8
    o += wall_adapter(100, 300)
    o += wire("M254,347 C300,347 330,353 375,353", "#2b2b2b", width=6)
    o += barrel_plug(378, 353, facing="right")
    o += line(418, 353, BX - 14, 353, stroke="#333", sw=1, extra='stroke-dasharray="2 3"')
    o += callout(300, 320, 1)
    o += label_lines(60, 425, ["Power in — 12 V from the wall adapter.",
                               "Plug goes into J8. Centre of the plug is ⊕."], size=10.5)
    # alternative: bare wires into J1
    o += wire("M395,409 L462,409", WIRE["12V"], width=4)
    o += wire("M395,427 L462,427", WIRE["GND"], width=4)
    o += text(390, 413, "+", size=11, weight=700, anchor="end")
    o += text(390, 431, "−", size=11, weight=700, anchor="end")
    o += text(458, 452, "…or bare wires into J1 (never both)", size=9.5, fill=MUTED, italic=True, anchor="end")

    # ---------------- ⑦ laptop → USB-C
    o += laptop(100, 600)
    o += wire("M254,650 C320,650 330,666 440,666", WIRE["USB"], width=5.5)
    o += rrect(438, 660, 26, 12, r=5, fill="url(#gMetal)", stroke="#4d5257", sw=0.9)
    o += callout(330, 630, 7)
    o += label_lines(60, 725, ["Programming & logs — USB-C to a laptop.",
                               "Only used by the person maintaining it."], size=10.5)

    # ---------------- ③ display → J4 (plugs straight down)
    o += display_module(440, 80, header_side="bottom")
    for i in range(14):
        px = 488.5 + i * 9
        o += line(px, 230, px, BY + 6, stroke=COPPER, sw=2.6)
        o += line(px, 230, px, BY + 6, stroke="#7a5a12", sw=0.6)
    o += callout(668, 200, 3)
    o += label_lines(690, 176, ["Touch screen — 14 pins, plugs directly into J4.",
                               "No loose wires. Pin 1 must line up with pin 1.",
                               "Runs on 3.3 V: power, backlight, and 12 data lines."], size=10.5)

    # ---------------- ② sensor → CN1 (sheathed 4-wire cable)
    o += sensor_module(1190, 120, conn_side="left")
    sheath = "M1150,153 C1090,153 1080,230 1060,290 C1052,315 1048,330 1046,346"
    o += wire(sheath, "#8a8f94", width=11)
    # fan-out at the board end, real DFRobot colours: 1 black, 2 yellow, 3 green, 4 red
    ys = (336, 344, 352, 360)
    cols = (WIRE["GND"], WIRE["YEL"], WIRE["GRN"], WIRE["12V"])
    for y, c in zip(ys, cols):
        o += wire(f"M1046,346 C1040,{y} 1036,{y} {BX + BW + 2},{y}", c, width=3.2)
    # fan-out at the sensor end
    for i, c in enumerate(cols):
        y = 145 + i * 5.5
        o += wire(f"M1150,153 C1165,153 1170,{y} 1184,{y}", c, width=3.2)
    o += callout(1120, 250, 2)
    o += label_lines(1180, 205, ["Palm-vein sensor — 4-wire cable, colours as supplied:",
                               "black = ground · red = 5 V power",
                               "yellow = board → sensor · green = sensor → board",
                               "Plugs into CN1."], size=10.5)

    # ---------------- ⑥ panel LEDs → J7
    o += led_5mm(1280, 470, "#3aa655")
    o += text(1280, 445, "recognised", size=9, fill=MUTED, anchor="middle")
    o += led_5mm(1340, 470, "#d62828")
    o += text(1340, 445, "not recognised", size=9, fill=MUTED, anchor="middle")
    # J7: pin1 GND (y≈480), pin2 green anode (489), pin3 red anode (498)
    jx = BX + BW + 2
    p1, p2, p3 = 476.5, 485.5, 494.5
    # lanes: black (both short legs) on top, green anode, red anode
    o += wire(f"M1284,494 V512 H1344 V494", WIRE["GND"], width=3)                     # cathodes joined
    o += wire(f"M1300,512 H1090 C1070,512 1070,{p1} {jx},{p1}", WIRE["GND"], width=3) # → pin 1
    o += wire(f"M1276,500 V524 H1090 C1070,524 1070,{p2} {jx},{p2}", WIRE["GRN"], width=3)   # → pin 2
    o += wire(f"M1336,500 V536 H1090 C1070,536 1070,{p3} {jx},{p3}", "#d62828", width=3)     # → pin 3
    o += callout(1210, 535, 6)
    o += label_lines(1180, 580, ["Front-panel lights — two ordinary 5 mm LEDs on wires.",
                               "Long leg (+) to J7 pin 2 (green) / pin 3 (red); short legs to pin 1."], size=10.5)

    # ---------------- ④ solenoid → J3
    o += solenoid_lock(1190, 640)
    jx3 = BX + BW
    o += wire(f"M1190,672 C1120,672 1100,621 {jx3},621", WIRE["12V"], width=4.5)
    o += wire(f"M1190,690 C1120,690 1100,639 {jx3},639", "#e8e8e8", width=4.5)
    o += callout(1120, 700, 4)
    o += label_lines(1180, 760, ["Door release — 12 V solenoid bolt, 2 wires, no polarity.",
                               "One wire to J3 pin 1 (+12 V), the other to pin 2 (switched).",
                               "The board turns it on for at most 5 seconds at a time."], size=10.5)

    # ---------------- ⑤ exit button → J5 (bottom edge)
    o += push_button(640, 900)
    o += wire(f"M620,868 C620,820 609,800 609,{BY + BH + 4}", "#e8e8e8", width=4)
    o += wire(f"M660,868 C660,820 627,800 627,{BY + BH + 4}", WIRE["GND"], width=4)
    o += callout(700, 830, 5)
    o += label_lines(700, 880, ["Exit button — any push button,",
                               "2 wires, no polarity. Opens the",
                               "lock from inside without a scan."], size=10.5)

    # ---------------- ⑧ debug header (optional)
    o += usb_serial_dongle(960, 900)
    cols8 = (WIRE["3V3"], WIRE["GRN"], "#e8e8e8", WIRE["GND"])
    for i, c in enumerate(cols8):
        px = 804.5 + i * 9
        o += wire(f"M{px},{BY + BH + 2} C{px},800 {970 + i * 14},860 {970 + i * 14},900", c, width=2.6, dash="6 4")
    o += callout(900, 830, 8)
    o += label_lines(1040, 912, ["Debug header — only if USB ever stops working.",
                               "Dashed = optional. Normally nothing is connected here."], size=10.5)
    return o


def title_block() -> str:
    o = text(40, 62, "palm-scan", size=34, weight=900)
    o += text(40, 90, "Complete wiring — what plugs into what, and why", size=15, weight=400, fill=LABEL)
    o += text(40, 112, "Controller board Rev 2.4  ·  September 2026", size=10.5, fill=MUTED)
    o += text(40, 128, "Fold-out sheet — read together with Sections 4.1 – 4.8", size=10.5, fill=MUTED)
    return o


def legend() -> str:
    x, y, w = 40, 770, 380
    o = rrect(x, y, w, 262, r=8, fill="#fafafa", stroke="#d0d0d0", sw=1)
    o += text(x + 14, y + 24, "How to read this sheet", size=13, weight=700)
    rows = [
        (WIRE["12V"], "red wire", "12 V power, positive (+)"),
        (WIRE["5V"], "orange", "5 V power (sensor only)"),
        (WIRE["3V3"], "yellow-gold", "3.3 V power (screen, debug header)"),
        (WIRE["GND"], "black", "ground — the shared return path (−)"),
        ("pair", "yellow / green", "sensor cable data: to sensor / from sensor"),
        ("#8a8f94", "grey sheath", "several wires bundled inside one cable"),
        ("#e8e8e8", "white", "switched line — a wire the board turns on or off"),
        (WIRE["USB"], "purple", "USB cable"),
    ]
    for i, (c, name, meaning) in enumerate(rows):
        yy = y + 46 + i * 20
        if c == "pair":
            o += wire(f"M{x + 14},{yy} L{x + 32},{yy}", WIRE["YEL"], width=4.5)
            o += wire(f"M{x + 36},{yy} L{x + 54},{yy}", WIRE["GRN"], width=4.5)
        elif c == "#8a8f94":
            o += wire(f"M{x + 14},{yy} L{x + 54},{yy}", c, width=9)
        else:
            o += wire(f"M{x + 14},{yy} L{x + 54},{yy}", c, width=4.5)
        o += text(x + 64, yy + 4, name, size=10.5, weight=700)
        o += text(x + 160, yy + 4, meaning, size=10.5, fill=LABEL)
    yy = y + 46 + len(rows) * 20 + 4
    o += callout(x + 24, yy + 6, "n", r=11)
    o += text(x + 44, yy + 10, "Numbered badge = section 4.n in the guide explains that cable", size=10.5, fill=LABEL)
    o += mono(x + 14, yy + 34, "J8  CN1  1 2 3", size=10.5, fill=INK, weight=700)
    o += text(x + 120, yy + 34, "names and pin numbers printed on the board itself", size=10.5, fill=LABEL)
    return o


def footer_note() -> str:
    return note_box(1100, 972, 360, [
        "Board drawing is illustrative: connector positions will be fixed",
        "during PCB layout. Pins, names and wire colours are exact."],
        size=9.5, title="Note")


def svg() -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" '
        f'style="font-family:{SANS}">',
        defs(),
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>',
        title_block(),
        board(),
        on_board(),
        off_board(),
        legend(),
        footer_note(),
        "</svg>",
    ]
    return "".join(parts)


if __name__ == "__main__":
    import sys
    sys.stdout.write(svg())
