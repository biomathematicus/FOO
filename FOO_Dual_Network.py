# -*- coding: utf-8 -*-
"""
Flaws7.py  —  cross-network invalidation–detection simulation
=============================================================

Two disjoint discursive networks, N₁ and N₂, exchange messages and
cross-check one another’s statements.  Each statement is subject to

    • intrinsic corruption        r → f  with probability  pₖ
    • intrinsic self-correction   f → r  with probability  qₖ
    • fabrication / hallucination r → f  with hazard λₖ  (per true stmt)
    • external detection          f → r  with probability d_{jk}

Calibrated to the empirical picture in Ji et al. (2023) and
Zhang et al. (2024):

        λ  >  q    and   π_f*^single ≈ 0.60

Choosing  
    p = 0.02 ,  q = 0.05 ,  λ = 0.055  
gives the single-network target.  
Setting d so that λ/d ≈ p/(p+q) (= 0.2857) yields  
    d ≈ 0.19, so π_f*^cross ≈ 0.29 < 0.60.

This script simulates the proportion dynamics and plots mean trajectories
±95 % CI for both networks alongside their theoretical asymptotes.
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------
# Configurable appearance
# --------------------------------------------------------------
FONT_SIZE = 10
plt.rcParams.update({
    "font.size": FONT_SIZE,
    "axes.titlesize": FONT_SIZE + 1,
    "axes.labelsize": FONT_SIZE,
    "legend.fontsize": FONT_SIZE - 1,
    "xtick.labelsize": FONT_SIZE - 1,
    "ytick.labelsize": FONT_SIZE - 1,
})

# --------------------------------------------------------------
# 1 · Model parameters  (same p,q,λ in both networks)
# --------------------------------------------------------------
num_iterations = 100      # simulation horizon
epochs         = 20       # Monte-Carlo runs

# intrinsic flip hazards
p12 = 0.02; q12 = 0.05    # N1 (r → f , f → r)
p21 = 0.02; q21 = 0.05    # N2

# fabrication hazards (per true statement)
lambda1 = 0.055           # N1
lambda2 = 0.055           # N2

# cross-network detection probabilities
d12 = 0.19                # N2 detects falsehoods in N1
d21 = 0.19                # N1 detects falsehoods in N2

rng  = np.random.default_rng(seed=42)
time = np.arange(num_iterations + 1)

# --------------------------------------------------------------
# 2 · Monte-Carlo epoch simulator (returns PROPORTIONS)
# --------------------------------------------------------------
def simulate_epoch():
    """Return four trajectories of proportions: (π_T1, π_F1, π_T2, π_F2)."""
    # initialise with non-degenerate counts
    T1, F1 = rng.integers(10, 15, size=2)
    T2, F2 = rng.integers(10, 15, size=2)

    traj_T1, traj_F1, traj_T2, traj_F2 = [], [], [], []

    for _ in range(num_iterations + 1):
        total1 = T1 + F1
        total2 = T2 + F2
        traj_T1.append(T1 / total1)
        traj_F1.append(F1 / total1)
        traj_T2.append(T2 / total2)
        traj_F2.append(F2 / total2)

        # ---------- stochastic draws ----------
        # N1
        X1  = rng.poisson(lambda1 * T1)          # fabrication
        Y12 = rng.binomial(F1, d12)              # cross-detection
        Z1  = rng.binomial(T1, p12)              # intrinsic r → f
        W1  = rng.binomial(F1, q12)              # intrinsic f → r

        # N2
        X2  = rng.poisson(lambda2 * T2)
        Y21 = rng.binomial(F2, d21)
        Z2  = rng.binomial(T2, p21)
        W2  = rng.binomial(F2, q21)

        # ---------- updates (non-negative guard) ----------
        T1 = max(T1 - Z1 + W1, 0)
        F1 = max(F1 + X1 + Z1 - W1 - Y12, 0)
        T2 = max(T2 - Z2 + W2, 0)
        F2 = max(F2 + X2 + Z2 - W2 - Y21, 0)

    return (np.asarray(traj_T1), np.asarray(traj_F1),
            np.asarray(traj_T2), np.asarray(traj_F2))

# --------------------------------------------------------------
# 3 · Monte-Carlo ensemble
# --------------------------------------------------------------
all_T1p, all_F1p, all_T2p, all_F2p = [], [], [], []
for _ in range(epochs):
    T1p, F1p, T2p, F2p = simulate_epoch()
    all_T1p.append(T1p)
    all_F1p.append(F1p)
    all_T2p.append(T2p)
    all_F2p.append(F2p)

all_T1p = np.vstack(all_T1p)
all_F1p = np.vstack(all_F1p)
all_T2p = np.vstack(all_T2p)
all_F2p = np.vstack(all_F2p)

# --------------------------------------------------------------
# 4 · Mean and 95 % confidence interval
# --------------------------------------------------------------
def mean_ci(arr: np.ndarray):
    mean = arr.mean(axis=0)
    std  = arr.std(axis=0, ddof=1)
    half = 1.96 * std / np.sqrt(epochs)
    return mean, half

mean_T1p, ci_T1p = mean_ci(all_T1p)
mean_F1p, ci_F1p = mean_ci(all_F1p)
mean_T2p, ci_T2p = mean_ci(all_T2p)
mean_F2p, ci_F2p = mean_ci(all_F2p)

# --------------------------------------------------------------
# 5 · Theoretical asymptotes
# --------------------------------------------------------------
F1_star = lambda1 / d12
T1_star = F1_star * (q12 / p12)
F2_star = lambda2 / d21
T2_star = F2_star * (q21 / p21)

prop_T1_star = T1_star / (T1_star + F1_star)
prop_F1_star = F1_star / (T1_star + F1_star)
prop_T2_star = T2_star / (T2_star + F2_star)
prop_F2_star = F2_star / (T2_star + F2_star)

# --------------------------------------------------------------
# 6 · Plot (proportion space)
# --------------------------------------------------------------
fig, axes = plt.subplots(2, 1, figsize=(6.5, 5.5), dpi=300)

def panel(ax, label, mean_Tp, ci_Tp, mean_Fp, ci_Fp, Tp_star, Fp_star):
    ax.plot(time, mean_Tp, color="blue",
            label=rf"$\pi_{{{label},r}}$ mean")
    ax.fill_between(time, mean_Tp - ci_Tp, mean_Tp + ci_Tp,
                    color="blue", alpha=0.15)
    ax.plot(time, mean_Fp, color="red",
            label=rf"$\pi_{{{label},f}}$ mean")
    ax.fill_between(time, mean_Fp - ci_Fp, mean_Fp + ci_Fp,
                    color="red", alpha=0.15)

    ax.axhline(Tp_star, color="blue", linestyle="--", linewidth=1.2,
               label=rf"$\pi_{{{label},r}}^*$")
    ax.axhline(Fp_star, color="red", linestyle="--", linewidth=1.2,
               label=rf"$\pi_{{{label},f}}^*$")

    ax.set_ylim(0, 1)
    ax.set_ylabel("Proportion")
    ax.set_title(f"Network $N_{label}$")
    ax.legend(frameon=False, ncol=2)

panel(axes[0], "1", mean_T1p, ci_T1p, mean_F1p, ci_F1p,
      prop_T1_star, prop_F1_star)
panel(axes[1], "2", mean_T2p, ci_T2p, mean_F2p, ci_F2p,
      prop_T2_star, prop_F2_star)

axes[1].set_xlabel("Time step")

fig.suptitle("Dual-Network Invalidation Dynamics (proportions)\n"
             f"Monte-Carlo runs = {epochs}", fontsize=FONT_SIZE + 1, y=0.965)
fig.tight_layout(rect=[0, 0, 1, 0.99])
fig.savefig("FOO_Dual-Network.png", dpi=300, bbox_inches="tight")
plt.show()

# --------------------------------------------------------------
# 7 · Quick numeric summary
# --------------------------------------------------------------
print(f"Theoretical π_f* (single network) ≈ "
      f"{(0.02 + 0.055) / (0.02 + 0.055 + 0.05):.3f}")
print(f"Theoretical π_f* (cross network)  ≈ {F1_star / (T1_star + F1_star):.3f}")
print(f"Empirical  π_f(T)  N1 mean end   ≈ {all_F1p[:, -1].mean():.3f}")
print(f"Empirical  π_f(T)  N2 mean end   ≈ {all_F2p[:, -1].mean():.3f}")
