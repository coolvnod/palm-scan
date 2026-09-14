#!/usr/bin/env python3
"""Generate palm-scan.kicad_sch from the stock KiCad 9 libraries.

Every pin gets a short wire stub and a net label; the netlist itself lives in
NETLIST (below) and must match ../../docs/NETLIST.md.  Rerun after editing NETLIST:

    python3 gen_schematic.py && kicad-cli sch erc palm-scan.kicad_sch
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path

LIB_DIR = Path("/usr/share/kicad/symbols")
OUT_DIR = Path(__file__).parent
PROJECT = "palm-scan"
ROOT_UUID = "6f2c1a3e-1b1b-4d5e-9f00-0000000000a1"

STUB = 5.08           # wire stub length from pin end to label, mm (4 × 1.27 grid)
GRID = 1.27


# --------------------------------------------------------------------------- #
# Netlist: (lib symbol, reference, value, footprint, {pin_number: net})
# Net "NC" = explicit no-connect flag.  Pins not listed are left floating,
# which ERC reports - so list every pin.
# --------------------------------------------------------------------------- #
@dataclass
class Part:
    lib_id: str
    ref: str
    value: str
    footprint: str
    nets: dict[str, str]
    group: str
    pos: tuple[float, float] = (0.0, 0.0)
    pins: list["Pin"] = field(default_factory=list)


FP = {
    "R": "Resistor_SMD:R_0603_1608Metric",
    "C": "Capacitor_SMD:C_0603_1608Metric",
    "C08": "Capacitor_SMD:C_0805_2012Metric",
    "TERM": "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
    "SW": "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2",
    "R78E": "Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT",
}

esp_nets = {
    "1": "GND", "2": "+3V3", "3": "EN",
    "4": "LOCK_EN", "5": "BUZZER", "6": "EXIT_BTN",
    "10": "SEN_RX", "11": "SEN_TX", "12": "TOUCH_IRQ",
    "13": "USB_D-", "14": "USB_D+",
    "17": "TOUCH_CS", "18": "TFT_CS", "19": "SPI_MOSI", "20": "SPI_SCK",
    "21": "SPI_MISO", "22": "TFT_DC", "23": "TFT_RST",
    "27": "BOOT", "36": "RXD0", "37": "TXD0",
    "39": "LED_OK", "38": "LED_DENY",          # IO1 green, IO2 red
    "7": "USB_DET",                            # IO7: VBUS present (3.0 V via divider)
    "40": "GND", "41": "GND",
}
# every other module pin is a deliberate no-connect (incl. strapping 3/45/46)
for n in range(1, 42):
    esp_nets.setdefault(str(n), "NC")

usbc_nets = {
    "A1": "GND", "A4": "VBUS", "A5": "CC1", "A6": "USB_D+", "A7": "USB_D-",
    "A8": "NC", "A9": "VBUS", "A12": "GND",
    "B1": "GND", "B4": "VBUS", "B5": "CC2", "B6": "USB_D+", "B7": "USB_D-",
    "B8": "NC", "B9": "VBUS", "B12": "GND", "S1": "GND",
}

j4_nets = {
    "1": "+3V3", "2": "GND", "3": "TFT_CS", "4": "TFT_RST", "5": "TFT_DC",
    "6": "SPI_MOSI", "7": "SPI_SCK", "8": "+3V3", "9": "NC",  # SDO never releases MISO; touch owns it
    # module is rated 3.3-5 V; at 3.3 V its outputs (MISO, T_IRQ) can never exceed ESP32 levels
    "10": "SPI_SCK", "11": "TOUCH_CS", "12": "SPI_MOSI", "13": "SPI_MISO",
    "14": "TOUCH_IRQ",
}

PARTS: list[Part] = [
    # --- power in ----------------------------------------------------------
    Part("Connector:Screw_Terminal_01x02", "J1", "12V IN", FP["TERM"],
         {"1": "VIN_12V", "2": "GND"}, "POWER INPUT"),
    Part("Connector:Barrel_Jack", "J8", "DC JACK 5.5x2.1", "Connector_BarrelJack:BarrelJack_Horizontal",
         {"1": "VIN_12V", "2": "GND"}, "POWER INPUT"),           # 1 = centre (+), 2 = sleeve
    Part("Device:Polyfuse", "F1", "MF-MSMF200/16", "Fuse:Fuse_1812_4532Metric",
         {"1": "VIN_12V", "2": "VIN_FUSED"}, "POWER INPUT"),
    Part("Diode:SS34", "D1", "SS34", "Diode_SMD:D_SMA",
         {"1": "+12V", "2": "VIN_FUSED"}, "POWER INPUT"),        # 1=K 2=A
    Part("Device:C_Polarized", "C1", "470uF 25V", "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
         {"1": "+12V", "2": "GND"}, "POWER INPUT"),
    Part("Device:D_TVS", "D7", "SMAJ15A", "Diode_SMD:D_SMA",
         {"1": "+12V", "2": "GND"}, "POWER INPUT"),              # clamps ~24 V, under Q1's 30 V
    Part("Converter_DCDC:R-78E3.3-1.0", "U2", "R-78E3.3-1.0", FP["R78E"],
         {"1": "+12V", "2": "GND", "3": "+3V3"}, "3.3V REGULATOR"),
    Part("Device:C", "C5", "10uF 50V X7R", "Capacitor_SMD:C_1210_3225Metric", {"1": "+12V", "2": "GND"}, "3.3V REGULATOR"),
    Part("Device:C", "C6", "10uF", FP["C08"], {"1": "+3V3", "2": "GND"}, "3.3V REGULATOR"),
    Part("Device:C_Polarized", "C2", "100uF 10V", "Capacitor_SMD:CP_Elec_6.3x5.4",
         {"1": "+3V3", "2": "GND"}, "3.3V REGULATOR"),           # SMD electrolytic/polymer, not MLCC
    Part("Device:R", "R7", "1k", FP["R"], {"1": "+3V3", "2": "LED_A"}, "POWER LED"),
    Part("Device:LED", "D4", "YELLOW", "LED_SMD:LED_0603_1608Metric",
         {"1": "GND", "2": "LED_A"}, "POWER LED"),                # 1=K 2=A
    # panel LEDs live in the enclosure on wires; resistors stay on the board
    Part("Device:R", "R9", "150R", FP["R"], {"1": "LED_OK", "2": "LED_OK_A"}, "STATUS LEDS"),
    Part("Device:R", "R10", "150R", FP["R"], {"1": "LED_DENY", "2": "LED_DENY_A"}, "STATUS LEDS"),
    Part("Connector:Conn_01x03_Pin", "J7", "PANEL LEDS",
         "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
         {"1": "GND", "2": "LED_OK_A", "3": "LED_DENY_A"}, "STATUS LEDS"),
    Part("Converter_DCDC:R-78E5.0-1.0", "U3", "R-78E5.0-1.0", FP["R78E"],
         {"1": "+12V", "2": "GND", "3": "+5V"}, "5V REGULATOR (SENSOR)"),
    Part("Device:C", "C7", "10uF 50V X7R", "Capacitor_SMD:C_1210_3225Metric", {"1": "+12V", "2": "GND"}, "5V REGULATOR (SENSOR)"),
    Part("Device:C", "C8", "10uF", FP["C08"], {"1": "+5V", "2": "GND"}, "5V REGULATOR (SENSOR)"),
    # --- MCU ---------------------------------------------------------------
    Part("RF_Module:ESP32-S3-WROOM-1", "U1", "ESP32-S3-WROOM-1-N8R2",
         "RF_Module:ESP32-S3-WROOM-1", esp_nets, "ESP32-S3 MCU"),
    Part("Device:C", "C3", "100nF", FP["C"], {"1": "+3V3", "2": "GND"}, "ESP32-S3 MCU"),
    Part("Device:R", "R1", "10k", FP["R"], {"1": "+3V3", "2": "EN"}, "RESET & BOOT"),
    Part("Device:C", "C4", "1uF", FP["C"], {"1": "EN", "2": "GND"}, "RESET & BOOT"),
    Part("Switch:SW_Push", "S1", "RESET", FP["SW"], {"1": "EN", "2": "GND"}, "RESET & BOOT"),
    Part("Switch:SW_Push", "S2", "BOOT", FP["SW"], {"1": "BOOT", "2": "GND"}, "RESET & BOOT"),
    Part("Device:C", "C10", "100nF", FP["C"], {"1": "BOOT", "2": "GND"}, "RESET & BOOT"),
    # --- USB ---------------------------------------------------------------
    Part("Connector:USB_C_Receptacle_USB2.0_16P", "J2", "USB-C",
         "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", usbc_nets, "USB-C (PROGRAMMING)"),
    Part("Device:R", "R3", "5.1k", FP["R"], {"1": "CC1", "2": "GND"}, "USB-C (PROGRAMMING)"),
    Part("Device:R", "R4", "5.1k", FP["R"], {"1": "CC2", "2": "GND"}, "USB-C (PROGRAMMING)"),
    Part("Device:R", "R11", "100k", FP["R"], {"1": "VBUS", "2": "USB_DET"}, "USB-C (PROGRAMMING)"),
    Part("Device:R", "R12", "150k", FP["R"], {"1": "USB_DET", "2": "GND"}, "USB-C (PROGRAMMING)"),
    Part("Power_Protection:USBLC6-2SC6", "D3", "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6",
         {"1": "USB_D-", "2": "GND", "3": "USB_D+", "4": "USB_D+", "5": "VBUS", "6": "USB_D-"}, "USB-C (PROGRAMMING)"),
    # --- lock driver -------------------------------------------------------
    Part("Device:R", "R13", "100R", FP["R"], {"1": "LOCK_EN", "2": "LOCK_G"}, "LOCK DRIVER"),  # gate series
    Part("Transistor_FET:AO3400A", "Q1", "AO3400A", "Package_TO_SOT_SMD:SOT-23",
         {"1": "LOCK_G", "2": "GND", "3": "LOCK_SW"}, "LOCK DRIVER"),    # 1=G 2=S 3=D
    Part("Device:R", "R2", "10k", FP["R"], {"1": "LOCK_G", "2": "GND"}, "LOCK DRIVER"),
    Part("Diode:SS34", "D2", "SS54", "Diode_SMD:D_SMA",
         {"1": "+12V", "2": "LOCK_SW"}, "LOCK DRIVER"),              # 1=K 2=A  (flyback)
    Part("Connector:Screw_Terminal_01x02", "J3", "LOCK", FP["TERM"],
         {"1": "+12V", "2": "LOCK_SW"}, "LOCK DRIVER"),
    # --- I/O ---------------------------------------------------------------
    Part("Connector:Conn_01x04_Pin", "CN1", "AI10 SENSOR",
         "Connector_Molex:Molex_PicoBlade_53047-0410_1x04_P1.25mm_Vertical",
         {"1": "GND", "2": "SEN_RX", "3": "SEN_TX", "4": "+5V"}, "PALM SENSOR"),
    Part("Device:C_Polarized", "C12", "100uF 10V", "Capacitor_SMD:CP_Elec_6.3x5.4",
         {"1": "+5V", "2": "GND"}, "PALM SENSOR"),                # feeds the sensor's start-up spike
    Part("Connector:Conn_01x14_Socket", "J4", "DISPLAY ST7789",
         "Connector_PinSocket_2.54mm:PinSocket_1x14_P2.54mm_Vertical", j4_nets, "DISPLAY"),
    Part("Connector:Screw_Terminal_01x02", "J5", "EXIT BTN", FP["TERM"],
         {"1": "EXIT_SW", "2": "GND"}, "EXIT BUTTON"),
    Part("Device:R", "R8", "1k", FP["R"], {"1": "EXIT_SW", "2": "EXIT_BTN"}, "EXIT BUTTON"),
    Part("Device:R", "R6", "10k", FP["R"], {"1": "+3V3", "2": "EXIT_BTN"}, "EXIT BUTTON"),
    Part("Device:C", "C11", "100nF", FP["C"], {"1": "EXIT_BTN", "2": "GND"}, "EXIT BUTTON"),
    Part("Device:R", "R5", "220R", FP["R"], {"1": "BUZZER", "2": "BZ_DRV"}, "BUZZER"),
    Part("Device:Buzzer", "BZ1", "PIEZO", "Buzzer_Beeper:Buzzer_12x9.5RM7.6",
         {"1": "BZ_DRV", "2": "GND"}, "BUZZER"),
    Part("Connector:Conn_01x04_Pin", "J6", "DEBUG UART0",
         "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
         {"1": "+3V3", "2": "TXD0", "3": "RXD0", "4": "GND"}, "DEBUG UART"),
]

# power symbols + PWR_FLAG, wired to a label so every rail has one driver
POWER_RAILS = [("power:+12V", "+12V", True), ("power:+5V", "+5V", False),
               ("power:+3V3", "+3V3", False), ("power:GND", "GND", True),
               ("power:PWR_FLAG", "VIN_12V", False), ("power:PWR_FLAG", "VBUS", False)]

# --------------------------------------------------------------------------- #
# Library parsing
# --------------------------------------------------------------------------- #
@dataclass
class Pin:
    number: str
    x: float          # connection point, lib coords (y up)
    y: float
    angle: int        # direction from connection point toward body
    hidden: bool


def find_block(text: str, header: str) -> str | None:
    """Return the raw balanced S-expr block starting at `header`."""
    i = text.find(header)
    if i < 0:
        return None
    depth, j, in_str = 0, i, False
    while j < len(text):
        c = text[j]
        if c == '"' and text[j - 1] != "\\":
            in_str = not in_str
        elif not in_str:
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return text[i:j + 1]
        j += 1
    raise ValueError(f"unbalanced block at {header}")


_lib_cache: dict[str, str] = {}


def lib_text(lib: str) -> str:
    if lib not in _lib_cache:
        _lib_cache[lib] = (LIB_DIR / f"{lib}.kicad_sym").read_text()
    return _lib_cache[lib]


SYMBOL_SCALE = 1.5    # KLC pins sit on 2.54 mm; x1.5 -> 3.81, still on the 1.27 grid
PRJ_LIB = "palmscan"  # project symbol library holding the scaled copies


def scale_block(block: str, k: float) -> str:
    """Scale all symbol geometry by k (pins, graphics, text sizes)."""
    def two(m):
        return f"({m.group(1)} {fmt(float(m.group(2)) * k)} {fmt(float(m.group(3)) * k)}"
    def one(m):
        return f"({m.group(1)} {fmt(float(m.group(2)) * k)}"
    block = re.sub(r"\((at|xy|start|end|mid|center|size) (-?[\d.]+) (-?[\d.]+)", two, block)
    block = re.sub(r"\((length|radius|offset|width) (-?[\d.]+)", one, block)
    return block


def symbol_block(lib: str, name: str) -> str:
    blk = find_block(lib_text(lib), f'(symbol "{name}"')
    if blk is None:
        raise KeyError(f"{lib}:{name} not in library")
    return scale_block(blk, SYMBOL_SCALE)


PIN_RE = re.compile(
    r'\(pin\s+\w+\s+\w+\s*(?:\(hide yes\)\s*)?\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)'
    r'\s*\(length\s+[\d.]+\)(\s*\(hide yes\))?.*?\(number\s+"([^"]+)"', re.S)


def parse_pins(block: str) -> list[Pin]:
    pins = []
    for m in PIN_RE.finditer(block):
        x, y, ang, hide, num = m.groups()
        pins.append(Pin(num, float(x), float(y), int(ang), hide is not None))
    return pins


def resolve(lib: str, name: str) -> tuple[list[str], list[Pin]]:
    """Return ([flattened symbol block], pins).

    Schematic files cannot use (extends ...); a derived symbol is flattened by
    taking the parent's body, renaming it, and overriding the derived
    symbol's properties.
    """
    blk = symbol_block(lib, name)
    m = re.search(r'\(extends\s+"([^"]+)"\)', blk)
    if not m:
        return [blk.replace(f'(symbol "{name}"', f'(symbol "{PRJ_LIB}:{name}"', 1)], parse_pins(blk)
    parent = m.group(1)
    (pblk,), pins = resolve(lib, parent)
    flat = pblk.replace(f'(symbol "{PRJ_LIB}:{parent}"', f'(symbol "{PRJ_LIB}:{name}"', 1)
    flat = flat.replace(f'(symbol "{parent}_', f'(symbol "{name}_')
    for pm in re.finditer(r'\(property "([^"]+)"', blk):
        pname = pm.group(1)
        dprop = find_block(blk[pm.start():], f'(property "{pname}"')
        if f'(property "{pname}"' in flat:
            flat = flat.replace(find_block(flat, f'(property "{pname}"'), dprop, 1)
        else:
            flat = flat.replace('\n\t\t(symbol "', '\n\t\t' + dprop + '\n\t\t(symbol "', 1)
    return [flat], pins

# --------------------------------------------------------------------------- #
# Emit helpers
# --------------------------------------------------------------------------- #
def uid() -> str:
    return str(uuid.uuid4())


def snap(v: float) -> float:
    return round(round(v / GRID) * GRID, 4)


def snap_for_pins(origin: float, pin_offsets: list[float]) -> float:
    """Snap a symbol origin so that origin + every pin offset lands on GRID.

    Scaled symbols can have pins at half-grid offsets (e.g. 5.715); shifting the
    origin by that residue keeps the pins - the things that must connect - on grid.
    """
    residues = {round((o % GRID), 3) for o in pin_offsets}
    residues = {r if r < GRID / 2 else round(r - GRID, 3) for r in residues}
    if len(residues) != 1:
        return round(origin, 4)          # pins disagree; leave exact, ERC will only warn
    r = residues.pop()
    return round(snap(origin - r) + r, 4)


def fmt(v: float) -> str:
    return f"{v:.4f}".rstrip("0").rstrip(".")


def wire(x1, y1, x2, y2) -> str:
    return (f"\t(wire (pts (xy {fmt(x1)} {fmt(y1)}) (xy {fmt(x2)} {fmt(y2)}))\n"
            f"\t\t(stroke (width 0) (type default)) (uuid \"{uid()}\"))\n")


def label(name: str, x: float, y: float, angle: int) -> str:
    """Global label: connects across sheets (a plain label is sheet-local)."""
    justify = "left" if angle in (0, 90) else "right"
    return (f"\t(global_label \"{name}\" (shape passive) (at {fmt(x)} {fmt(y)} {angle})"
            f" (fields_autoplaced yes)\n"
            f"\t\t(effects (font (size 2 2)) (justify {justify})) (uuid \"{uid()}\")\n"
            f"\t\t(property \"Intersheetrefs\" \"${{INTERSHEET_REFS}}\" (at 0 0 0)"
            f" (effects (font (size 1.27 1.27)) (hide yes))))\n")


def no_connect(x: float, y: float) -> str:
    return f"\t(no_connect (at {fmt(x)} {fmt(y)}) (uuid \"{uid()}\"))\n"


def text(s: str, x: float, y: float, size: float = 2.0, white: bool = False) -> str:
    color = " (color 255 255 255 1)" if white else ""
    return (f"\t(text \"{s}\" (exclude_from_sim no) (at {fmt(x)} {fmt(y)} 0)\n"
            f"\t\t(effects (font (size {size} {size}) (thickness 0.4) (bold yes){color})"
            f" (justify left bottom)) (uuid \"{uid()}\"))\n")


def rect(x1: float, y1: float, x2: float, y2: float, fill: bool) -> str:
    fill_s = "(fill (type color) (color 0 102 170 1))" if fill else "(fill (type none))"
    return (f"\t(rectangle (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)})\n"
            f"\t\t(stroke (width 0.25) (type default) (color 0 102 170 1)) {fill_s} (uuid \"{uid()}\"))\n")


def prop(name: str, val: str, x: float, y: float, hide: bool = False) -> str:
    h = " (hide yes)" if hide else ""
    return (f"\t\t(property \"{name}\" \"{val}\" (at {fmt(x)} {fmt(y)} 0)\n"
            f"\t\t\t(effects (font (size 2 2)){h}))\n")


SHEET_PATH = f"/{ROOT_UUID}"     # set per sub-sheet while emitting


def symbol_instance(lib_id: str, ref: str, value: str, footprint: str,
                    x: float, y: float, pins: list[Pin], top: float, bottom: float) -> str:
    s = (f"\t(symbol (lib_id \"{lib_id}\") (at {fmt(x)} {fmt(y)} 0) (unit 1)\n"
         f"\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n"
         f"\t\t(uuid \"{uid()}\")\n")
    s += prop("Reference", ref, x, y - top - 2.5, hide=ref.startswith("#"))
    s += prop("Value", value, x, y - bottom + 2.5)
    s += prop("Footprint", footprint, x, y, hide=True)
    s += prop("Datasheet", "~", x, y, hide=True)
    s += prop("Description", "", x, y, hide=True)
    for p in pins:
        s += f"\t\t(pin \"{p.number}\" (uuid \"{uid()}\"))\n"
    s += (f"\t\t(instances (project \"{PROJECT}\" (path \"{SHEET_PATH}\""
          f" (reference \"{ref}\") (unit 1))))\n\t)\n")
    return s


# --------------------------------------------------------------------------- #
# Layout: groups are columns; parts stack vertically inside a group.
# Widths include room for a label on each side.
# --------------------------------------------------------------------------- #
def extents(pins: list[Pin]) -> tuple[float, float, float, float]:
    xs = [p.x for p in pins]
    ys = [p.y for p in pins]
    return min(xs), max(xs), max(ys), min(ys)          # left, right, top, bottom (lib y-up)


# Page plan: (sheet file stem, page title, groups on it).  A group that does
# not fit raises, so overflow is a loud failure, not a silently clipped page.
PAGES = [
    ("power_in", "POWER INPUT & POWER LED", ["POWER INPUT", "POWER LED"]),
    ("power_reg", "3.3V & 5V REGULATORS", ["3.3V REGULATOR", "5V REGULATOR (SENSOR)"]),
    ("mcu", "ESP32-S3 MCU", ["ESP32-S3 MCU"]),
    ("reset_boot", "RESET, BOOT & DEBUG UART", ["RESET & BOOT", "DEBUG UART"]),
    ("usb", "USB-C", ["USB-C (PROGRAMMING)"]),
    ("lock", "LOCK DRIVER & SENSOR", ["LOCK DRIVER", "PALM SENSOR"]),
    ("display", "DISPLAY & STATUS LEDS", ["DISPLAY", "STATUS LEDS"]),
    ("exit", "EXIT BUTTON", ["EXIT BUTTON"]),
    ("buzzer", "BUZZER & POWER FLAGS", ["BUZZER", "POWER FLAGS"]),
]
SHEET_UUIDS = {stem: f"6f2c1a3e-1b1b-4d5e-9f00-0000000000b{n}" for n, (stem, _, _) in enumerate(PAGES, 1)}

# A4 landscape, generous spacing
PAPER = "A4"
SHEET_X0, SHEET_X1, SHEET_Y0, SHEET_Y1 = 12.0, 287.0, 14.0, 176.0   # Y1 keeps clear of title block
LABEL_ROOM = 26.0      # stub + global label flag, each side of a part
PART_GAP = 6.0         # vertical gap between stacked parts
COL_GAP = 5.0          # horizontal gap between sub-columns in a box
COL_MAX_H = 135.0      # wrap to a new sub-column inside the box above this
BAR_H = 7.0
BOX_PAD = 5.0
ROW_GAP = 14.0
TITLE_BLOCK_X = 175.0  # A4 title block starts about here


def label_len(net: str) -> float:
    """Approximate length of a 2 mm global label flag along its wire, mm."""
    return STUB + 1.5 * len(net) + 4.0


def vertical_reach(part: Part) -> tuple[float, float]:
    """(above, below): how far stubs+labels on up/down pins extend past the pins."""
    above = below = 0.0
    for pin in part.pins:
        net = part.nets.get(pin.number, "NC")
        if net == "NC":
            continue
        out = (pin.angle + 180) % 360
        if out == 90:
            above = max(above, label_len(net))
        elif out == 270:
            below = max(below, label_len(net))
    return above, below


def part_size(part: Part) -> tuple[float, float]:
    left, right, top, bottom = extents(part.pins)
    above, below = vertical_reach(part)
    return (right - left) + 2 * LABEL_ROOM, (top - bottom) + above + below + PART_GAP


def emit_part(part: Part, top: float, bottom: float) -> str:
    out = symbol_instance(f"{PRJ_LIB}:{part.lib_id.split(':')[1]}", part.ref, part.value, part.footprint,
                          part.pos[0], part.pos[1], part.pins, top, bottom)
    seen: dict[tuple[float, float], str] = {}
    for p in part.pins:
        net = part.nets.get(p.number)
        if net is None:
            raise KeyError(f"{part.ref} pin {p.number} has no net")
        px, py = round(part.pos[0] + p.x, 4), round(part.pos[1] - p.y, 4)
        if (px, py) in seen:                  # stacked pins share one stub
            if seen[(px, py)] != net:
                raise ValueError(f"{part.ref}: stacked pins at {(px, py)} on different nets")
            continue
        seen[(px, py)] = net
        if net == "NC":
            out += no_connect(px, py)
            continue
        d = (p.angle + 180) % 360             # direction away from body
        dx = {0: 1, 180: -1}.get(d, 0)
        dy = {90: -1, 270: 1}.get(d, 0)       # schematic y is down
        ex, ey = round(px + dx * STUB, 4), round(py + dy * STUB, 4)
        out += wire(px, py, ex, ey)
        out += label(net, ex, ey, d)
    return out


def place_group(parts: list[Part], x0: float, y0: float) -> tuple[float, float, str]:
    """Stack parts in sub-columns inside a box at (x0, y0). Returns (w, h, body)."""
    out = ""
    cols: list[list[Part]] = []
    col: list[Part] = []
    col_h = 0.0
    for part in parts:
        _, h = part_size(part)
        if col and col_h + h > COL_MAX_H:
            cols.append(col)
            col, col_h = [], 0.0
        col.append(part)
        col_h += h
    cols.append(col)

    cx = x0 + BOX_PAD
    box_h = 0.0
    for i, col in enumerate(cols):
        col_w = max(part_size(p)[0] for p in col)
        cy = y0 + BAR_H + BOX_PAD + 3.0
        for part in col:
            left, right, top, bottom = extents(part.pins)
            above, below = vertical_reach(part)
            ox = cx + col_w / 2 - (left + right) / 2
            oy = cy + above + top + 3.0
            part.pos = (snap_for_pins(ox, [q.x for q in part.pins]),
                        snap_for_pins(oy, [-q.y for q in part.pins]))
            out += emit_part(part, top, bottom)
            cy = part.pos[1] - bottom + below + PART_GAP
        cx += col_w + (COL_GAP if i < len(cols) - 1 else 0)
        box_h = max(box_h, cy - y0 + BOX_PAD)
    return cx - x0 + BOX_PAD, box_h, out


def power_flags_box(x0: float, y0: float) -> tuple[float, float, str]:
    out = ""
    max_y = y0
    for n, (lib_id, net, flag) in enumerate(POWER_RAILS):
        lib, name = lib_id.split(":")
        _, pins = resolve(lib, name)
        col, row = divmod(n, 3)
        sx, sy = snap(x0 + 12.0 + col * 70.0), snap(y0 + BAR_H + 18.0 + row * 28.0)
        is_flag = "PWR_FLAG" in lib_id
        out += symbol_instance(f"{PRJ_LIB}:{name}", f"#FLG{n:02d}" if is_flag else f"#PWR{n:02d}",
                               "PWR_FLAG" if is_flag else net, "", sx, sy, pins, 0, 0)
        out += wire(sx, sy, sx + STUB, sy)
        out += label(net, sx + STUB, sy, 0)
        if flag:
            ex = snap(sx + STUB + 34.0)
            out += symbol_instance(f"{PRJ_LIB}:PWR_FLAG", f"#FLG{n + 10:02d}", "PWR_FLAG", "",
                                   ex, sy, pins, 0, 0)
            out += wire(sx + STUB, sy, ex, sy)
        max_y = max(max_y, sy + 12.0)
    return 150.0, max_y - y0 + BOX_PAD, out


def box(title: str, x: float, y: float, w: float, h: float) -> str:
    return (rect(x, y, x + w, y + h, fill=False)
            + rect(x, y, x + w, y + BAR_H, fill=True)
            + text(title, x + 2.5, y + BAR_H - 1.6, 2.5, white=True))


def layout_page(groups: list[str]) -> str:
    body = ""
    x, y, row_h = SHEET_X0, SHEET_Y0, 0.0
    for title in groups:
        parts = [p for p in PARTS if p.group == title]
        placer = (lambda gx, gy: power_flags_box(gx, gy)) if title == "POWER FLAGS" \
            else (lambda gx, gy: place_group(parts, gx, gy))
        w, h, sub = placer(x, y)
        if x + w > SHEET_X1:                          # wrap to next row and redo
            x, y, row_h = SHEET_X0, y + row_h + ROW_GAP, 0.0
            w, h, sub = placer(x, y)
        # the title block sits bottom-right; boxes left of it may run lower
        y_limit = SHEET_Y1 if x + w > TITLE_BLOCK_X else SHEET_Y1 + 18.0
        if y + h > y_limit or x + w > SHEET_X1:
            raise RuntimeError(f"'{title}' does not fit on the page ({w:.0f}x{h:.0f} at {x:.0f},{y:.0f})")
        body += box(title, x, y, w, h) + sub
        if title == "POWER INPUT":
            body += text("Use J1 OR J8 - never both. Centre pin of J8 is +.", x + 3.0, y + h + 5.0, 1.6)
        x += w + ROW_GAP
        row_h = max(row_h, h)
    return body


def sheet_file(stem: str, title: str, body: str, lib_blocks: dict[str, str], page: int) -> None:
    header = (f"(kicad_sch (version 20250114) (generator \"gen_schematic\") (generator_version \"9.0\")\n"
              f"\t(uuid \"{SHEET_UUIDS.get(stem, ROOT_UUID)}\")\n\t(paper \"{PAPER}\")\n"
              f"\t(title_block (title \"palm-scan Rev 2 - {title}\") (date \"2026-09-13\") (rev \"2\")\n"
              f"\t\t(comment 1 \"Palm-vein door lock - ESP32-S3, MOSFET lock driver, 12 V adapter\"))\n")
    libs = "\t(lib_symbols\n" + "".join(indent(b) for b in lib_blocks.values()) + "\t)\n"
    footer = "\t(embedded_fonts no)\n)\n"
    if stem == PROJECT:
        footer = f"\t(sheet_instances (path \"/\" (page \"1\")))\n" + footer
    (OUT_DIR / f"{stem}.kicad_sch").write_text(header + libs + body + footer)


def sheet_symbol(stem: str, title: str, x: float, y: float, page: int) -> str:
    w, h = 80.0, 22.0
    return (f"\t(sheet (at {fmt(x)} {fmt(y)}) (size {fmt(w)} {fmt(h)}) (exclude_from_sim no)"
            f" (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes)\n"
            f"\t\t(stroke (width 0.25) (type solid)) (fill (color 0 102 170 0.08))\n"
            f"\t\t(uuid \"{SHEET_UUIDS[stem]}\")\n"
            f"\t\t(property \"Sheetname\" \"{title}\" (at {fmt(x)} {fmt(y - 0.8)} 0)"
            f" (effects (font (size 2 2) (bold yes)) (justify left bottom)))\n"
            f"\t\t(property \"Sheetfile\" \"{stem}.kicad_sch\" (at {fmt(x)} {fmt(y + h + 0.8)} 0)"
            f" (effects (font (size 1.27 1.27)) (justify left top)))\n"
            f"\t\t(instances (project \"{PROJECT}\" (path \"/{ROOT_UUID}\" (page \"{page}\"))))\n\t)\n")


def main() -> None:
    global SHEET_PATH
    lib_blocks: dict[str, str] = {}
    for part in PARTS:
        lib, name = part.lib_id.split(":")
        blocks, pins = resolve(lib, name)
        for b in blocks:
            lib_blocks.setdefault(re.match(r'\(symbol "([^"]+)"', b).group(1), b)
        part.pins = [p for p in pins if not p.hidden]
    for lib_id, *_ in POWER_RAILS:
        lib, name = lib_id.split(":")
        for b in resolve(lib, name)[0]:
            lib_blocks.setdefault(re.match(r'\(symbol "([^"]+)"', b).group(1), b)

    planned = {g for _, _, gs in PAGES for g in gs}
    missing = {p.group for p in PARTS} - planned
    if missing:
        raise RuntimeError(f"groups not on any page: {missing}")

    # sub-sheets
    for n, (stem, title, groups) in enumerate(PAGES, start=2):
        SHEET_PATH = f"/{ROOT_UUID}/{SHEET_UUIDS[stem]}"
        body = layout_page(groups)
        sheet_file(stem, title, body, lib_blocks, n)

    # root sheet: one block per page + a short reading guide
    SHEET_PATH = f"/{ROOT_UUID}"
    body = text("palm-scan Rev 2 - palm-vein door lock", 20.0, 30.0, 4.0)
    body += text("ESP32-S3 + DFRobot AI10 palm sensor + 12 V solenoid. Net names are global labels:", 20.0, 40.0, 1.8)
    body += text("the same name on any page is the same wire. See NETLIST.md for the table.", 20.0, 45.0, 1.8)
    for n, (stem, title, _) in enumerate(PAGES, start=2):
        col, row = divmod(n - 2, 3)
        body += sheet_symbol(stem, title, 20.0 + col * 92.0, 55.0 + row * 36.0, n)
    sheet_file(PROJECT, "ROOT", body, {}, 1)
    write_symbol_library(lib_blocks)
    write_project()
    print(f"wrote root + {len(PAGES)} sheets, {len(PARTS)} parts")


def indent(block: str) -> str:
    return "".join("\t\t" + line + "\n" for line in block.splitlines())


def write_symbol_library(lib_blocks: dict[str, str]) -> None:
    """palmscan.kicad_sym: the 2x-scaled symbols, registered in the project sym-lib-table."""
    body = ""
    for key, blk in lib_blocks.items():
        bare = key.split(":", 1)[1]
        body += indent(blk.replace(f'(symbol "{key}"', f'(symbol "{bare}"', 1)).replace("\t\t", "\t", 1)
    (OUT_DIR / f"{PRJ_LIB}.kicad_sym").write_text(
        "(kicad_symbol_lib (version 20241209) (generator \"gen_schematic\") (generator_version \"9.0\")\n"
        + body + ")\n")
    (OUT_DIR / "sym-lib-table").write_text(
        "(sym_lib_table (version 7)\n"
        f"\t(lib (name \"{PRJ_LIB}\")(type \"KiCad\")(uri \"${{KIPRJMOD}}/{PRJ_LIB}.kicad_sym\")"
        "(options \"\")(descr \"palm-scan symbols, 1.5x scaled for readability\"))\n)\n")


def write_project() -> None:
    pro = OUT_DIR / f"{PROJECT}.kicad_pro"
    if not pro.exists():
        pro.write_text('{\n  "meta": {"filename": "%s.kicad_pro", "version": 3},\n'
                       '  "sheets": [["%s", "Root"]]\n}\n' % (PROJECT, ROOT_UUID))


if __name__ == "__main__":
    main()
