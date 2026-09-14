#!/usr/bin/env python3
"""Run the lock-driver SPICE simulation through libngspice (the engine inside KiCad) and plot it.

    python3 run_sim.py          # writes lock_driver.png and prints the key numbers

Uses the shared library directly because the `ngspice` CLI is not installed; with the CLI
present, `ngspice -b lock_driver.cir` produces the same .txt files.
"""
from __future__ import annotations

import ctypes as ct
import shutil
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
CIR = HERE / "lock_driver.cir"


def run_ngspice() -> None:
    if shutil.which("ngspice"):
        subprocess.run(["ngspice", "-b", str(CIR)], cwd=HERE, check=True, capture_output=True)
        return
    lib = ct.CDLL("libngspice.so.0")
    log: list[str] = []
    SendChar = ct.CFUNCTYPE(ct.c_int, ct.c_char_p, ct.c_int, ct.c_void_p)
    SendStat = ct.CFUNCTYPE(ct.c_int, ct.c_char_p, ct.c_int, ct.c_void_p)
    Exit = ct.CFUNCTYPE(ct.c_int, ct.c_int, ct.c_bool, ct.c_bool, ct.c_int, ct.c_void_p)

    @SendChar
    def on_char(s, _id, _ud):
        log.append(s.decode(errors="replace"))
        return 0

    @SendStat
    def on_stat(_s, _id, _ud):
        return 0

    @Exit
    def on_exit(_status, _immediate, _quit, _id, _ud):
        return 0

    keep = (on_char, on_stat, on_exit)          # keep callbacks alive
    lib.ngSpice_Init(on_char, on_stat, on_exit, None, None, None, None)
    lib.ngSpice_Command(f"cd {HERE}".encode())
    lib.ngSpice_Command(f"source {CIR}".encode())
    errors = [l for l in log if "error" in l.lower() and "stderr" in l.lower()]
    if errors:
        raise SystemExit("ngspice errors:\n" + "\n".join(errors))
    del keep


def load(name: str) -> dict[str, np.ndarray]:
    raw = np.loadtxt(HERE / name, skiprows=1)
    cols = (HERE / name).read_text().splitlines()[0].split()
    return {c.lower(): raw[:, i] for i, c in enumerate(cols)}


def main() -> None:
    run_ngspice()
    a = load("with_d2.txt")
    b = load("without_d2.txt")
    t = a["time"]

    # ---- numbers worth knowing
    on = (t > 0.5e-3) & (t < 20.5e-3)
    i_ss = a["i(lcoil)"][(t > 18e-3) & (t < 20e-3)].mean()
    v_sw_on = a["v(sw)"][(t > 18e-3) & (t < 20e-3)].mean()
    rds = v_sw_on / i_ss
    p_q1 = v_sw_on * i_ss
    t_rise = t[on][np.argmax(a["i(lcoil)"][on] > 0.632 * i_ss)] - 0.5e-3   # L/R time constant
    vgs = a["v(g)"][(t > 18e-3) & (t < 20e-3)].mean()
    off = t > 20.5e-3
    spike_with = a["v(sw)"][off].max()
    tb = b["time"]
    spike_without = b["v(sw)"][tb > 20.5e-3].max()
    p_av = np.abs(b["v(sw)"] * b["i(vav)"])                          # power dumped into Q1 in avalanche
    e_av = np.trapz(p_av[tb > 20.5e-3], tb[tb > 20.5e-3])
    t_av = tb[(tb > 20.5e-3) & (np.abs(b["i(vav)"]) > 1e-3)]
    dur_av = (t_av.max() - t_av.min()) if len(t_av) else 0.0
    i_d2_peak = a["i(vd2)"][off].max()
    L = 60e-3
    e_coil = 0.5 * L * i_ss**2

    print(f"gate voltage while ON           : {vgs:.2f} V")
    print(f"coil current, steady            : {i_ss:.3f} A   (reaches 63 % after {t_rise*1e3:.1f} ms = L/R)")
    print(f"drain voltage while ON          : {v_sw_on*1e3:.0f} mV  ->  Rds(on) ≈ {rds*1e3:.0f} mΩ, Q1 dissipates {p_q1*1e3:.0f} mW")
    print(f"energy stored in the coil       : {e_coil*1e3:.1f} mJ  (must go somewhere at turn-off)")
    print(f"turn-off spike on LOCK_SW  WITH D2 : {spike_with:.1f} V   (12 V + one diode drop)")
    print(f"turn-off spike on LOCK_SW  NO  D2  : {spike_without:.1f} V   (Q1 avalanches at its 30 V limit)")
    print(f"   energy dumped into Q1 per turn-off : {e_av*1e3:.1f} mJ over {dur_av*1e3:.2f} ms  ->  {e_av/max(dur_av,1e-9):.0f} W average")
    print(f"peak current through D2         : {abs(i_d2_peak):.2f} A  (rated 5 A)")

    # ---- plots
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "Lato", "font.size": 9, "axes.titleweight": "bold"})
    fig, ax = plt.subplots(2, 2, figsize=(11, 7))
    fig.suptitle("palm-scan lock driver — Q1 AO3400A + D2 SS54, 12 V / 15 Ω / 60 mH solenoid  (ngspice)", fontweight="bold")

    z = (t > 0.4999e-3) & (t < 0.5e-3 + 3e-6)
    ax[0, 0].plot((t[z] - 0.5e-3) * 1e6, a["v(io4)"][z], label="IO4 (ESP32 pin)", color="#457b9d")
    ax[0, 0].plot((t[z] - 0.5e-3) * 1e6, a["v(g)"][z], label="LOCK_G (Q1 gate)", color="#d62828")
    ax[0, 0].plot((t[z] - 0.5e-3) * 1e6, a["v(sw)"][z] / 4, label="LOCK_SW ÷ 4", color="#2a9d8f")
    ax[0, 0].set(title="Turn-on, first 3 µs", xlabel="µs after IO4 goes high", ylabel="V"); ax[0, 0].legend(); ax[0, 0].grid(alpha=.3)

    ax[0, 1].plot(t * 1e3, a["i(lcoil)"], color="#d62828")
    ax[0, 1].axhline(i_ss, ls="--", color="#999", lw=.8)
    ax[0, 1].set(title="Coil current — 20 ms pulse", xlabel="ms", ylabel="A"); ax[0, 1].grid(alpha=.3)
    ax[0, 1].annotate(f"{i_ss:.2f} A steady\nL/R = {t_rise*1e3:.1f} ms", xy=(12, i_ss), xytext=(12, i_ss * .6))

    z2 = (t > 20.5e-3 - 20e-6) & (t < 20.5e-3 + 300e-6)
    ax[1, 0].plot((t[z2] - 20.5e-3) * 1e6, a["v(sw)"][z2], color="#2a9d8f", label="LOCK_SW (drain)")
    ax[1, 0].plot((t[z2] - 20.5e-3) * 1e6, a["i(vd2)"][z2] * 10, color="#f77f00", label="D2 current × 10")
    ax[1, 0].axhline(30, ls="--", color="#d62828", lw=.8); ax[1, 0].text(150, 31, "Q1 limit 30 V", color="#d62828")
    ax[1, 0].set(title=f"Turn-off WITH D2 — peak {spike_with:.1f} V", xlabel="µs after IO4 goes low", ylabel="V  /  A×10"); ax[1, 0].legend(); ax[1, 0].grid(alpha=.3)
    ax[1, 0].set_ylim(-2, 40)

    zb = (tb > 20.5e-3 - 50e-6) & (tb < 20.5e-3 + 1500e-6)
    ax[1, 1].plot((tb[zb] - 20.5e-3) * 1e6, b["v(sw)"][zb], color="#d62828", label="LOCK_SW (drain)")
    ax[1, 1].plot((tb[zb] - 20.5e-3) * 1e6, np.abs(b["i(vav)"][zb]) * 10, color="#6a4c93", label="avalanche current × 10")
    ax[1, 1].axhline(30, ls="--", color="#999", lw=.8)
    ax[1, 1].set(title=f"Turn-off WITHOUT D2 — Q1 pinned at {spike_without:.0f} V, absorbs {e_av*1e3:.0f} mJ", xlabel="µs after IO4 goes low", ylabel="V  /  A×10"); ax[1, 1].legend(); ax[1, 1].grid(alpha=.3)
    ax[1, 1].set_ylim(-2, 40)

    fig.tight_layout()
    fig.savefig(HERE / "lock_driver.png", dpi=130)
    print("wrote lock_driver.png")


if __name__ == "__main__":
    main()
