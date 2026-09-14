#!/usr/bin/env python3
"""Build the palm-scan Wiring & Components Guide (HTML → PDF).

    python3 build.py            # writes wiring-guide.html and ../palm-scan-wiring-guide.pdf

Two render passes: the first finds which page each heading lands on, the second
fills those numbers into the contents page. Needs the Playwright Chromium that
lives in ~/.cache/ms-playwright (any recent Chrome/Chromium works: set CHROME=...).
"""

from __future__ import annotations

import html
import os
import re
import subprocess
from pathlib import Path

import cards
import master

HERE = Path(__file__).parent
OUT_HTML = HERE / "wiring-guide.html"
OUT_PDF = HERE.parent / "palm-scan-wiring-guide.pdf"
CHROME = os.environ.get("CHROME") or next(
    iter(sorted(Path.home().glob(".cache/ms-playwright/chromium-*/chrome-linux64/chrome"))), None)

DOC_TITLE = "palm-scan · Wiring & Components Guide"
REV = "Controller board Rev 2.4 · Guide rev A · 14 September 2026"

# ----------------------------------------------------------------------------- CSS
CSS = r"""
@page { size: A4 portrait; margin: 22mm 20mm 24mm 20mm;
  @top-left { content: "palm-scan · Wiring & Components Guide"; font-family: Lato; font-size: 8.5pt; color: #777; letter-spacing: .02em; }
  @top-right { content: "Rev 2.4"; font-family: Lato; font-size: 8.5pt; color: #777; }
  @bottom-center { content: counter(page); font-family: Lato; font-size: 9pt; color: #555; } }
@page cover { margin: 0; @top-left { content: none } @top-right { content: none } @bottom-center { content: none } }
@page wide  { size: A3 landscape; margin: 10mm 12mm 12mm 12mm;
  @top-left { content: "palm-scan · Wiring & Components Guide · Section 3 — complete wiring diagram"; font-family: Lato; font-size: 8.5pt; color: #777; }
  @top-right { content: "Rev 2.4"; font-family: Lato; font-size: 8.5pt; color: #777; } }

:root { --ink:#1c1c1c; --navy:#1f3a5f; --muted:#6b6b6b; --rule:#d9d9d9; --amber:#b7791f; --amberbg:#fff8e6; --eng:#f3f5f8; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: P052, "TeX Gyre Pagella", Palatino, "Liberation Serif", serif; font-size: 10.2pt; line-height: 1.45; color: var(--ink); margin: 0; }
section.page { break-after: page; }
section.cover { page: cover; break-after: page; }
section.wide { page: wide; break-after: page; }

h1, h2, h3, h4, .sans { font-family: Lato, "Liberation Sans", sans-serif; }
h1 { font-size: 22pt; font-weight: 800; letter-spacing: -.01em; margin: 0 0 4mm; padding-bottom: 2mm; border-bottom: 1.5pt solid var(--navy); break-after: avoid; }
h1 .num { color: var(--navy); margin-right: 3mm; }
h2 { font-size: 14pt; font-weight: 700; margin: 6mm 0 2mm; break-after: avoid; }
h2 .num { color: var(--navy); margin-right: 2.5mm; }
h3 { font-size: 11pt; font-weight: 700; margin: 5mm 0 1.5mm; text-transform: uppercase; letter-spacing: .06em; color: #333; break-after: avoid; }
p { margin: 0 0 2.6mm; text-align: left; orphans: 3; widows: 3; }
p.lead { font-size: 12pt; line-height: 1.5; color: #222; }
ul, ol { margin: 0 0 3mm; padding-left: 6mm; }
li { margin-bottom: 1.2mm; }
strong { font-weight: 700; }
code, .mono { font-family: "Ubuntu Mono", "DejaVu Sans Mono", monospace; font-size: 9.6pt; background: #f2f2f2; padding: 0 .25em; border-radius: 2px; }
small, .small { font-size: 9pt; color: var(--muted); }

figure { margin: 2mm 0 3.5mm; break-inside: avoid; }
figure.card { width: 80%; margin-left: auto; margin-right: auto; }
figure svg { display: block; width: 100%; height: auto; }
figcaption { font-family: Lato; font-size: 8.8pt; color: var(--muted); margin-top: 1.5mm; line-height: 1.35; }
figcaption b { color: #333; font-weight: 700; }
figure.half { width: 62%; margin-left: auto; margin-right: auto; }
figure.w85 { width: 85%; margin-left: auto; margin-right: auto; }

table { border-collapse: collapse; width: 100%; font-family: Lato; font-size: 8.8pt; margin: 1.5mm 0 3mm; break-inside: auto; }
th { text-align: left; font-weight: 700; color: var(--navy); border-bottom: 1.2pt solid var(--navy); padding: 1.4mm 1.6mm; vertical-align: bottom; }
td { border-bottom: .5pt solid var(--rule); padding: 1.1mm 1.6mm; vertical-align: top; }
tr { break-inside: avoid; }
table.keep { break-inside: avoid; }
td.nw { white-space: nowrap; }
td.ic { width: 14mm; padding-top: 1mm; } td.ic svg { width: 14mm; height: auto; }
th.w-ref { width: 9mm; } th.w-ic { width: 14mm; } th.w-part { width: 24mm; }
table.dense { font-size: 8.3pt; } table.dense td { padding: .9mm 1.4mm; }
h2.newpage { break-before: page; margin-top: 0; }
td.c, th.c { text-align: center; }
td.m { font-family: "Ubuntu Mono", monospace; font-size: 9.2pt; white-space: nowrap; }
.sw { display: inline-block; width: 22px; height: 8px; border-radius: 4px; border: 1px solid #333; vertical-align: middle; margin-right: 4px; }

.eng { background: var(--eng); border-left: 3pt solid var(--navy); padding: 2mm 3.5mm 1.6mm; margin: 2.5mm 0 3mm; font-size: 9.2pt; line-height: 1.4; break-inside: avoid; }
.eng .tag, .warn .tag, .plain .tag { font-family: Lato; font-size: 7.6pt; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; display: block; margin-bottom: 1mm; }
.eng .tag { color: var(--navy); }
.warn { background: var(--amberbg); border-left: 3pt solid var(--amber); padding: 2mm 3.5mm 1.6mm; margin: 2.5mm 0 3mm; font-size: 9.5pt; line-height: 1.4; break-inside: avoid; }
.warn ul, .eng ul { margin-bottom: 1mm; } .warn li { margin-bottom: .6mm; }
.warn .tag { color: var(--amber); }
.plain { border: .6pt solid var(--rule); border-radius: 2mm; padding: 2mm 3.5mm 1.6mm; margin: 2.5mm 0 3mm; break-inside: avoid; }
.plain .tag { color: #2f8f4e; }
.badge { display: inline-block; font-family: Lato; font-weight: 700; font-size: 8.5pt; color: #fff; background: var(--navy); border-radius: 50%; width: 5.2mm; height: 5.2mm; line-height: 5.2mm; text-align: center; margin-right: 1.5mm; vertical-align: middle; }
.cols2 { column-count: 2; column-gap: 8mm; }
.kv { display: grid; grid-template-columns: 34mm 1fr; gap: 1mm 4mm; font-size: 10pt; margin: 2mm 0 4mm; }
.kv b { font-family: Lato; font-size: 9pt; color: var(--navy); }
.check li { list-style: none; position: relative; padding-left: 7mm; }
.check li::before { content: ""; position: absolute; left: 0; top: 1.2mm; width: 3.6mm; height: 3.6mm; border: 1pt solid #333; border-radius: .6mm; }

/* cover */
.cover-inner { height: 297mm; box-sizing: border-box; padding: 26mm 22mm 20mm; display: flex; flex-direction: column; background: #fff; }
.cover-inner .kicker { font-family: Lato; font-size: 10pt; letter-spacing: .22em; text-transform: uppercase; color: var(--navy); }
.cover-inner .title { font-family: Lato; font-size: 46pt; font-weight: 900; letter-spacing: -.02em; line-height: 1; margin: 6mm 0 2mm; }
.cover-inner .sub { font-family: Lato; font-size: 17pt; font-weight: 300; color: #333; margin-bottom: 10mm; }
.cover-inner img { width: 100%; border-radius: 3mm; }
.cover-inner .foot { margin-top: auto; display: grid; grid-template-columns: 1fr 1fr; font-family: Lato; font-size: 9.5pt; color: #444; line-height: 1.6; border-top: 1pt solid var(--navy); padding-top: 4mm; }
.cover-inner .foot b { color: var(--navy); font-weight: 700; display: block; font-size: 8pt; letter-spacing: .12em; text-transform: uppercase; }

/* contents */
.toc { font-family: Lato; font-size: 10.5pt; }
.toc div { display: flex; align-items: baseline; margin: 1.2mm 0; }
.toc div.l2 { padding-left: 8mm; font-size: 9.8pt; color: #333; }
.toc .t { white-space: nowrap; }
.toc .dots { flex: 1; border-bottom: 1px dotted #999; margin: 0 2mm; position: relative; top: -3px; }
.toc .pg { width: 8mm; text-align: right; color: var(--navy); font-weight: 700; }

/* wide page */
.wide-inner { width: 100%; height: 100%; }
.wide-inner svg { width: 100%; height: auto; display: block; }
"""

# ----------------------------------------------------------------------------- helpers
def h(s: str) -> str:
    return html.escape(s, quote=False)


def swatch(color: str) -> str:
    return f'<span class="sw" style="background:{color}"></span>'


def table(headers, rows, cls="keep"):
    th = ""
    for x in headers:
        t, c = x if isinstance(x, tuple) else (x, None)
        th += f'<th class="{c}">{t}</th>' if c else f"<th>{t}</th>"
    body = ""
    for r in rows:
        tds = ""
        for cell in r:
            if isinstance(cell, tuple):
                tds += f'<td class="{cell[1]}">{cell[0]}</td>'
            else:
                tds += f"<td>{cell}</td>"
        body += f"<tr>{tds}</tr>"
    open_tag = f'<table class="{cls}">' if cls else "<table>"
    return f"{open_tag}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>"


def fig(svg: str, caption: str, half=False, cls="") -> str:
    open_tag = f'<figure class="{cls}">' if cls else ('<figure class="half">' if half else "<figure>")
    return f"{open_tag}{svg}<figcaption>{caption}</figcaption></figure>"


def eng(body: str) -> str:
    return f'<div class="eng"><span class="tag">For the engineer</span>{body}</div>'


def warn(body: str, tag="Before you connect it") -> str:
    return f'<div class="warn"><span class="tag">{tag}</span>{body}</div>'


def plain(body: str, tag="In plain words") -> str:
    return f'<div class="plain"><span class="tag">{tag}</span>{body}</div>'


TOC_ENTRIES: list[tuple[str, str, int]] = []   # (id, title, level)


def H1(id_, num, title):
    TOC_ENTRIES.append((id_, f"{num}  {title}", 1))
    return f'<h1 id="{id_}"><span class="num">{num}</span>{title}</h1>'


def H2(id_, num, title, newpage=False):
    TOC_ENTRIES.append((id_, f"{num}  {title}", 2))
    cls = ' class="newpage"' if newpage else ""
    return f'<h2 id="{id_}"{cls}><span class="num">{num}</span>{title}</h2>'


C = {"12V": "#d62828", "5V": "#f77f00", "3V3": "#e9c46a", "GND": "#222", "YEL": "#f4c20d",
     "GRN": "#3aa655", "WHT": "#e8e8e8", "USB": "#6a4c93", "RED": "#d62828"}

# ----------------------------------------------------------------------------- content
def cover() -> str:
    return f"""
<section class="cover"><div class="cover-inner">
  <div class="kicker">Palm-vein recognition · hardware documentation</div>
  <div class="title">palm-scan</div>
  <div class="sub">Wiring &amp; Components Guide — every connection, explained for everyone</div>
  <img src="../images/enclosure-labeled.png" alt="palm-scan enclosure concept">
  <div class="foot">
    <div><b>Applies to</b>Controller board Rev 2.4 (schematic verified 14 Sep 2026)<br>DFRobot AI10 palm-vein sensor · 2.4″ TFT touch display · 12 V solenoid</div>
    <div><b>Makers</b>Ashmita K Rao · Adithya Satish · Vinod Kumar<br>github.com/coolvnod/palm-scan</div>
  </div>
</div></section>"""


def contents(pages: dict[str, int] | None) -> str:
    rows = ""
    for id_, title, lvl in TOC_ENTRIES:
        pg = pages.get(id_, "") if pages else ""
        rows += f'<div class="{"l2" if lvl == 2 else ""}"><span class="t">{h(title)}</span><span class="dots"></span><span class="pg">{pg}</span></div>'
    return f"""
<section class="page">
  <h1>Contents</h1>
  <div class="toc">{rows}</div>
  <p class="small" style="margin-top:8mm">Section 3 is an A3 fold-out. If you print on A4, print that page at “fit to page” — or read it on a screen, where you can zoom.</p>
</section>"""


def sec1() -> str:
    legend_rows = [
        (swatch(C["12V"]) + " red", "12 V power, the positive (+) side", "adapter → board, board → lock"),
        (swatch(C["5V"]) + " orange", "5 V power", "regulator → sensor (inside the board)"),
        (swatch(C["3V3"]) + " yellow-gold", "3.3 V power", "board → screen, debug header"),
        (swatch(C["GND"]) + " black", "ground — the shared return path, the “−” side", "every cable has one"),
        (swatch(C["YEL"]) + " yellow", "data: the board talking to the sensor", "sensor cable"),
        (swatch(C["GRN"]) + " green", "data: the sensor talking to the board", "sensor cable"),
        (swatch(C["WHT"]) + " white", "a switched line — the board turns it on or off", "lock, exit button"),
        (swatch(C["USB"]) + " purple", "USB", "laptop cable"),
        (swatch("#8a8f94") + " grey", "a sheath with several wires inside", "sensor cable"),
    ]
    gloss = [
        ("Voltage (V)", "How hard electricity is being pushed — like water pressure. 12 V pushes harder than 3.3 V. Every part has a voltage it expects; too much breaks it."),
        ("Current (A)", "How much electricity is flowing — like litres per minute. The adapter can supply 2 A; the board never needs more than about 1.2 A."),
        ("Ground (GND, −)", "The common “zero level” every voltage is measured against, and the path electricity takes back. Every cable carries one ground wire."),
        ("Rail", "A shared supply line at one voltage. The board has three: +12 V, +5 V and +3.3 V."),
        ("Signal", "A wire that carries information instead of power. Tiny currents, but the timing matters."),
        ("Pin", "One metal contact in a connector. Pins are numbered; pin 1 is usually marked with a square, a dot or an arrow."),
        ("Polarity", "Which way round. Power and LEDs have a + and a −; a button and the solenoid don’t care."),
        ("UART", "A two-wire conversation: one wire for each direction, at an agreed speed. The sensor talks to the board this way."),
        ("SPI", "A faster, four-wire conversation with a shared clock — used for the screen."),
        ("GPIO", "A pin on the brain that the software can switch on or off, or read. The lock, buzzer, LEDs and button all sit on GPIOs."),
    ]
    return f"""
<section class="page">
  {H1("s1", "1", "How to read this guide")}
  <p class="lead">This guide shows every wire and every part of the palm-scan controller, and says what each one is for — in ordinary words first, and in engineering terms for those who want them.</p>
  <p>You do not need to know electronics. Three things are enough: a wire carries either <em>power</em> or <em>information</em>; power has a <em>+</em> side and a <em>−</em> side; and every connector has numbered <em>pins</em>. Everything else is explained where it comes up.</p>
  <p>The guide has three layers, marked like this:</p>
  {plain("Ordinary-language explanation. If you only read these, you can still wire the unit correctly.")}
  {eng("Precise engineering detail — part numbers, voltages, currents, and the reasoning behind a choice. Skip freely.")}
  {warn("Something to check or avoid <em>before</em> plugging in. These are the paragraphs that save hardware.")}

  <h2>Wire colours used in the drawings</h2>
  <p>Colours in this guide follow what you will actually see: the sensor cable comes with its wires already coloured by the maker, and the rest follow the usual convention of red for +, black for −.</p>
  {table(["Colour", "Meaning", "Where you will see it"], legend_rows)}

  <h2>Ten words</h2>
  {table(["Word", "What it means here"], gloss)}
</section>"""


def sec2() -> str:
    items = [
        (("<span class='badge'>1</span>Wall adapter", "nw"), "Supplies all the power: 12 V, up to 2 A.", "J8 (round plug) or J1 (bare wires)"),
        (("<span class='badge'>2</span>Palm-vein sensor", "nw"), "The eye. Shines near-infrared light, photographs the veins, decides who it is.", "CN1 — 4-wire cable, supplied with the sensor"),
        (("<span class='badge'>3</span>Touch screen", "nw"), "Shows what is happening; used to add or remove people.", "J4 — plugs straight onto the board, no cable"),
        (("<span class='badge'>4</span>Solenoid bolt", "nw"), "The hand. Pulls a bolt back for five seconds when a palm is recognised.", "J3 — 2 wires"),
        (("<span class='badge'>5</span>Exit button", "nw"), "Opens the bolt from inside without a scan.", "J5 — 2 wires"),
        (("<span class='badge'>6</span>Panel lights", "nw"), "Green = recognised, red = not recognised.", "J7 — 3 wires"),
        (("<span class='badge'>7</span>Laptop (USB-C)", "nw"), "Only for loading software and reading logs.", "J2 — ordinary USB-C cable"),
        (("<span class='badge'>8</span>Debug header", "nw"), "A spare way in if USB ever breaks. Normally empty.", "J6 — 4 pins"),
    ]
    return f"""
<section class="page">
  {H1("s2", "2", "The system at a glance")}
  <p class="lead">One small board is the brain. Eight things connect to it. That is the whole system.</p>
  <p>The board is built around an <strong>ESP32-S3</strong> — a microcontroller with Wi-Fi, Bluetooth and a USB port on a thumbnail-sized module. It does not do the palm recognition itself: the <strong>AI10 sensor</strong> is a small computer of its own that photographs the palm in near-infrared light and answers the question “who is this?”. The board asks that question, reads the answer, and then does the ordinary things: lights, a beep, a message on the screen, and — if the answer is a known person — power to the bolt for a few seconds.</p>
  <p>Everything that plugs into the board is listed below with the number used for it throughout this guide. The numbers appear on the fold-out diagram in Section 3 and as the sub-section numbers in Section 4.</p>
  {table(["What", "What it does", "Where it connects"], items)}
  {plain("Think of it as a small office: the <strong>brain</strong> (ESP32-S3) sits at the desk. The <strong>eye</strong> (sensor) reports who is at the door. The <strong>screen</strong>, <strong>lights</strong> and <strong>beeper</strong> talk to the person. The <strong>bolt</strong> is the only thing that moves. The <strong>adapter</strong> keeps the lights on. The <strong>USB port</strong> is the back door for the person who maintains it.")}
  {eng("Recognition runs entirely inside the AI10 (DFRobot SEN0677): NIR illumination, binocular camera, on-module matching, template storage. The ESP32-S3 drives it over UART at 115 200 baud with a simple framed protocol (<code>EF AA · id · length · payload · XOR</code>). The board itself has 46 parts on 38 nets; its jobs are power conditioning (12 V in → 3.3 V and 5 V), a protected low-side MOSFET driver for the solenoid, an SPI display, USB for programming, and I/O for a button, two LEDs and a piezo. Full design record: <code>docs/DESIGN_REVIEW.md</code>.")}
</section>"""


def sec3() -> str:
    TOC_ENTRIES.append(("s3", "3  The complete wiring diagram (A3 fold-out)", 1))
    return f"""
<section class="wide" id="s3"><div class="wide-inner">{master.svg()}</div></section>"""


def sec4() -> str:
    out = f"""
<section class="page">
  {H1("s4", "4", "Connection by connection")}
  <p class="lead">Each of the eight connections, one at a time: a drawing, the pin table, why it is wired that way, and what goes wrong if it isn’t. Net names (<code>this typeface</code>) are the schematic’s labels.</p>
"""
    # ---------------- 4.1
    out += H2("s41", "4.1", "Power in — the wall adapter")
    out += fig(cards.card_power(), cls="card", caption="<b>Figure 4.1</b> — The adapter’s round plug goes into J8. The screw terminal J1 is an alternative for an adapter with bare wire ends, or a bench supply. They are wired in parallel on the board: use one or the other, never both.")
    out += table(["Connector", "Pin", "Net", "Plain words"], [
        ("J8 barrel jack", ("centre", "c"), ("VIN_12V", "m"), "12 V, positive (+). The adapter must be <em>centre-positive</em> (⊕ symbol on its label)."),
        ("J8 barrel jack", ("sleeve", "c"), ("GND", "m"), "ground (−)"),
        ("J1 screw terminal", ("1", "c"), ("VIN_12V", "m"), "12 V, positive (+) — red wire"),
        ("J1 screw terminal", ("2", "c"), ("GND", "m"), "ground (−) — black wire"),
    ])
    out += plain("The adapter is the only source of power. Twelve volts is the “pressure” the solenoid needs; the board makes its own lower voltages from it (Section 6). Two amps is more than the unit ever draws — about 1.2 A while the bolt is pulled, a quarter of that the rest of the time. A reversed plug does no harm: a one-way valve (D1) on the board simply blocks it.")
    out += eng("12 V DC regulated (±5 %), ≥ 1.5 A, 5.5 × 2.1 mm centre-positive. Path: J8/J1 → F1 (Bourns MF-MSMF200/16 polyfuse, 2 A hold / 4 A trip) → D1 (SS34 Schottky, 3 A, ~0.5 V) → <code>+12V</code> rail with C1 470 µF bulk and D7 SMAJ15A TVS (15 V stand-off, ~24 V clamp, below Q1’s 30 V). Regulators need ≥ 8 V in, so 9 V is out; 19 V drives D7 into conduction and trips F1. Worst 1.5 A, idle ≈ 0.25 A (POWER_BUDGET §1).")
    out += warn("<ul><li>Label must say <strong>12 V</strong> and <strong>⊕ on the centre</strong>. Some adapters (guitar pedals, older modems) are centre-negative.</li><li>Plug size 5.5 × <strong>2.1</strong> mm — a 2.5 mm plug fits loosely and flickers.</li><li><strong>J8 or J1</strong>, never both. Measure the adapter first: 11.5 – 12.6 V is right.</li></ul>")

    # ---------------- 4.2
    out += H2("s42", "4.2", "The palm-vein sensor", newpage=True)
    out += fig(cards.card_sensor(), cls="card", caption="<b>Figure 4.2</b> — The AI10 comes with its 4-wire cable already fitted. Only the small plug at the free end goes onto the board, into CN1. Yellow and green are the two directions of the conversation; red and black are power.")
    out += table(["Pin", "Wire colour", "Net", "Plain words"], [
        (("1", "c"), swatch(C["GND"]) + " black", ("GND", "m"), "ground — the return path for both power and data"),
        (("2", "c"), swatch(C["YEL"]) + " yellow", ("SEN_RX", "m"), "the sensor’s <em>listening</em> wire: the board’s questions travel along it (“reset”, “who is this?”, “add this person”)"),
        (("3", "c"), swatch(C["GRN"]) + " green", ("SEN_TX", "m"), "the sensor’s <em>talking</em> wire: its answers come back along it (“ready”, “user 3, score 92”, “nobody”)"),
        (("4", "c"), swatch(C["12V"]) + " red", ("+5V", "m"), "5 V power for the sensor, made on the board"),
    ])
    out += plain("The sensor and the board talk the way two people talk on a phone: one wire carries each direction, and both must agree on a speed (here 115 200 “bits per second”, roughly eleven thousand letters a second). The maker names the wires from the <em>sensor’s</em> point of view — its RX (receive) wire is where the board’s messages arrive — so the yellow wire is <code>SEN_RX</code> even though it carries what the board <em>sends</em>. The cable does the crossing-over for you; you only plug it in.")
    out += eng("UART1 on the ESP32-S3: IO17 (U1TXD) → CN1 pin 2, IO18 (U1RXD) ← CN1 pin 3. 115 200 8N1, fixed. The sensor is powered from the dedicated <code>+5V</code> rail (U3, R-78E5.0-1.0, 1 A) rather than 12 V: the AI10 accepts 5–12 V, but at 12 V its internal regulator runs hot. Measured draw 320–330 mA at 8 V; budgeted 530 mA worst case at 5 V. C12 (100 µF) sits right at CN1 to feed the unknown start-up spike. After power-up the module sends <code>NOTE:READY</code>; firmware must wait for it before sending any command. Protocol reference: <code>docs/datasheets/SEN0677_AI10_protocol_manual_V1.0.pdf</code>.")
    out += warn("<ul><li><strong>The sensor’s data voltage is not documented.</strong> Before the plug ever touches the board: power the sensor on its own (red = 5 V, black = ground) and measure the <strong>green</strong> wire with a multimeter. Idle, it must read <strong>3.3 V or less (never above 3.6 V)</strong>. If it reads 5 V, stop — the board needs a small divider added on that wire.</li><li>Check the plug pitch: CN1 is a 1.25 mm PicoBlade socket. If the sensor’s plug is 1.5 mm or 2.0 mm, the socket on the board must be changed before ordering the PCB.</li><li>Pin 1 (black) is marked on the board. The plug only fits one way.</li></ul>")

    # ---------------- 4.3
    out += H2("s43", "4.3", "The touch screen", newpage=True)
    out += fig(cards.card_display(), cls="card", caption="<b>Figure 4.3</b> — The screen module has a row of 14 pins that pushes straight into the socket J4 on the board’s top edge. Nothing to solder, no cable. Seven pins drive the picture; six drive the touch layer; pin 9 is deliberately left empty.")
    out += table(["Pin", "Screen label", "Net", "Plain words"], [
        (("1", "c"), "VCC", ("+3V3", "m"), "power for the screen"),
        (("2", "c"), "GND", ("GND", "m"), "ground"),
        (("3", "c"), "CS", ("TFT_CS", "m"), "“I’m talking to <em>you</em>, screen” — the board pulls this low to address the display"),
        (("4", "c"), "RESET", ("TFT_RST", "m"), "restarts the screen chip at power-up"),
        (("5", "c"), "DC", ("TFT_DC", "m"), "tells the screen whether the next byte is a command or picture data"),
        (("6", "c"), "SDI (MOSI)", ("SPI_MOSI", "m"), "picture data, board → screen"),
        (("7", "c"), "SCK", ("SPI_SCK", "m"), "the clock — a steady tick that keeps sender and receiver in step"),
        (("8", "c"), "LED", ("+3V3", "m"), "backlight power"),
        (("9", "c"), "SDO (MISO)", ("—", "m"), "<strong>not connected, on purpose</strong> (see engineer’s note)"),
        (("10", "c"), "T_CLK", ("SPI_SCK", "m"), "the same clock, shared with the touch chip"),
        (("11", "c"), "T_CS", ("TOUCH_CS", "m"), "“I’m talking to you, touch chip”"),
        (("12", "c"), "T_DIN", ("SPI_MOSI", "m"), "commands, board → touch chip"),
        (("13", "c"), "T_DO", ("SPI_MISO", "m"), "the touch position, touch chip → board"),
        (("14", "c"), "T_IRQ", ("TOUCH_IRQ", "m"), "“someone is touching me” — lets the board react instantly"),
    ])
    out += plain("Where the sensor uses two wires, the screen uses a faster arrangement called SPI: a clock wire ticks, and on every tick one bit moves along the data wire. Two chips live on the screen module — one that draws pixels and one that senses your finger — and they share the clock and data wires like two people sharing one phone line. The two <em>CS</em> (“chip select”) wires are how the board says which of them it is addressing. Because the board only ever <em>sends</em> to the picture chip, that chip’s reply wire (pin 9) is left unconnected.")
    out += eng("FSPI on IOMUX pins for full speed: IO12 SCK, IO11 MOSI, IO13 MISO, IO10 TFT_CS (FSPICS0), IO9 TOUCH_CS, IO14 DC, IO21 RST, IO8 TOUCH_IRQ. The whole module runs from <code>+3V3</code> (VCC and LED) so no module output can exceed the ESP32’s 3.3 V I/O — Rev 2.4 moved it off 5 V for exactly that reason; the backlight is marginally dimmer. Pin 9 is unconnected because the ST7789’s SDO does <em>not</em> tri-state when CS is high on these red 2.4″ boards, so it would fight the XPT2046 on MISO — a well-known failure (touch reads garbage, or the display freezes after the first touch). The Robu listing says “ILI9341/ST7789”: firmware must probe and support both. <code>TOUCH_IRQ</code> is optional; polling works.")
    out += warn("<ul><li><strong>Pin 1 to pin 1.</strong> The board’s socket has a square pad at pin 1 and the module’s header has pin 1 marked. Plugging in shifted by one pin puts 3.3 V on a data pin — nothing burns, but nothing works either.</li><li>The manual lists pin <em>names</em> but not their order. When the module arrives, read the order off its silkscreen and compare with the table above before the PCB is ordered.</li></ul>")

    # ---------------- 4.4
    out += H2("s44", "4.4", "The solenoid bolt", newpage=True)
    out += fig(cards.card_lock(), cls="card", caption="<b>Figure 4.4</b> — Two wires from the solenoid into the screw terminal J3. There is no right or wrong way round for the solenoid itself: it is a coil, and the board switches its − side.")
    out += table(["Pin", "Net", "Plain words"], [
        (("1", "c"), ("+12V", "m"), "always at 12 V — one end of the coil sits here permanently"),
        (("2", "c"), ("LOCK_SW", "m"), "the switched end. The board connects it to ground for up to 5 s; current flows; the bolt pulls back"),
    ])
    out += plain("A solenoid is an electromagnet with a spring-loaded bolt inside. Give it 12 V and the magnet pulls the bolt in; take the power away and the spring pushes it out. The board does the “give it 12 V” with an electronic switch (a MOSFET, Q1) on the ground side of the coil, so the wiring is just two wires and a screw terminal. The board also makes sure the bolt is never held in for more than five seconds at a time — these cabinet solenoids overheat if left on.")
    out += eng("Low-side switch: Q1 AO3400A (30 V, 5.7 A, R<sub>DS(on)</sub> ≈ 40 mΩ) gated from IO4 via R13 100 Ω, with R2 10 kΩ gate-to-source holding it off while the ESP32 boots (GPIOs float for ~50 ms at reset). D2 SS54 across the coil catches the inductive kick when Q1 opens. The coil is fed from <code>+12V</code> <em>after</em> F1 and D1 — Rev 2.0 fed it before D1, which put Q1’s body diode straight across a reversed adapter. Rated load: Robu 12 V cabinet lock, ~0.8 A, intermittent duty (max 10 s on). Firmware: hard 5 s cap per release plus the ESP-IDF task watchdog. Fail-secure: loss of power = bolt out = locked.")
    out += warn("<ul><li>Buy a solenoid marked <strong>12 V</strong>. Measure its current once with the multimeter: if it is above 0.8 A, tell whoever orders the PCB — the fuse must move up one size.</li><li>If this bolt ever secures a real door, the door <strong>must open from inside with a handle</strong> regardless of the electronics. That is a fire-safety rule, not a preference.</li><li>Keep this cable away from the exit-button cable and the sensor cable — the coil’s switching can upset them.</li></ul>")

    # ---------------- 4.5
    out += H2("s45", "4.5", "The exit button", newpage=True)
    out += fig(cards.card_exit(), cls="card", caption="<b>Figure 4.5</b> — Any ordinary push button, two wires, into J5. Either way round.")
    out += table(["Pin", "Net", "Plain words"], [
        (("1", "c"), ("EXIT_SW", "m"), "the sensing wire — normally held at 3.3 V by the board"),
        (("2", "c"), ("GND", "m"), "ground"),
    ])
    out += plain("A button is the simplest input there is: two wires that touch when you press. The board keeps the sensing wire gently pulled up to 3.3 V; pressing the button connects it to ground, the voltage drops to zero, and the software sees “pressed”. Real buttons bounce — the contacts chatter for a few thousandths of a second — so the board smooths the wire with a small capacitor and the software double-checks before acting.")
    out += eng("IO6 with R6 10 kΩ pull-up to <code>+3V3</code>, C11 100 nF to ground (RC ≈ 1 ms debounce), and R8 1 kΩ in series between IO6 and the terminal to limit current from static or induced transients on a long wall wire; the ESP32’s internal clamp diodes do the rest. Normally-open momentary switch. Cable length is not critical (tens of metres is fine); route it away from the solenoid cable. On press the firmware runs the same 5 s release sequence as a recognised palm, without touching the sensor.")
    out += warn("Use a <strong>momentary</strong> (push-and-release) button, not a latching one. A latching switch left “on” would hold the release request — the 5 s cap still protects the solenoid, but the door would re-release every time the software re-armed.")

    # ---------------- 4.6
    out += H2("s46", "4.6", "The front-panel lights", newpage=True)
    out += fig(cards.card_leds(), cls="card", caption="<b>Figure 4.6</b> — Two ordinary 5 mm LEDs on wires, into the 3-pin header J7. Both short legs share the ground pin; each long leg has its own pin.")
    out += table(["Pin", "Net", "Plain words"], [
        (("1", "c"), ("GND", "m"), "ground — both LEDs’ <em>short</em> legs join here"),
        (("2", "c"), ("LED_OK_A", "m"), "green LED’s <em>long</em> leg: lights when a palm is recognised"),
        (("3", "c"), ("LED_DENY_A", "m"), "red LED’s <em>long</em> leg: lights when it isn’t"),
    ])
    out += plain("An LED only works one way round: the longer leg is the + side. The board already contains the small resistor each LED needs to limit its current, so the wires are just wires — no extra parts. The screen shows the same information in words; the lights exist so the result can be seen from across the room.")
    out += eng("IO1 → R9 150 Ω → J7.2 (green), IO2 → R10 150 Ω → J7.3 (red); ~8 mA each with a 2 V LED from 3.3 V. Any 5 mm LED with V<sub>f</sub> ≤ 2.4 V works; a blue or white LED (V<sub>f</sub> ≈ 3 V) would be dim. Header is a plain 1×3 2.54 mm pin header; use a 3-way Dupont housing so it cannot be plugged in reversed. Pin 1 is square. The yellow LED D4 on the board itself is a separate 3.3 V “power present” indicator (R7 1 kΩ).")
    out += warn("Long leg to pin 2 or 3, short leg to pin 1. Reversed, the LED simply stays dark — nothing is damaged, so if a light never comes on, this is the first thing to check.")

    # ---------------- 4.7
    out += H2("s47", "4.7", "USB-C — programming and logs", newpage=True)
    out += fig(cards.card_usb(), cls="card", caption="<b>Figure 4.7</b> — A standard USB-C cable to a laptop, into J2. Either way up. Used only by whoever maintains the unit.")
    out += table(["USB-C pins", "Net", "Plain words"], [
        ("A4 A9 B4 B9", ("VBUS", "m"), "the laptop’s 5 V. The board only <em>looks</em> at it to know a cable is present; it never runs on it"),
        ("A6 B6 / A7 B7", ("USB_D+ / USB_D−", "m"), "the data pair, protected against static by D3"),
        ("A5 / B5", ("CC1 / CC2", "m"), "two small resistors that tell the laptop “I am a device, not a charger”"),
        ("A1 A12 B1 B12, shell", ("GND", "m"), "ground and the cable’s metal shield"),
    ])
    out += plain("The USB port is the back door: it is how the software gets onto the brain and how its diary (the log) gets read out. It does not power the unit — the bolt needs 12 V and a USB port can’t supply that — so the adapter must be plugged in even while programming. The board notices when a USB cable is connected and can show it on the screen.")
    out += eng("ESP32-S3 native USB on IO19 (D−) / IO20 (D+) — no bridge chip; the S3 enumerates as a CDC serial port and supports DFU. D3 USBLC6-2SC6 ESD array across D+/D− with VBUS reference. R3/R4 5.1 kΩ CC pull-downs (UFP/sink) so the host applies VBUS in either orientation. No VBUS power path by design (no diode-OR, no 5 V → 3.3 V regulator from USB): 12 V is required for U2/U3 anyway. R11 100 kΩ / R12 150 kΩ divide VBUS to 3.0 V on IO7 (<code>USB_DET</code>) so firmware can hold off the D+ pull-up until a host is present. Shield is tied straight to GND (prototype-appropriate; an RC to chassis is an EMC refinement). Recovery if USB enumeration ever breaks: hold BOOT (S2), tap RESET (S1), or use J6.")
    out += warn("Plug the <strong>12 V adapter in first</strong>, then USB. With only USB connected nothing lights up — that is expected, not a fault.")

    # ---------------- 4.8
    out += H2("s48", "4.8", "The debug header (normally empty)", newpage=True)
    out += fig(cards.card_debug(), cls="card", caption="<b>Figure 4.8</b> — Four pins for a USB-to-serial dongle. A recovery path only; in normal life nothing is connected here.")
    out += table(["Pin", "Net", "Plain words"], [
        (("1", "c"), ("+3V3", "m"), "3.3 V <em>out of</em> the board — a reference for the dongle, never a way to power the board"),
        (("2", "c"), ("TXD0", "m"), "board talks → connect to the dongle’s <strong>RX</strong>"),
        (("3", "c"), ("RXD0", "m"), "board listens ← connect to the dongle’s <strong>TX</strong>"),
        (("4", "c"), ("GND", "m"), "ground"),
    ])
    out += plain("This is the same kind of two-wire conversation as the sensor cable, but between the brain and a laptop. It exists for one reason: if a software mistake ever leaves the USB port not responding, this header still works, because it is wired to the brain’s original console. Notice the crossing: the board’s “talk” pin goes to the dongle’s “listen” pin and vice-versa — the most common mistake in the world of serial cables.")
    out += eng("UART0 console: IO43 (U0TXD) → J6.2, IO44 (U0RXD) ← J6.3. 1×4 2.54 mm pin header. Works with any 3.3 V USB–UART bridge (CP2102, CH340 set to 3.3 V, FT232 at 3.3 V). ROM bootloader is reachable via this port with BOOT held at reset, so a wiped or broken USB stack is recoverable. Pin 1 supplies <code>+3V3</code> for level reference only — do not back-feed the rail from a dongle.")
    out += warn("The dongle must be a <strong>3.3 V</strong> type. A 5 V one can damage the brain’s pins. And never connect the dongle’s 5 V or 3.3 V output to pin 1 — pin 1 is an output.")
    out += "</section>"
    return out


def sec5() -> str:
    rows = [
        ("U1", "ESP32-S3-WROOM-1 (N8R2)", "<strong>The brain.</strong> A complete small computer on one module, with Wi-Fi, Bluetooth and USB built in, plus its own antenna printed on the top edge.", "Dual-core Xtensa LX7 at 240 MHz, 8 MB flash, 2 MB PSRAM, native USB. Antenna keep-out on the board edge; 3 GND pads incl. thermal pad. Strapping pins IO0/IO3/IO45/IO46 left free except IO0 (BOOT)."),
        ("U2", "RECOM R-78E3.3-1.0", "<strong>Pressure reducer, 12 → 3.3 V.</strong> Makes the gentle voltage the brain, screen and lights run on. Runs cool.", "Switching regulator, 1 A, ~93 % efficient, 3-pin SIP, needs ≥ 7 V in. Loss ≈ 0.09 W. Drop-in alternative K7803-1000R3."),
        ("U3", "RECOM R-78E5.0-1.0", "<strong>Pressure reducer, 12 → 5 V.</strong> Feeds only the sensor.", "Switching regulator, 1 A. Must be the 1.0 A part (same body as 0.5 A). ≈ 0.35 W loss at worst load; copper pour suffices."),
        ("F1", "Polyfuse 2 A hold / 16 V", "<strong>Automatic circuit breaker.</strong> If something shorts, it goes high-resistance and cuts the current; when it cools, it resets itself.", "Bourns MF-MSMF200/16, 1812. 4 A trip. Guards against an oversized adapter; with a 2 A SMPS adapter the adapter’s own limit acts first."),
        ("D1", "SS34 Schottky diode", "<strong>One-way valve.</strong> Lets power in only if the adapter is the right way round. Backwards, nothing flows and nothing breaks.", "3 A, 40 V, ~0.5 V forward drop (≈ 0.5 W during a 5 s release). Everything on the board sits behind it."),
        ("D7", "SMAJ15A TVS", "<strong>Surge clamp.</strong> Swallows short voltage spikes — from the lock cable acting as an antenna, or a noisy adapter — before they reach anything delicate.", "15 V stand-off, ~24 V clamp, 400 W peak. Protects Q1 (30 V) and the regulators."),
        ("C1", "470 µF 25 V electrolytic", "<strong>The big tank.</strong> Stores a little energy so that when the bolt suddenly draws current, the voltage doesn’t sag.", "Low-ESR 105 °C, 8 mm radial. Also absorbs the switching ripple from U2/U3. C5/C7 10 µF at the regulator inputs."),
        ("C2, C12", "100 µF 10 V, ×2", "<strong>Smaller tanks</strong> at the 3.3 V output and right at the sensor socket, for the sensor’s start-up gulp.", "SMD electrolytic/polymer 6.3 × 5.4 mm (a 100 µF MLCC in 0805 does not exist). Within RECOM’s 220 µF output-capacitance limit."),
        ("C3, C6, C8, C4, C10, C11", "100 nF … 10 µF ceramics", "<strong>Tiny tanks</strong> placed right next to each chip’s power pin, so fast demands are met locally.", "C3 100 nF at U1 pin 2 (≤ 5 mm), C6/C8 10 µF at regulator outputs, C4 1 µF on EN (10 ms reset RC with R1), C10/C11 100 nF button debounce."),
        ("Q1", "AO3400A N-MOSFET", "<strong>Electronic switch</strong> for the bolt — like a relay with no moving parts. The brain nudges it with 3.3 V; it switches the full 12 V current.", "SOT-23, 30 V, 5.7 A, R<sub>DS(on)</sub> ≈ 40 mΩ, V<sub>GS(th)</sub> ≤ 1.45 V. Low-side. R13 100 Ω gate series, R2 10 kΩ gate pull-down."),
        ("D2", "SS54 Schottky diode", "<strong>Kick-back catcher.</strong> When the switch opens, the coil tries to keep current flowing; this diode gives it a safe path instead of a damaging spike.", "5 A, 40 V, across J3 (cathode to +12V). Flyback / freewheeling diode."),
        ("R2", "10 kΩ", "<strong>Safety resistor</strong> that holds the switch firmly off while the brain is waking up, so the bolt can never twitch at power-on.", "Gate-to-source pull-down; GPIOs are high-impedance for ~50 ms after reset."),
        ("D3", "USBLC6-2SC6", "<strong>Static guard</strong> on the USB data wires. Your finger on the plug can carry thousands of volts of static; this shunts it away.", "Ultra-low-capacitance ESD array, SOT-23-6, on D+/D− with VBUS reference."),
        ("R3, R4", "5.1 kΩ ×2", "Tell the laptop <strong>“I’m a device”</strong> so it switches on its USB power for either plug orientation.", "CC1/CC2 pull-downs, USB-C UFP sink."),
        ("R11, R12", "100 kΩ / 150 kΩ", "<strong>USB detector.</strong> Lets the brain see that a cable is plugged in.", "VBUS divider → 3.0 V on IO7 (<code>USB_DET</code>)."),
        ("BZ1, R5", "Passive piezo, 220 Ω", "<strong>The beeper.</strong> One beep for welcome, two for denied.", "Passive piezo element driven by a PWM tone on IO5 through 220 Ω (≈ 15 mA edge current). A magnetic buzzer would need a transistor — don’t substitute."),
        ("S1, S2", "Tactile buttons", "<strong>Reset</strong> restarts the brain. <strong>Boot</strong>, held while pressing Reset, puts it into programming mode. Both only for the maintainer.", "S1 → EN (with R1 10 kΩ / C4 1 µF). S2 → IO0 strapping with C10 100 nF; internal pull-up."),
        ("D4, R7", "Yellow LED, 1 kΩ", "<strong>Power light</strong> on the board itself: proves the 3.3 V supply is alive even before the screen wakes up.", "0603 LED on <code>+3V3</code>, ~1.3 mA."),
        ("R6, R8, C11", "10 kΩ, 1 kΩ, 100 nF", "Make the <strong>exit button</strong> read cleanly and protect the brain from the long wire.", "Pull-up, series guard, RC debounce on IO6 (Section 4.5)."),
        ("R9, R10", "150 Ω ×2", "Current limiters for the two <strong>panel lights</strong>.", "~8 mA each from 3.3 V GPIOs (Section 4.6)."),
    ]
    return f"""
<section class="page">
  {H1("s5", "5", "Inside the board — the parts and what they do")}
  <p class="lead">Forty-six parts sit on the board. Most of them exist to protect something, store a little energy, or keep a signal clean. Here is each one in ordinary words, with the engineering detail beside it.</p>
  <p>Parts are named as printed on the board: <code>U</code> chips and modules, <code>D</code> diodes and LEDs, <code>C</code> capacitors, <code>R</code> resistors, <code>Q</code> transistors, <code>F</code> fuses, <code>J</code>/<code>CN</code> connectors, <code>S</code> switches, <code>BZ</code> buzzer.</p>
  {eng("Parts count by category: 1 module, 2 regulators, 1 fuse, 4 diodes (D1, D2, D7, plus the D3 array), 1 LED, 1 MOSFET, 12 capacitors, 13 resistors, 2 switches, 1 buzzer, 9 connectors — 46 on-board, plus the two panel LEDs. Full BOM with sourcing notes in <code>docs/COMPONENTS.md</code>; every value is justified in <code>docs/POWER_BUDGET.md</code> or <code>docs/DESIGN_REVIEW.md</code>.")}
  {table([("Ref", "w-ref"), ("", "w-ic"), ("Part", "w-part"), "In plain words", "For the engineer"], cls="dense", rows=[(r[0], (cards.icon(k), "ic"), r[1], r[2], r[3]) for r, k in zip(rows, ICONS)])}
</section>"""


ICONS = ["module", "regulator", "regulator", "fuse", "diode", "diode", "cap_big", "cap_small", "ceramics", "mosfet",
         "diode", "resistor", "esd", "resistor", "resistor", "buzzer", "buttons", "led", "resistor", "resistor"]


def sec6() -> str:
    return f"""
<section class="page">
  {H1("s6", "6", "Where the power goes")}
  <p class="lead">One 12 V supply comes in. Three voltages come out of it. Each part gets the voltage it was built for.</p>
  {fig(cards.power_tree(), caption="<b>Figure 6.1</b> — The power tree. Left to right: adapter, fuse, one-way valve, then the +12 V rail. Two regulators step it down; the solenoid takes it straight. Widths are roughly proportional to current.")}
  {plain("Think of the 12 V rail as the mains water pipe in a house. The fuse is a stopcock that shuts itself if a pipe bursts; the one-way valve stops water flowing back into the street. The big tank (C1) keeps the pressure steady when a tap opens suddenly — that tap is the solenoid, the thirstiest thing in the box. Two pressure reducers (U2, U3) feed the delicate things: the brain and screen at 3.3 V, the sensor at 5 V.")}
  {table(["Rail", "Made by", "Feeds", "Typical", "Worst"], [
        (("+12V", "m"), "adapter via F1, D1", "U2, U3, solenoid (via Q1), C1, D7", "0.25 A idle", "1.5 A for ≤ 5 s"),
        (("+5V", "m"), "U3 (1 A)", "sensor only", "0.35 – 0.43 A", "0.63 A + start-up spike"),
        (("+3V3", "m"), "U2 (1 A)", "brain, screen + backlight, panel LEDs, buzzer, pull-ups, debug header", "0.15 A", "0.52 A (Wi-Fi burst)"),
        (("VBUS", "m"), "laptop", "nothing — sensed only (R11/R12 → IO7)", "0", "0"),
  ])}
  {eng("Worst-case dissipation: D1 0.53 W (5 s bursts), U3 0.35 W, U2 0.09 W, F1 0.1 W, Q1 0.03 W — copper pours suffice, no heatsinks. Trace widths (POWER_BUDGET §6): +12V trunk to J3 and +5V trunk to CN1 ≥ 1.0 mm at 1 oz, +12V to U2/U3 0.6 mm, signals 0.2–0.25 mm. A 3 A adapter is acceptable and lets F1 (4 A trip) act on a hard short before the adapter does. Unknowns: AI10 inrush (mitigated by C12), display current (est. 100 mA).")}
</section>"""


def sec7() -> str:
    return f"""
<section class="page">
  {H1("s7", "7", "What happens during a scan")}
  <p class="lead">From switching on to a door opening, in seven steps — and which wire each step travels on.</p>
  {fig(cards.scan_timeline(), caption="<b>Figure 7.1</b> — One scan. Yellow steps are messages from the board to the sensor (yellow wire); green steps are the sensor’s replies (green wire).")}
  <ol>
    <li><strong>Power on.</strong> The adapter is plugged in. The yellow light on the board comes on within a fraction of a second (the 3.3 V rail is alive). The brain boots and shows “starting” on the screen. The sensor, on its own 5 V, boots too.</li>
    <li><strong>Sensor ready.</strong> A few seconds later the sensor sends a “ready” message down the green wire. Until it does, the board sends nothing — asking too early is ignored or answered with an error.</li>
    <li><strong>Waiting.</strong> The screen says “hold your palm over the sensor”. The sensor watches for a hand at the right distance; the board listens.</li>
    <li><strong>Palm seen.</strong> The board sends the “verify” command on the yellow wire. The sensor lights its infrared LEDs, photographs the veins, and compares the pattern with the people it has stored.</li>
    <li><strong>Answer.</strong> About a second later the reply arrives on the green wire: either a person number and a confidence score, or “nobody”.</li>
    <li><strong>Match.</strong> The board switches the green light on (J7 pin 2), beeps once (BZ1), shows “Welcome” on the screen, and switches Q1 on so 12 V flows through the bolt for five seconds. Then Q1 opens, D2 catches the coil’s kick, the spring pushes the bolt out, and everything returns to <em>Waiting</em>.</li>
    <li><strong>No match.</strong> Red light (J7 pin 3), two low beeps, “Not recognised”. Back to <em>Waiting</em>.</li>
  </ol>
  {plain("The exit button skips steps 3–5 entirely: pressing it produces the same five-second release. Adding a person is the same conversation with a different question — the screen guides the maintainer through it, and the sensor stores the new pattern in its own memory, not on the board.")}
  {eng("Firmware skeleton: UART1 task (framing, XOR check, <code>NOTE:READY</code> gate) → event queue → application state machine (IDLE → VERIFY_PENDING → RELEASE(5 s) → IDLE) → outputs. The release timer is a hardware timer, and the ESP-IDF task watchdog is armed on the application task; a hung task resets the chip, and R2 guarantees Q1 is off through the reset. <code>VERIFY</code> (0x12) carries a timeout byte; <code>NOTE</code> messages report face/palm position while the module is searching, so the screen can say “a little higher”. Score threshold and template management stay inside the AI10.")}
</section>"""


def sec8() -> str:
    return f"""
<section class="page">
  {H1("s8", "8", "Before you power it on")}
  <p class="lead">Ten minutes with a multimeter, in this order. Each line prevents a specific way of breaking something.</p>
  <h3>Bench, before anything is plugged into the board</h3>
  <ul class="check">
    <li>Adapter measures <strong>11.5 – 12.6 V</strong> with nothing connected, and its label shows ⊕ on the centre pin.</li>
    <li>Sensor, powered on its own: the <strong>green wire idles at ≤ 3.6 V</strong>. If it reads 5 V, stop and ask for the divider.</li>
    <li>Solenoid coil resistance is roughly <strong>10 – 20 Ω</strong> (≈ 0.6 – 1.2 A at 12 V). An open circuit or under 5 Ω means a faulty unit.</li>
    <li>Screen module’s pin order matches the table in Section 4.3, read off its silkscreen.</li>
    <li>Buzzer says <strong>passive</strong> and <strong>piezo</strong> on the listing.</li>
  </ul>
  <h3>Board, empty (no modules, no adapter)</h3>
  <ul class="check">
    <li>Resistance from <code>+12V</code> to <code>GND</code> is not a short (should climb as C1 charges through the meter).</li>
    <li>No solder bridges across Q1, D3, or the regulator pins.</li>
  </ul>
  <h3>First power</h3>
  <ul class="check">
    <li>Adapter only — nothing else plugged in. The <strong>yellow light</strong> comes on.</li>
    <li>Measure: <code>+12V</code> ≈ 11.5 V (12 V minus D1), <code>+5V</code> = 4.9 – 5.1 V, <code>+3V3</code> = 3.2 – 3.4 V.</li>
    <li>Power off. Plug in the screen (pin 1 to pin 1). Power on: backlight lights.</li>
    <li>Power off. Plug in the sensor. Power on: the sensor’s IR LEDs may glow faintly on a phone camera; the board reports “ready” in the log.</li>
    <li>Power off. Connect the solenoid. Power on, press the exit button: bolt pulls for 5 s and releases.</li>
  </ul>
  <h3>Always</h3>
  <ul class="check">
    <li>One power source into the board at a time (J8 <em>or</em> J1).</li>
    <li>USB is never the power source. 12 V first, USB second.</li>
    <li>A door secured by this bolt opens from inside by hand.</li>
  </ul>
  {warn("If anything smells hot, gets hot to the touch, or the yellow light flickers: unplug the adapter first, think second. The fuse resets itself once it cools, so a flickering light usually means a short somewhere downstream.", tag="If something is wrong")}
</section>"""


def appendix_a() -> str:
    j2 = [("A1 B1 A12 B12", "GND"), ("A4 A9 B4 B9", "VBUS"), ("A5", "CC1"), ("B5", "CC2"), ("A6 B6", "USB_D+"),
          ("A7 B7", "USB_D−"), ("A8 B8", "SBU — not connected"), ("S1 (shell)", "GND")]
    gpio = [("EN", "EN", "reset (S1, R1, C4)"), ("IO0", "BOOT", "boot strap (S2, C10)"), ("IO1", "LED_OK", "green panel LED → R9 → J7.2"),
            ("IO2", "LED_DENY", "red panel LED → R10 → J7.3"), ("IO4", "LOCK_EN", "solenoid switch → R13 → Q1 gate"),
            ("IO5", "BUZZER", "piezo → R5 → BZ1"), ("IO6", "EXIT_BTN", "exit button (R6, R8, C11) ← J5.1"),
            ("IO7", "USB_DET", "VBUS present (R11/R12)"), ("IO8", "TOUCH_IRQ", "J4.14"), ("IO9", "TOUCH_CS", "J4.11"),
            ("IO10", "TFT_CS", "J4.3"), ("IO11", "SPI_MOSI", "J4.6, J4.12"), ("IO12", "SPI_SCK", "J4.7, J4.10"),
            ("IO13", "SPI_MISO", "J4.13"), ("IO14", "TFT_DC", "J4.5"), ("IO17", "SEN_RX", "U1TXD → CN1.2 (yellow)"),
            ("IO18", "SEN_TX", "U1RXD ← CN1.3 (green)"), ("IO19", "USB_D−", "J2"), ("IO20", "USB_D+", "J2"),
            ("IO21", "TFT_RST", "J4.4"), ("IO43", "TXD0", "J6.2"), ("IO44", "RXD0", "J6.3"),
            ("IO3, IO45, IO46", "—", "strapping pins, deliberately unconnected")]
    return f"""
<section class="page">
  {H1("sa", "A", "Appendix — pin tables")}
  <p>The complete reference for every connector, in one place. Net names are the schematic labels. Pin 1 is marked on the board.</p>
  <div class="cols2">
  {table(["J8 · DC jack 5.5 × 2.1", "Net"], [("centre", ("VIN_12V", "m")), ("sleeve", ("GND", "m"))])}
  {table(["J1 · 12 V screw terminal", "Net"], [("1", ("VIN_12V", "m")), ("2", ("GND", "m"))])}
  {table(["J3 · lock terminal", "Net"], [("1", ("+12V", "m")), ("2", ("LOCK_SW", "m"))])}
  {table(["J5 · exit button", "Net"], [("1", ("EXIT_SW", "m")), ("2", ("GND", "m"))])}
  {table(["J7 · panel LEDs", "Net"], [("1", ("GND", "m")), ("2", ("LED_OK_A", "m")), ("3", ("LED_DENY_A", "m"))])}
  {table(["J6 · debug UART", "Net"], [("1", ("+3V3", "m")), ("2", ("TXD0", "m")), ("3", ("RXD0", "m")), ("4", ("GND", "m"))])}
  {table(["CN1 · sensor (PicoBlade 1.25 mm)", "Net"], [("1 black", ("GND", "m")), ("2 yellow", ("SEN_RX", "m")), ("3 green", ("SEN_TX", "m")), ("4 red", ("+5V", "m"))])}
  {table(["J2 · USB-C", "Net"], [(a, (b, "m")) for a, b in j2])}
  </div>
  {table(["J4 · display, 14-pin", "Net", "", "J4 · display, 14-pin", "Net"], [
        ("1 VCC", ("+3V3", "m"), "", "8 LED", ("+3V3", "m")),
        ("2 GND", ("GND", "m"), "", "9 SDO", ("— (NC)", "m")),
        ("3 CS", ("TFT_CS", "m"), "", "10 T_CLK", ("SPI_SCK", "m")),
        ("4 RESET", ("TFT_RST", "m"), "", "11 T_CS", ("TOUCH_CS", "m")),
        ("5 DC", ("TFT_DC", "m"), "", "12 T_DIN", ("SPI_MOSI", "m")),
        ("6 SDI", ("SPI_MOSI", "m"), "", "13 T_DO", ("SPI_MISO", "m")),
        ("7 SCK", ("SPI_SCK", "m"), "", "14 T_IRQ", ("TOUCH_IRQ", "m")),
  ])}
  <h2>ESP32-S3 pin use</h2>
  {table(["GPIO", "Net", "Goes to"], [(a, (b, "m"), c) for a, b, c in gpio], cls=None)}
</section>"""


def appendix_b() -> str:
    terms = [
        ("Capacitor", "A tiny rechargeable tank for electricity. Big ones smooth the supply; small ones sit next to chips to answer sudden demands."),
        ("Debounce", "Smoothing the chatter of a mechanical button so one press is read as one press."),
        ("Diode", "A one-way valve for current. A Schottky diode is a low-loss kind; a TVS diode is one built to swallow spikes; an LED is one that lights up."),
        ("ESD", "Electrostatic discharge — the spark from a finger. Thousands of volts, harmless to you, fatal to a chip."),
        ("Fail-secure", "When power is lost, the lock stays locked. (The opposite, fail-safe, unlocks.)"),
        ("Flyback diode", "The diode across a coil that gives its stored energy somewhere safe to go when the coil is switched off."),
        ("Fuse (polyfuse)", "A self-resetting fuse: it becomes a high resistance when too much current flows, then recovers when it cools."),
        ("MOSFET", "An electronic switch. A small voltage on its gate lets a large current flow between its other two pins."),
        ("NIR", "Near-infrared light, 700–900 nm — just beyond what the eye can see. Blood absorbs it; skin lets it through; that is why veins show up dark."),
        ("Pull-up / pull-down", "A resistor that gives a wire a definite resting level (high or low) so it doesn’t float and pick up noise."),
        ("Regulator", "A circuit that turns one voltage into another, steadily. Switching regulators do it efficiently and run cool."),
        ("Strapping pin", "A pin the ESP32 reads at the instant of reset to decide how to start. Left alone unless you mean it."),
        ("Watchdog", "A timer the software must keep resetting. If the software hangs, the timer expires and restarts the chip."),
    ]
    return f"""
<section class="page">
  {H1("sb", "B", "Appendix — glossary")}
  {table(["Term", "Meaning"], terms, cls=None)}
  <h2>References</h2>
  <ul>
    <li>palm-scan design documents: <code>docs/NETLIST.md</code>, <code>docs/COMPONENTS.md</code>, <code>docs/POWER_BUDGET.md</code>, <code>docs/DATASHEETS.md</code>, <code>docs/DESIGN_REVIEW.md</code>; schematic <code>hardware/kicad/palm-scan.pdf</code>.</li>
    <li>DFRobot, <em>SEN0677 AI10 wiki</em> and <em>User Software Development Manual</em> V1.0 (2025).</li>
    <li>Espressif, <em>ESP32-S3-WROOM-1 Datasheet</em> v1.8.</li>
    <li>RECOM, <em>R-78E series</em> datasheet; Alpha &amp; Omega, <em>AO3400A</em>; Vishay, <em>SS34</em>; ST, <em>USBLC6-2SC6</em>.</li>
    <li>W. Wu et al., “Review of palm vein recognition,” <em>IET Biometrics</em> 9(1), 2020.</li>
  </ul>
  <p class="small" style="margin-top:10mm">Generated from the Rev 2.4 netlist by <code>docs/wiring-guide/build.py</code>. The board drawing in Section 3 is illustrative; connector positions are fixed during PCB layout. Makers: Ashmita K Rao, Adithya Satish, Vinod Kumar.</p>
</section>"""


# ----------------------------------------------------------------------------- assembly
def document(pages: dict[str, int] | None) -> str:
    TOC_ENTRIES.clear()
    body = sec1() + sec2() + sec3() + sec4() + sec5() + sec6() + sec7() + sec8() + appendix_a() + appendix_b()
    toc = contents(pages)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{DOC_TITLE}</title>
<style>{CSS}</style></head><body>{cover()}{toc}{body}</body></html>"""


def render(html_path: Path, pdf_path: Path) -> None:
    if not CHROME:
        raise SystemExit("No Chromium found. Set CHROME=/path/to/chrome")
    subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
                    f"--print-to-pdf={pdf_path}", "--no-pdf-header-footer", html_path.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def page_map(pdf_path: Path) -> dict[str, int]:
    """Which page each heading starts on (pdftotext, one page at a time; skip cover + contents)."""
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout).group(1))
    found: dict[str, int] = {}
    info = subprocess.run(["pdfinfo", "-f", "1", "-l", str(n), str(pdf_path)], capture_output=True, text=True).stdout
    for m in re.finditer(r"Page\s+(\d+) size:\s+([\d.]+) x", info):
        if float(m.group(2)) > 1000:            # the only A3-landscape page is the fold-out
            found["s3"] = int(m.group(1))
    for pg in range(3, n + 1):
        txt = subprocess.run(["pdftotext", "-f", str(pg), "-l", str(pg), "-layout", str(pdf_path), "-"],
                             capture_output=True, text=True).stdout
        lines = [re.sub(r"\s+", " ", ln).strip() for ln in txt.splitlines()]
        for id_, title, _ in TOC_ENTRIES:
            if id_ in found:
                continue
            key = re.sub(r"\s+", " ", title).strip()
            if any(ln.startswith(key) for ln in lines):
                found[id_] = pg
    return found


def main() -> None:
    OUT_HTML.write_text(document(None), encoding="utf-8")
    render(OUT_HTML, OUT_PDF)
    pages = page_map(OUT_PDF)
    OUT_HTML.write_text(document(pages), encoding="utf-8")
    render(OUT_HTML, OUT_PDF)
    print(f"wrote {OUT_PDF} ({OUT_PDF.stat().st_size // 1024} kB); headings found on pages: {pages}")


if __name__ == "__main__":
    main()
