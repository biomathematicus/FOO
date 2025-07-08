# -*- coding: utf-8 -*-
"""
Flaws5.py  —  single-network “emergent invalidation” simulation
================================================================

A population of `num_actors` agents holds exactly one of two mutually
exclusive statements

    r : “true”   (state index 0, blue curves)
    f : “false”  (state index 1, red  curves)

At every discrete time-step each statement faces three independent
hazards, all specified *per statement*:

    • intrinsic corruption        r → f  with probability  p
    • intrinsic self-correction   f → r  with probability  q
    • fabrication / hallucination r → f  with probability  λ

The long-run false proportion is

    π_f* = (p + λ) / (p + λ + q)            (see manuscript)

This script draws Monte-Carlo trajectories, averages them, and plots the
empirical mean ± 95 % confidence band against the theoretical fixed
points.
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------
# Configurable appearance
# --------------------------------------------------------------
FONT_SIZE = 16
plt.rcParams.update({
    "font.size": FONT_SIZE,
    "axes.titlesize": FONT_SIZE + 1,
    "axes.labelsize": FONT_SIZE,
    "legend.fontsize": FONT_SIZE - 1,
    "xtick.labelsize": FONT_SIZE - 1,
    "ytick.labelsize": FONT_SIZE - 1,
})

# --------------------------------------------------------------
# 1 · Model parameters – grounded in Ji (2023) & Zhang (2024)
# --------------------------------------------------------------
num_actors   = 20          # population size
p            = 0.02        # intrinsic  r → f  (slip)
q            = 0.05        # intrinsic  f → r  (self-repair)
lambda_rate  = 0.055       # fabrication / hallucination (λ > q)

num_iterations = 100       # time horizon
epochs         = 20        # Monte-Carlo runs
rng            = np.random.default_rng(seed=1973)

# theoretical stationary proportions
pi_f_star = (p + lambda_rate) / (p + lambda_rate + q)   # ≈ 0.60
pi_r_star = 1.0 - pi_f_star

time = np.arange(num_iterations)

# --------------------------------------------------------------
# 2 · One Monte-Carlo epoch → trajectories of PROPORTIONS
# --------------------------------------------------------------
def simulate_epoch() -> tuple[np.ndarray, np.ndarray]:
    """Return two length-`num_iterations` arrays of π_r(t) and π_f(t)."""
    beliefs = rng.choice(["r", "f"], size=num_actors)
    traj_r, traj_f = [], []

    for _ in range(num_iterations):
        mask_r = beliefs == "r"
        mask_f = ~mask_r

        # intrinsic flips
        flip_r_to_f = rng.random(num_actors) < p
        flip_f_to_r = rng.random(num_actors) < q

        # fabrication applies only to current r-statements
        fabricate   = (rng.random(num_actors) < lambda_rate) & mask_r
        flip_r_to_f = flip_r_to_f | fabricate

        # apply flips
        beliefs[mask_r & flip_r_to_f] = "f"
        beliefs[mask_f & flip_f_to_r] = "r"

        traj_r.append(np.count_nonzero(beliefs == "r") / num_actors)
        traj_f.append(np.count_nonzero(beliefs == "f") / num_actors)

    return np.asarray(traj_r), np.asarray(traj_f)

# --------------------------------------------------------------
# 3 · Monte-Carlo ensemble
# --------------------------------------------------------------
all_r, all_f = [], []
for _ in range(epochs):
    r, f = simulate_epoch()
    all_r.append(r)
    all_f.append(f)

all_r = np.vstack(all_r)
all_f = np.vstack(all_f)

# --------------------------------------------------------------
# 4 · Mean and 95 % confidence interval
# --------------------------------------------------------------
def mean_ci(arr: np.ndarray):
    mean = arr.mean(axis=0)
    std  = arr.std(axis=0, ddof=1)
    half = 1.96 * std / np.sqrt(epochs)
    return mean, half

mean_r, ci_r = mean_ci(all_r)
mean_f, ci_f = mean_ci(all_f)

# --------------------------------------------------------------
# 5 · Plot
# --------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.8, 7.68), dpi=100)

ax.plot(time, mean_r, color="blue", label="Mean $\\pi_r$")
ax.fill_between(time, mean_r - ci_r, mean_r + ci_r,
                color="blue", alpha=0.15)
ax.plot(time, mean_f, color="red", label="Mean $\\pi_f$")
ax.fill_between(time, mean_f - ci_f, mean_f + ci_f,
                color="red", alpha=0.15)

ax.axhline(pi_r_star, color="blue", linestyle="--",
           label=f"$\\pi_r^* \\approx {pi_r_star:.2f}$")
ax.axhline(pi_f_star, color="red", linestyle="--",
           label=f"$\\pi_f^* \\approx {pi_f_star:.2f}$")

ax.set_xlabel("Time step")
ax.set_ylabel("Proportion of actors")
ax.set_ylim(0, 1)
ax.set_title(
    "Single-Network Emergent Invalidation Dynamics (proportions)\n"
    f"Monte-Carlo runs = {epochs}")
ax.legend(frameon=False, ncol=2, loc="lower center")

fig.tight_layout()
fig.savefig("FOO_Single-Network.png",
            dpi=300, bbox_inches="tight")
plt.show()

# --------------------------------------------------------------
# 6 · Quick numeric summary
# --------------------------------------------------------------
print(f"Theoretical π_f* ≈ {pi_f_star:.3f}")
print(f"Empirical  π_f(T) mean over epochs ≈ {all_f[:, -1].mean():.3f}")
