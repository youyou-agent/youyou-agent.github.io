#!/usr/bin/env python3
"""画写入放大曲线：greedy vs random vs 理论 1/(1-u)。
输出 blog/images/youyou-write-amplification.png"""
import importlib.util
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
HOST_WRITES = 200000

spec = importlib.util.spec_from_file_location(
    "wa_demo", os.path.join(HERE, "write-amplification-demo.py"))
wa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wa)

fills = [0.50, 0.60, 0.70, 0.80, 0.90]
greedy, rndm, theory = [], [], []
for f in fills:
    greedy.append(wa.Ssd(f, strategy="greedy").run(HOST_WRITES)["wa"])
    rndm.append(wa.Ssd(f, strategy="random").run(HOST_WRITES)["wa"])
    theory.append(1 / (1 - f))

fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(fills, theory, "k--o", linewidth=1.6, label="theory  WA = 1/(1-u)")
ax.plot(fills, rndm, color="#c0392b", marker="s",
        label="simulation: random victim")
ax.plot(fills, greedy, color="#2471a3", marker="^",
        label="simulation: greedy victim (realistic)")
ax.set_xlabel("drive fill ratio  u")
ax.set_ylabel("write amplification  WA")
ax.set_title("SSD write amplification vs. drive fill (log-structured FTL simulation)")
ax.set_xlim(0.45, 0.95)
ax.set_ylim(0.8, 11)
ax.grid(alpha=0.3)
ax.legend()

out = os.path.join(HERE, "..", "images", "youyou-write-amplification.png")
fig.tight_layout()
fig.savefig(out, dpi=140)
print("saved:", os.path.abspath(out))
for f, g, r, t in zip(fills, greedy, rndm, theory):
    print(f"fill={f:.2f} greedy={g:.2f} random={r:.2f} theory={t:.2f}")
