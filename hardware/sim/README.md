# Circuit simulations (ngspice — the engine inside KiCad)

| File | What |
|---|---|
| `lock_driver.cir` | Solenoid driver: Q1 AO3400A (VDMOS model fitted to the datasheet) + D2 SS54 flyback + 12 V / 15 Ω / 60 mH coil, driven by a 3.3 V GPIO pulse. Two runs: with D2, and without D2 (Q1 avalanche modelled at 32 V). |
| `run_sim.py` | Runs the netlist through `libngspice` (or the `ngspice` CLI if installed), prints the key numbers, writes `lock_driver.png`. |

```bash
python3 run_sim.py
```

Results, Rev 2.4 values (2026-09-14): gate 3.26 V · coil 0.78 A, L/R 3.8 ms · Rds(on) 40 mΩ, 24 mW in Q1 ·
turn-off with D2 peaks 12.4 V (D2 carries 0.79 A) · without D2, Q1 avalanches at 32 V and absorbs 21 mJ per release.

Coil inductance is an assumption (60 mH); measure the real lock and update `LCOIL`.
