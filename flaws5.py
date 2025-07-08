# -*- coding: utf-8 -*-
"""single_network_simulation.py  (Flaws 5, proportion space, CHANGE 1)

Single‑network invalidation dynamics with Monte‑Carlo averaging.
Counts are normalised to proportions so plots lie in the common
range [0,1].  Font size is now controlled by the configurable global
`FONT_SIZE`.
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------
# Configurable appearance
# --------------------------------------------------------------
FONT_SIZE = 16  # ← adjust once; affects all default text sizes
plt.rcParams.update({
    "font.size": FONT_SIZE,
    "axes.titlesize": FONT_SIZE + 1,
    "axes.labelsize": FONT_SIZE,
    "legend.fontsize": FONT_SIZE - 1,
    "xtick.labelsize": FONT_SIZE - 1,
    "ytick.labelsize": FONT_SIZE - 1,
})

# --------------------------------------------------------------
# Model parameters
# --------------------------------------------------------------

num_actors      = 20
p12             = 0.08   # s1 → s2
p21             = 0.045  # s2 → s1

num_iterations  = 100
epochs          = 20
rng             = np.random.default_rng(seed=1973)

time = np.arange(num_iterations)

# --------------------------------------------------------------
# One Monte‑Carlo epoch → trajectories of PROPORTIONS
# --------------------------------------------------------------

def simulate_epoch() -> tuple[np.ndarray, np.ndarray]:
    """Return two length‑`num_iterations` arrays of proportions."""
    beliefs = rng.choice(["s1", "s2"], size=num_actors)
    traj_s1, traj_s2 = [], []

    for _ in range(num_iterations):
        mask_s1 = beliefs == "s1"
        mask_s2 = ~mask_s1
        flips_s1 = rng.random(num_actors) < p12  # s1 → s2
        flips_s2 = rng.random(num_actors) < p21  # s2 → s1
        beliefs[mask_s1 & flips_s1] = "s2"
        beliefs[mask_s2 & flips_s2] = "s1"

        traj_s1.append(np.count_nonzero(beliefs == "s1") / num_actors)
        traj_s2.append(np.count_nonzero(beliefs == "s2") / num_actors)

    return np.asarray(traj_s1), np.asarray(traj_s2)

# --------------------------------------------------------------
# Monte‑Carlo ensemble
# --------------------------------------------------------------

all_s1, all_s2 = [], []
for _ in range(epochs):
    s1, s2 = simulate_epoch()
    all_s1.append(s1)
    all_s2.append(s2)

all_s1 = np.vstack(all_s1)
all_s2 = np.vstack(all_s2)

# --------------------------------------------------------------
# Mean and 95 % confidence interval
# --------------------------------------------------------------

def mean_ci(arr: np.ndarray):
    mean = arr.mean(axis=0)
    std = arr.std(axis=0, ddof=1)
    half = 1.96 * std / np.sqrt(epochs)
    return mean, half

mean_s1, ci_s1 = mean_ci(all_s1)
mean_s2, ci_s2 = mean_ci(all_s2)

# --------------------------------------------------------------
# Theoretical asymptotes in proportion space
# --------------------------------------------------------------

P1_star = p21 / (p12 + p21)
P2_star = p12 / (p12 + p21)

# --------------------------------------------------------------
# Plot
# --------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10.8, 7.68), dpi=100)

ax.plot(time, mean_s1, color="blue", label="Mean $s_1$")
ax.fill_between(time, mean_s1 - ci_s1, mean_s1 + ci_s1,
                color="blue", alpha=0.15)
ax.plot(time, mean_s2, color="red", label="Mean $s_2$")
ax.fill_between(time, mean_s2 - ci_s2, mean_s2 + ci_s2,
                color="red", alpha=0.15)

ax.axhline(P1_star, color="blue", linestyle="--", label="$P_1^{*}$")
ax.axhline(P2_star, color="red", linestyle="--", label="$P_2^{*}$")

ax.set_xlabel("Time step")
ax.set_ylabel("Proportion of actors")
ax.set_ylim(0, 1)
ax.set_title(
    "Single‑Network Invalidation Dynamics (proportions)\n"
    f"Monte‑Carlo runs = {epochs}")
ax.legend(frameon=False, ncol=2, loc="lower center")

fig.tight_layout()
fig.savefig("FOO_Single-Network.png", dpi=300, bbox_inches="tight")
plt.show()
