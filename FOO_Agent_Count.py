# -*- coding: utf-8 -*-
"""
Flaws_Agent_Count.py  —  long-run false-share vs. number of agents
==================================================================

Analytic curve
    π_f(n) = (p + λ) / (p + λ + q + (n – 1) d)

derived in Lemma 2 (effective hazard) and
Proposition 3 (tolerance bound).

This script computes π_f(n) for n = 1 … N_MAX with the
calibrated hazards from Table 1 of the manuscript and plots:

    • orange line  : analytic π_f(n)
    • orange dots  : individual (n, π_f(n)) pairs

It also writes the values to stdout for quick copy-and-paste.
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------
# Configurable appearance
# --------------------------------------------------------------
FONT_SIZE = 12
plt.rcParams.update({
    "font.size": FONT_SIZE,
    "axes.titlesize": FONT_SIZE + 1,
    "axes.labelsize": FONT_SIZE,
    "legend.fontsize": FONT_SIZE - 1,
    "xtick.labelsize": FONT_SIZE - 1,
    "ytick.labelsize": FONT_SIZE - 1,
})

# --------------------------------------------------------------
# 1 · Model parameters  (anchored in Ji 2023 & Zhang 2024)
# --------------------------------------------------------------
p       = 0.02      # intrinsic r → f  (slip)
q       = 0.05      # intrinsic f → r  (self-repair)
lam     = 0.055     # fabrication / hallucination  (λ > q)
d       = 0.19      # cross-network detection (per external agent)
N_MAX   = 15        # evaluate n = 1 … N_MAX

# --------------------------------------------------------------
# 2 · Analytic curve  π_f(n)
# --------------------------------------------------------------
n_vals  = np.arange(1, N_MAX + 1)
pi_f    = (p + lam) / (p + lam + q + (n_vals - 1) * d)

# quick table to console
print("# n   π_f(n)")
for n, val in zip(n_vals, pi_f):
    print(f"{n:2d}  {val:6.4f}")

# --------------------------------------------------------------
# 3 · Plot
# --------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=300)

ax.plot(n_vals, pi_f, color="orange", marker="o", linewidth=2)
ax.set_xlabel("Number of agents  $n$")
ax.set_ylabel("Long-run false share  $\\pi_f(n)$")
ax.set_title("Long-run false share vs. # of cross-detecting agents")
ax.set_ylim(0, pi_f[0] * 1.05)
ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)

# horizontal helper line at 5 %
ax.axhline(0.05, color="gray", linewidth=1.2, linestyle=":",
           label="$\\pi_f = 0.05$")
# annotate the point where π_f < 0.05 first holds
idx_thresh = np.argmax(pi_f < 0.05)
if idx_thresh > 0:
    ax.scatter(n_vals[idx_thresh], pi_f[idx_thresh],
               color="green", zorder=5)
    ax.annotate(f"$n_\\min = {n_vals[idx_thresh]}$",
                xy=(n_vals[idx_thresh], pi_f[idx_thresh]),
                xytext=(n_vals[idx_thresh] + 0.5, pi_f[idx_thresh] + 0.02),
                arrowprops=dict(arrowstyle="->", color="green"))

ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("FOO_Agent_Count.png", dpi=300, bbox_inches="tight")
plt.show()
