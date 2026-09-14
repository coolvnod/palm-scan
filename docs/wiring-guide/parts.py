"""SVG drawing primitives and component illustrations for the wiring guide.

Every function returns an SVG fragment (string). Coordinates are in the caller's
viewBox units. Style is deliberately "technical illustration": flat fills, soft
shading, rounded corners, real proportions — so a reader who has never seen a
schematic still recognises the adapter, the screen, the lock.
"""

from __future__ import annotations

# ---------------------------------------------------------------- palette
INK = "#1c1c1c"
PAPER = "#ffffff"
BOARD = "#1f6b45"          # solder-mask green
BOARD_DARK = "#174f33"
BOARD_EDGE = "#0f3a25"
COPPER = "#c9a24a"
SILK = "#f2f2f2"
PLASTIC = "#2b2b2b"
PLASTIC_LT = "#4a4a4a"
METAL = "#b9bec4"
METAL_DK = "#7d8388"
TERMINAL_GREEN = "#2f8f4e"
LABEL = "#333333"
MUTED = "#6b6b6b"
CALLOUT = "#1f3a5f"

WIRE = {
    "12V": "#d62828",
    "5V": "#f77f00",
    "3V3": "#e9c46a",
    "GND": "#222222",
    "SIG_A": "#2a9d8f",   # generic signal, teal
    "SIG_B": "#457b9d",   # generic signal, blue
    "YEL": "#f4c20d",
    "GRN": "#3aa655",
    "WHT": "#e8e8e8",
    "USB": "#6a4c93",
}

SANS = "Lato, 'Liberation Sans', sans-serif"
MONO = "'Ubuntu Mono', 'DejaVu Sans Mono', monospace"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------- text
def text(x, y, s, size=13, weight=400, fill=INK, anchor="start", family=SANS,
         italic=False, extra="") -> str:
    style = f"font-family:{family};font-size:{size}px;font-weight:{weight};"
    if italic:
        style += "font-style:italic;"
    return (f'<text x="{x}" y="{y}" fill="{fill}" text-anchor="{anchor}" '
            f'style="{style}" {extra}>{esc(s)}</text>')


def mono(x, y, s, size=11, fill=INK, anchor="start", weight=400) -> str:
    return text(x, y, s, size=size, fill=fill, anchor=anchor, family=MONO, weight=weight)


def label_lines(x, y, lines, size=12, fill=LABEL, anchor="start", lh=1.3, weight=400):
    out = []
    for i, ln in enumerate(lines):
        out.append(text(x, y + i * size * lh, ln, size=size, fill=fill, anchor=anchor, weight=weight))
    return "".join(out)


# ---------------------------------------------------------------- shapes
def rrect(x, y, w, h, r=6, fill=PAPER, stroke=INK, sw=1.2, extra="") -> str:
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def circle(cx, cy, r, fill=PAPER, stroke=INK, sw=1.2, extra="") -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def line(x1, y1, x2, y2, stroke=INK, sw=1.2, extra="") -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def path(d, stroke=INK, sw=1.2, fill="none", extra="") -> str:
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" {extra}/>'


def defs() -> str:
    """Gradients, filters and patterns shared by all illustrations."""
    return """
<defs>
  <linearGradient id="gMetal" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e6e9ec"/><stop offset="0.5" stop-color="#b9bec4"/><stop offset="1" stop-color="#8d9297"/>
  </linearGradient>
  <linearGradient id="gPlastic" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4b4b4b"/><stop offset="1" stop-color="#232323"/>
  </linearGradient>
  <linearGradient id="gBoard" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#25764d"/><stop offset="1" stop-color="#1a5c3b"/>
  </linearGradient>
  <linearGradient id="gScreen" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#10233a"/><stop offset="1" stop-color="#050b14"/>
  </linearGradient>
  <linearGradient id="gAdapter" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fafafa"/><stop offset="1" stop-color="#d9d9d9"/>
  </linearGradient>
  <linearGradient id="gSolenoid" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#d7dadd"/><stop offset="0.55" stop-color="#9aa0a6"/><stop offset="1" stop-color="#6c7176"/>
  </linearGradient>
  <linearGradient id="gCopper" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e9cf7a"/><stop offset="1" stop-color="#b98d2e"/>
  </linearGradient>
  <filter id="shadow" x="-10%" y="-10%" width="130%" height="140%">
    <feDropShadow dx="0" dy="2.5" stdDeviation="2.5" flood-color="#000" flood-opacity="0.22"/>
  </filter>
  <filter id="softShadow" x="-10%" y="-10%" width="130%" height="140%">
    <feDropShadow dx="0" dy="1.5" stdDeviation="1.5" flood-color="#000" flood-opacity="0.18"/>
  </filter>
  <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="7" stroke="#ffffff" stroke-width="1.4" stroke-opacity="0.55"/>
  </pattern>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="#1c1c1c"/>
  </marker>
  <marker id="arrowMuted" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="#6b6b6b"/>
  </marker>
</defs>
"""


# ---------------------------------------------------------------- wires
def wire(d: str, color: str, width: float = 5, outline: bool = True, dash: str = "") -> str:
    """A cable: dark outline under a coloured core so it reads as a physical wire."""
    dash_attr = f'stroke-dasharray="{dash}"' if dash else ""
    out = ""
    if outline:
        out += path(d, stroke="#111", sw=width + 2.2, extra='stroke-linecap="round" stroke-linejoin="round"')
    out += path(d, stroke=color, sw=width, extra=f'stroke-linecap="round" stroke-linejoin="round" {dash_attr}')
    if color in ("#222222", "#111111", "#1c1c1c"):
        # ground / black wire: add a faint highlight so it isn't a black bar
        out += path(d, stroke="#ffffff", sw=max(width * 0.22, 0.8),
                    extra='stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.35"')
    return out


def ribbon(x1, y1, x2, y2, colors, spacing=5.5, width=3.6) -> str:
    """Several parallel straight wires (a flat ribbon) from (x1,y1) to (x2,y2)."""
    import math
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L               # unit normal
    n = len(colors)
    out = ""
    for i, c in enumerate(colors):
        off = (i - (n - 1) / 2) * spacing
        ox, oy = nx * off, ny * off
        out += wire(f"M{x1+ox},{y1+oy} L{x2+ox},{y2+oy}", c, width=width)
    return out


def flow_arrow(x1, y1, x2, y2, color=INK, sw=1.6) -> str:
    return line(x1, y1, x2, y2, stroke=color, sw=sw, extra='marker-end="url(#arrow)"')


# ---------------------------------------------------------------- callouts
def callout(cx, cy, n, r=15, fill=CALLOUT) -> str:
    return (circle(cx, cy, r, fill=fill, stroke="#ffffff", sw=2.5, extra='filter="url(#softShadow)"') +
            text(cx, cy + 6, str(n), size=17, weight=700, fill="#ffffff", anchor="middle"))


def note_box(x, y, w, lines, size=12, title=None, fill="#fff8e6", stroke="#e0b64d", lh=1.35) -> str:
    n = len(lines) + (1 if title else 0)
    h = 14 + n * size * lh + 4
    out = rrect(x, y, w, h, r=5, fill=fill, stroke=stroke, sw=1)
    cy = y + 10 + size
    if title:
        out += text(x + 10, cy, title, size=size, weight=700)
        cy += size * lh
    for ln in lines:
        out += text(x + 10, cy, ln, size=size, fill=LABEL)
        cy += size * lh
    return out


# ---------------------------------------------------------------- board-level connectors
def pin_header(x, y, n, pitch=9, vertical=False, female=False, numbers=True, first=1, num_side="below",
               label_only=None) -> str:
    """1×n 2.54 mm header. Horizontal by default: pins run left→right.

    label_only: optional set of pin numbers to print (e.g. {1, 14}) when the pitch is too tight for all.
    """
    body_w = n * pitch + 4
    body_h = 12
    out = ""
    if vertical:
        out += rrect(x, y, body_h, body_w, r=1.5, fill="url(#gPlastic)", stroke="#000", sw=0.8)
        for i in range(n):
            cy = y + 2 + pitch / 2 + i * pitch
            if female:
                out += rrect(x + 3.5, cy - 2.5, 5, 5, r=0.5, fill="#111", stroke="#000", sw=0.4)
            else:
                out += rrect(x + 3.5, cy - 2.2, 5, 4.4, r=1, fill="url(#gCopper)", stroke="#8a6a1e", sw=0.5)
            if numbers and (label_only is None or first + i in label_only):
                out += mono(x - 4 if num_side == "left" else x + body_h + 4, cy + 3.5, str(first + i), size=9,
                            fill=MUTED, anchor="end" if num_side == "left" else "start")
    else:
        out += rrect(x, y, body_w, body_h, r=1.5, fill="url(#gPlastic)", stroke="#000", sw=0.8)
        for i in range(n):
            cx = x + 2 + pitch / 2 + i * pitch
            if female:
                out += rrect(cx - 2.5, y + 3.5, 5, 5, r=0.5, fill="#111", stroke="#000", sw=0.4)
            else:
                out += rrect(cx - 2.2, y + 3.5, 4.4, 5, r=1, fill="url(#gCopper)", stroke="#8a6a1e", sw=0.5)
            if numbers and (label_only is None or first + i in label_only):
                ny = y - 3 if num_side == "above" else y + body_h + 10
                out += mono(cx, ny, str(first + i), size=9, fill=MUTED, anchor="middle")
    return out


def screw_terminal(x, y, n=2, pitch=18, facing="left") -> str:
    """Phoenix-style 5.08 mm screw terminal block. Wires enter from `facing` side."""
    w, h = 20, n * pitch
    out = rrect(x, y, w, h, r=2, fill=TERMINAL_GREEN, stroke="#1d5f33", sw=1)
    for i in range(n):
        cy = y + pitch / 2 + i * pitch
        # screw head
        out += circle(x + w / 2, cy, 5.2, fill="url(#gMetal)", stroke="#555", sw=0.8)
        out += line(x + w / 2 - 3.2, cy, x + w / 2 + 3.2, cy, stroke="#444", sw=1.4)
        # wire entry (dark square on facing side)
        ex = x - 7 if facing == "left" else x + w
        out += rrect(ex, cy - 4.5, 7, 9, r=1, fill="#0f3d1f", stroke="#0a2a15", sw=0.6)
    return out


def barrel_jack(x, y, facing="left") -> str:
    """DC-005 5.5×2.1 mm jack. Opening on `facing` side."""
    w, h = 34, 26
    out = rrect(x, y, w, h, r=3, fill="url(#gPlastic)", stroke="#000", sw=0.9)
    ox = x if facing == "left" else x + w
    out += circle(ox, y + h / 2, 8.5, fill="#0d0d0d", stroke="#555", sw=1)
    out += circle(ox, y + h / 2, 3, fill="url(#gMetal)", stroke="#333", sw=0.6)
    return out


def usb_c(x, y, facing="left") -> str:
    w, h = 26, 12
    out = rrect(x, y, w, h, r=6, fill="url(#gMetal)", stroke="#4d5257", sw=1)
    out += rrect(x + 3, y + 3.5, w - 6, h - 7, r=3, fill="#111", stroke="none")
    return out


def picoblade(x, y, n=4, pitch=7, vertical=True) -> str:
    """Molex PicoBlade 1.25 mm socket — small white/cream box."""
    if vertical:
        w, h = 14, n * pitch + 4
        out = rrect(x, y, w, h, r=1.5, fill="#f4f1e8", stroke="#9a9484", sw=0.9)
        for i in range(n):
            cy = y + 2 + pitch / 2 + i * pitch
            out += rrect(x + 4, cy - 2, 6, 4, r=0.5, fill="url(#gCopper)", stroke="#8a6a1e", sw=0.4)
    else:
        w, h = n * pitch + 4, 14
        out = rrect(x, y, w, h, r=1.5, fill="#f4f1e8", stroke="#9a9484", sw=0.9)
        for i in range(n):
            cx = x + 2 + pitch / 2 + i * pitch
            out += rrect(cx - 2, y + 4, 4, 6, r=0.5, fill="url(#gCopper)", stroke="#8a6a1e", sw=0.4)
    return out


def tact_button(x, y, size=14) -> str:
    out = rrect(x, y, size, size, r=2, fill="url(#gMetal)", stroke="#555", sw=0.8)
    out += circle(x + size / 2, y + size / 2, size * 0.3, fill="#222", stroke="#000", sw=0.6)
    return out


def smd_chip(x, y, w, h, label="", pins=0, pitch=4) -> str:
    out = rrect(x, y, w, h, r=1.5, fill="#151515", stroke="#000", sw=0.7)
    for i in range(pins):
        px = x + 3 + i * pitch
        out += rrect(px, y - 2, 2, 2, r=0.3, fill=METAL, stroke="none")
        out += rrect(px, y + h, 2, 2, r=0.3, fill=METAL, stroke="none")
    if label:
        out += mono(x + w / 2, y + h / 2 + 3.5, label, size=8, fill="#dddddd", anchor="middle")
    return out


def sip_regulator(x, y, label) -> str:
    """RECOM R-78E 3-pin SIP module, standing up."""
    w, h = 40, 30
    out = rrect(x, y, w, h, r=2, fill="#1b1b1b", stroke="#000", sw=0.8, extra='filter="url(#softShadow)"')
    out += mono(x + w / 2, y + 13, "RECOM", size=8, fill="#bbbbbb", anchor="middle")
    out += mono(x + w / 2, y + 24, label, size=8.5, fill="#ffffff", anchor="middle", weight=700)
    for i in range(3):
        out += rrect(x + 8 + i * 12, y + h, 3, 5, r=0.5, fill=METAL, stroke="none")
    return out


def electrolytic(x, y, r=12, label="") -> str:
    out = circle(x, y, r, fill="#1a1a2e", stroke="#000", sw=0.9, extra='filter="url(#softShadow)"')
    out += circle(x, y, r - 2.5, fill="none", stroke="#3a3a5e", sw=0.8)
    out += path(f"M{x-r*0.6},{y-r*0.9} A{r} {r} 0 0 0 {x-r*0.6},{y+r*0.9}", stroke="#cfcfcf", sw=2.2)
    if label:
        out += mono(x, y + 3.5, label, size=7.5, fill="#dddddd", anchor="middle")
    return out


def buzzer(x, y, r=14) -> str:
    out = circle(x, y, r, fill="url(#gPlastic)", stroke="#000", sw=0.9, extra='filter="url(#softShadow)"')
    out += circle(x, y, 2.6, fill="#000", stroke="none")
    out += circle(x, y, r * 0.6, fill="none", stroke="#555", sw=0.7)
    return out


def esp32_module(x, y, w=118, h=82) -> str:
    """ESP32-S3-WROOM-1 metal can with the PCB antenna zone on one short edge."""
    out = rrect(x, y, w, h, r=3, fill="#cfd3d7", stroke="#6a6f74", sw=1, extra='filter="url(#softShadow)"')
    # antenna zone (top strip)
    out += rrect(x, y, w, 18, r=3, fill="#0f3a25", stroke="#6a6f74", sw=1)
    out += path(f"M{x+8},{y+13} h8 v-7 h8 v7 h8 v-7 h8 v7 h8 v-7 h8 v7 h8 v-7 h8 v7 h8 v-7 h8 v7 h8 v-7 h8 v7",
                stroke=COPPER, sw=1.6)
    # shield can
    out += rrect(x + 6, y + 24, w - 12, h - 30, r=2, fill="url(#gMetal)", stroke="#5c6166", sw=0.9)
    out += text(x + w / 2, y + 46, "ESP32-S3", size=11, weight=700, fill="#1c1c1c", anchor="middle")
    out += text(x + w / 2, y + 60, "WROOM-1  N8R2", size=8, weight=400, fill="#33383d", anchor="middle")
    # castellated pads
    for i in range(10):
        py = y + 26 + i * 5.6
        out += rrect(x - 1.5, py, 3, 3.2, r=0.5, fill=COPPER, stroke="none")
        out += rrect(x + w - 1.5, py, 3, 3.2, r=0.5, fill=COPPER, stroke="none")
    for i in range(14):
        px = x + 8 + i * 7.5
        out += rrect(px, y + h - 1.5, 3.2, 3, r=0.5, fill=COPPER, stroke="none")
    return out


def led_0603(x, y, color="#f4c20d") -> str:
    return rrect(x, y, 6, 4, r=0.8, fill=color, stroke="#8a6a1e", sw=0.5)


# ---------------------------------------------------------------- off-board things
def wall_adapter(x, y, w=150, h=95) -> str:
    """Plug-in power brick, plain white — the thing you bought labelled 12 V 2 A."""
    out = rrect(x, y, w, h, r=10, fill="url(#gAdapter)", stroke="#8c8c8c", sw=1.2, extra='filter="url(#shadow)"')
    # mains pins (Indian round pins) on the back-left, hinted
    out += rrect(x - 12, y + 24, 12, 8, r=3, fill="url(#gMetal)", stroke="#666", sw=0.7)
    out += rrect(x - 12, y + h - 32, 12, 8, r=3, fill="url(#gMetal)", stroke="#666", sw=0.7)
    # label
    out += rrect(x + 16, y + 18, w - 32, h - 36, r=3, fill="#ffffff", stroke="#cfcfcf", sw=0.6)
    out += text(x + w / 2, y + 38, "AC ADAPTER", size=8, weight=700, fill="#444", anchor="middle")
    out += text(x + w / 2, y + 56, "OUTPUT 12 V ⎓ 2 A", size=10.5, weight=700, fill="#1c1c1c", anchor="middle")
    out += text(x + w / 2, y + 70, "⊖ ─ ◎ ─ ⊕  centre positive", size=8, fill="#444", anchor="middle")
    # cable exit
    out += rrect(x + w - 4, y + h / 2 - 5, 10, 10, r=2, fill="#222", stroke="#000", sw=0.6)
    return out


def barrel_plug(x, y, facing="right") -> str:
    """The plug on the end of the adapter cable (5.5 × 2.1 mm)."""
    out = rrect(x, y - 6, 22, 12, r=3, fill="url(#gPlastic)", stroke="#000", sw=0.8)
    if facing == "right":
        out += rrect(x + 22, y - 4, 16, 8, r=2, fill="url(#gMetal)", stroke="#555", sw=0.7)
        out += rrect(x + 36, y - 1.5, 4, 3, r=0.5, fill="#333", stroke="none")
    else:
        out += rrect(x - 16, y - 4, 16, 8, r=2, fill="url(#gMetal)", stroke="#555", sw=0.7)
    return out


def sensor_module(x, y, w=180, h=66, conn_side="right") -> str:
    """DFRobot AI10: a slim bar with two camera lenses and a row of IR LEDs."""
    out = rrect(x, y, w, h, r=6, fill="#1e1e1e", stroke="#000", sw=1.2, extra='filter="url(#shadow)"')
    out += rrect(x + 4, y + 4, w - 8, h - 8, r=4, fill="#2a2a2a", stroke="#111", sw=0.6)
    # two lenses (binocular)
    for cx in (x + w * 0.3, x + w * 0.7):
        out += circle(cx, y + h / 2, 15, fill="#0b0b0b", stroke="#444", sw=1)
        out += circle(cx, y + h / 2, 9, fill="#101a2e", stroke="#2c3e5a", sw=0.8)
        out += circle(cx - 3, y + h / 2 - 3, 2.4, fill="#7fa7d9", stroke="none")
    # IR LED windows
    for i in range(6):
        lx = x + w / 2 - 33 + i * 12
        out += rrect(lx, y + h - 14, 8, 6, r=1.5, fill="#3b1f3f", stroke="#5a2f60", sw=0.5)
    out += text(x + w / 2, y + 14, "AI10  palm-vein sensor", size=8.5, weight=700, fill="#cccccc", anchor="middle")
    # 4-pin connector on one end
    cx = x + w - 2 if conn_side == "right" else x - 6
    out += rrect(cx, y + h / 2 - 8, 8, 16, r=1.5, fill="#f4f1e8", stroke="#9a9484", sw=0.8)
    return out


def display_module(x, y, w=210, h=150, header_side="bottom") -> str:
    """2.4-inch TFT breakout: red PCB, dark screen, a 14-pin male header along one edge."""
    out = rrect(x, y, w, h, r=5, fill="#a3262b", stroke="#5c1518", sw=1.2, extra='filter="url(#shadow)"')
    # mounting holes
    for (hx, hy) in ((x + 8, y + 8), (x + w - 8, y + 8), (x + 8, y + h - 8), (x + w - 8, y + h - 8)):
        out += circle(hx, hy, 3.2, fill="#ffffff", stroke="#7a1d21", sw=0.8)
    # screen (active area) — 240×320 portrait, drawn landscape here
    sx, sy, sw_, sh = x + 18, y + 16, w - 36, h - 44
    out += rrect(sx, sy, sw_, sh, r=2, fill="url(#gScreen)", stroke="#000", sw=1)
    out += text(sx + sw_ / 2, sy + sh / 2 - 6, "Hold your palm", size=11, weight=700, fill="#e9eef5", anchor="middle")
    out += text(sx + sw_ / 2, sy + sh / 2 + 12, "over the sensor", size=9, fill="#b7c2d0", anchor="middle")
    out += text(x + w / 2, y + h - 18, '2.4" TFT 240×320  ·  ST7789  ·  XPT2046 touch', size=7.5, fill="#f4d9da", anchor="middle")
    return out


def solenoid_lock(x, y, w=170, h=92) -> str:
    """Cabinet solenoid bolt: metal body, bolt sticking out, two wires."""
    out = rrect(x, y + 14, w * 0.62, h - 28, r=5, fill="url(#gSolenoid)", stroke="#4f5459", sw=1.2, extra='filter="url(#shadow)"')
    out += rrect(x + 10, y + 26, w * 0.62 - 20, h - 52, r=3, fill="none", stroke="#6d7378", sw=0.8)
    # bolt
    out += rrect(x + w * 0.62 - 2, y + h / 2 - 9, w * 0.33, 18, r=3, fill="url(#gMetal)", stroke="#555", sw=1)
    out += path(f"M{x + w * 0.95},{y + h / 2 - 9} l10,9 l-10,9 z", stroke="#555", sw=1, fill="#d0d4d8")
    out += text(x + w * 0.31, y + h / 2 + 4, "12 V solenoid", size=9.5, weight=700, fill="#1c1c1c", anchor="middle")
    out += text(x + w * 0.31, y + h / 2 + 17, "0.8 A · intermittent duty", size=7.5, fill="#333", anchor="middle")
    return out


def push_button(x, y, r=22) -> str:
    """Big momentary wall button (the exit button)."""
    out = rrect(x - r - 10, y - r - 10, 2 * r + 20, 2 * r + 20, r=8, fill="#ececec", stroke="#9a9a9a", sw=1.2, extra='filter="url(#shadow)"')
    out += circle(x, y, r, fill="#2f8f4e", stroke="#1d5f33", sw=1.5)
    out += circle(x, y, r * 0.7, fill="#3aa655", stroke="none")
    out += text(x, y + 4, "EXIT", size=9, weight=700, fill="#ffffff", anchor="middle")
    return out


def led_5mm(x, y, color="#3aa655", glow=True) -> str:
    out = ""
    if glow:
        out += circle(x, y, 16, fill=color, stroke="none", extra='fill-opacity="0.18"')
    out += path(f"M{x-8},{y+6} v-8 a8 8 0 0 1 16 0 v8 z", stroke="#333", sw=1, fill=color)
    out += rrect(x - 9, y + 6, 18, 3, r=1, fill=color, stroke="#333", sw=0.8)
    # legs: long (anode, +) and short (cathode, −)
    out += line(x - 4, y + 9, x - 4, y + 30, stroke=METAL_DK, sw=1.6)
    out += line(x + 4, y + 9, x + 4, y + 24, stroke=METAL_DK, sw=1.6)
    return out


def laptop(x, y, w=150, h=95) -> str:
    out = rrect(x, y, w, h * 0.72, r=5, fill="#3b3f44", stroke="#1c1c1c", sw=1.1, extra='filter="url(#shadow)"')
    out += rrect(x + 7, y + 6, w - 14, h * 0.72 - 12, r=2, fill="url(#gScreen)", stroke="#000", sw=0.6)
    out += mono(x + 16, y + 24, "$ idf.py flash monitor", size=8, fill="#8fe388")
    out += mono(x + 16, y + 36, "I (312) ai10: NOTE:READY", size=8, fill="#c9d1d9")
    out += rrect(x - 8, y + h * 0.72, w + 16, 9, r=3, fill="url(#gMetal)", stroke="#6a6f74", sw=0.9)
    return out


def usb_serial_dongle(x, y) -> str:
    out = rrect(x, y, 70, 26, r=4, fill="#1f4e79", stroke="#123", sw=1, extra='filter="url(#softShadow)"')
    out += rrect(x - 14, y + 7, 14, 12, r=2, fill="url(#gMetal)", stroke="#555", sw=0.8)
    out += text(x + 35, y + 16, "USB–serial", size=8.5, weight=700, fill="#ffffff", anchor="middle")
    return out
