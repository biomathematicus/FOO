#!/usr/bin/env python3
"""
Generate publication-ready plots for the corrected Section
"Theoretical Validation and Parameter Analysis" of FlawsOfOthers.tex.

Run this script from the same directory as FlawsOfOthers.tex:

    python FOO_generate_plots.py

By default it writes both high-resolution PNG files and vector PDF files:

    FOO_Single-Network.png / .pdf
    FOO_Dual-Network.png   / .pdf
    FOO_Agent_Count.png    / .pdf
    FOO_simulation_summary.csv

The finite-population Monte-Carlo simulations implement the corrected two-state
model

    F_{t+1} = F_t + X_t - C_t,
    X_t | F_t ~ Binomial(N - F_t, a),
    C_t | F_t ~ Binomial(F_t, b),

which preserves T_t + F_t = N pathwise.  The agent-count figure also shows the
continuous-time rate equilibrium

    f*(n) = a / (a + q + (n-1)d),

from the ODE df/dt = a(1-f) - [q+(n-1)d]f.  That rate branch is not simulated
as a discrete stochastic matrix when q+(n-1)d can exceed 1.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


DEFAULT_P = 0.02
DEFAULT_Q = 0.05
DEFAULT_LAMBDA = 0.055
DEFAULT_D = 0.19
DEFAULT_EPSILON = 0.05
DEFAULT_STEPS = 100
DEFAULT_RUNS = 1000
DEFAULT_POPULATION = 1000
DEFAULT_SEED = 20260501
DEFAULT_N_MAX = 30


def configure_matplotlib() -> None:
    """Use a compact, print-friendly Matplotlib configuration."""
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 8,
            "legend.fontsize": 6.7,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "figure.dpi": 150,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def parse_formats(raw: str) -> List[str]:
    formats = [part.strip().lower().lstrip(".") for part in raw.split(",") if part.strip()]
    allowed = {"png", "pdf", "svg"}
    bad = sorted(set(formats) - allowed)
    if bad:
        raise argparse.ArgumentTypeError(f"unsupported format(s): {', '.join(bad)}")
    if not formats:
        raise argparse.ArgumentTypeError("at least one output format is required")
    return formats


def false_production_probability(p: float, lam: float, mode: str) -> float:
    """Return the true-to-false probability a.

    ``mode='additive'`` uses the manuscript's convention a=p+lambda.
    ``mode='independent'`` treats p and lambda as independent one-round
    Bernoulli channels, giving a=1-(1-p)(1-lambda).
    """
    if mode == "additive":
        a = p + lam
    elif mode == "independent":
        a = 1.0 - (1.0 - p) * (1.0 - lam)
    else:
        raise ValueError(f"unknown fabrication mode: {mode!r}")
    if not (0.0 <= a <= 1.0):
        raise ValueError(
            f"false-production probability a={a:.6g} is not in [0,1]. "
            "Choose smaller p/lambda, or use only the continuous-rate theory."
        )
    return a


def exact_bernoulli_correction(q: float, d: float, n_agents: int) -> float:
    """Exact one-round false-to-true correction probability.

    A false item survives internal repair with probability (1-q) and survives
    each of n_agents-1 external detectors with probability (1-d).  Therefore
    the total correction probability is 1-(1-q)(1-d)^(n_agents-1).
    """
    if n_agents < 1:
        raise ValueError("n_agents must be at least 1")
    b = 1.0 - (1.0 - q) * (1.0 - d) ** (n_agents - 1)
    if not (0.0 <= b <= 1.0):
        raise ValueError(f"correction probability b={b:.6g} is not in [0,1]")
    return b


def simulate_two_state(
    *,
    a: float,
    b: float,
    population: int,
    steps: int,
    runs: int,
    rng: np.random.Generator,
    f0: float = 0.0,
) -> np.ndarray:
    """Simulate the fixed-population two-state Markov model.

    Returns an array with shape (runs, steps+1), containing false fractions.
    """
    if not (0.0 <= a <= 1.0 and 0.0 <= b <= 1.0):
        raise ValueError("a and b must be probabilities for discrete simulation")
    if population <= 0 or steps < 0 or runs <= 0:
        raise ValueError("population and runs must be positive; steps must be nonnegative")
    if not (0.0 <= f0 <= 1.0):
        raise ValueError("f0 must be in [0,1]")

    samples = np.empty((runs, steps + 1), dtype=float)
    initial_false = int(round(f0 * population))

    for run in range(runs):
        false_count = initial_false
        samples[run, 0] = false_count / population
        for t in range(1, steps + 1):
            true_count = population - false_count
            new_false = rng.binomial(true_count, a)
            corrected = rng.binomial(false_count, b)
            false_count = false_count + new_false - corrected
            # The binomial construction already keeps this in [0,N]; the clamp
            # protects against impossible states if a caller changes internals.
            false_count = max(0, min(population, false_count))
            samples[run, t] = false_count / population
    return samples


def summarize_trajectory(samples: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return mean and pointwise 95% Monte-Carlo confidence half-width."""
    mean = samples.mean(axis=0)
    if samples.shape[0] == 1:
        ci95 = np.zeros_like(mean)
    else:
        ci95 = 1.96 * samples.std(axis=0, ddof=1) / math.sqrt(samples.shape[0])
    return mean, ci95


def save_figure(fig: plt.Figure, output_dir: Path, stem: str, formats: Sequence[str]) -> None:
    for ext in formats:
        fig.savefig(output_dir / f"{stem}.{ext}")


def add_light_grid(ax: plt.Axes) -> None:
    ax.grid(True, which="major", linewidth=0.4, alpha=0.35)
    ax.set_axisbelow(True)


def plot_single_network(
    *,
    times: np.ndarray,
    samples: np.ndarray,
    f_star: float,
    output_dir: Path,
    formats: Sequence[str],
    show_titles: bool,
) -> None:
    mean_f, ci_f = summarize_trajectory(samples)
    mean_t = 1.0 - mean_f
    ci_t = ci_f

    fig, ax = plt.subplots(figsize=(3.35, 2.35))
    ax.plot(times, mean_t, linewidth=1.8, label="valid")
    ax.fill_between(times, mean_t - ci_t, mean_t + ci_t, alpha=0.18, linewidth=0)
    ax.plot(times, mean_f, linewidth=1.8, label="invalid")
    ax.fill_between(times, mean_f - ci_f, mean_f + ci_f, alpha=0.18, linewidth=0)
    ax.axhline(1.0 - f_star, linestyle="--", linewidth=1.2, label="valid eq.")
    ax.axhline(f_star, linestyle=":", linewidth=1.6, label="invalid eq.")
    ax.set_xlabel("update step")
    ax.set_ylabel("population fraction")
    ax.set_xlim(times[0], times[-1])
    ax.set_ylim(0.0, 1.0)
    if show_titles:
        ax.set_title("Single-network two-state dynamics")
    add_light_grid(ax)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=False, handlelength=2.3, columnspacing=1.1)
    fig.tight_layout()
    save_figure(fig, output_dir, "FOO_Single-Network", formats)
    plt.close(fig)


def plot_dual_network(
    *,
    times: np.ndarray,
    samples_1: np.ndarray,
    samples_2: np.ndarray,
    f_star: float,
    output_dir: Path,
    formats: Sequence[str],
    show_titles: bool,
) -> None:
    mean_1, ci_1 = summarize_trajectory(samples_1)
    mean_2, ci_2 = summarize_trajectory(samples_2)

    fig, ax = plt.subplots(figsize=(3.35, 2.35))
    ax.plot(times, mean_1, linewidth=1.8, label="network 1")
    ax.fill_between(times, mean_1 - ci_1, mean_1 + ci_1, alpha=0.18, linewidth=0)
    ax.plot(times, mean_2, linewidth=1.8, linestyle="--", label="network 2")
    ax.fill_between(times, mean_2 - ci_2, mean_2 + ci_2, alpha=0.18, linewidth=0)
    ax.axhline(f_star, linestyle=":", linewidth=1.6, label="equilibrium")
    ax.set_xlabel("update step")
    ax.set_ylabel("invalid fraction")
    ax.set_xlim(times[0], times[-1])
    ax.set_ylim(0.0, 0.7)
    if show_titles:
        ax.set_title("Two identical networks with external detection")
    add_light_grid(ax)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=False, handlelength=2.3)
    fig.tight_layout()
    save_figure(fig, output_dir, "FOO_Dual-Network", formats)
    plt.close(fig)


def plot_agent_count(
    *,
    a: float,
    q: float,
    d: float,
    epsilon: float,
    n_max: int,
    output_dir: Path,
    formats: Sequence[str],
    show_titles: bool,
) -> Dict[str, float]:
    if n_max < 2:
        raise ValueError("n_max must be at least 2")
    n = np.arange(1, n_max + 1)
    b_disc = 1.0 - (1.0 - q) * (1.0 - d) ** (n - 1)
    f_disc = a / (a + b_disc)
    b_rate = q + (n - 1) * d
    f_rate = a / (a + b_rate)

    required_b = a * (1.0 / epsilon - 1.0)
    discrete_attainable = required_b < 1.0
    if required_b <= q:
        n_min_disc = 1
    elif required_b < 1.0:
        n_min_disc = 1 + math.ceil(
            math.log((1.0 - required_b) / (1.0 - q)) / math.log(1.0 - d)
        )
    else:
        n_min_disc = math.inf

    n_min_rate = max(1, math.ceil(1.0 + (required_b - q) / d))
    f_disc_floor = a / (a + 1.0)

    fig, ax = plt.subplots(figsize=(4.9, 3.15))
    ax.plot(n, f_disc, marker="o", markersize=3.5, linewidth=1.6, label="exact Bernoulli")
    ax.plot(n, f_rate, marker="s", markersize=3.3, linewidth=1.6, linestyle="--", label="continuous rate")
    ax.axhline(epsilon, linestyle=":", linewidth=1.5, label=fr"target $\varepsilon={epsilon:.2f}$")
    ax.axhline(f_disc_floor, linestyle="-.", linewidth=1.1, label="Bernoulli floor")
    if math.isfinite(n_min_rate) and n_min_rate <= n_max:
        ax.axvline(n_min_rate, linestyle=":", linewidth=1.1)
        ax.annotate(
            fr"rate $n_{{\min}}={n_min_rate}$",
            xy=(n_min_rate, a / (a + q + (n_min_rate - 1) * d)),
            xytext=(n_min_rate + 1.0, epsilon + 0.075),
            arrowprops={"arrowstyle": "->", "linewidth": 0.8},
            fontsize=8.5,
        )
    ax.set_xlabel("number of agents")
    ax.set_ylabel("long-run invalid fraction")
    ax.set_xlim(1, n_max)
    ax.set_ylim(0.0, 0.65)
    if show_titles:
        ax.set_title("Agent count under Bernoulli and rate regimes")
    add_light_grid(ax)
    ax.legend(loc="upper right", frameon=False, handlelength=2.3)
    fig.tight_layout()
    save_figure(fig, output_dir, "FOO_Agent_Count", formats)
    plt.close(fig)

    return {
        "required_total_correction_for_epsilon": required_b,
        "discrete_attainable": float(discrete_attainable),
        "n_min_disc": float(n_min_disc) if math.isfinite(n_min_disc) else math.inf,
        "n_min_rate": float(n_min_rate),
        "bernoulli_asymptotic_floor": f_disc_floor,
        "f_rate_at_n_min": a / (a + q + (n_min_rate - 1) * d),
        "f_rate_before_n_min": a / (a + q + max(0, n_min_rate - 2) * d),
    }


def write_summary_csv(path: Path, values: Dict[str, float]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["quantity", "value"])
        for key, value in values.items():
            writer.writerow([key, value])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate corrected FOO simulation plots.")
    parser.add_argument("--output-dir", type=Path, default=Path("."), help="Directory for generated figures.")
    parser.add_argument("--formats", type=parse_formats, default=parse_formats("png,pdf"), help="Comma-separated output formats: png,pdf,svg.")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--population", type=int, default=DEFAULT_POPULATION)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--p", type=float, default=DEFAULT_P)
    parser.add_argument("--q", type=float, default=DEFAULT_Q)
    parser.add_argument("--lambda", dest="lam", type=float, default=DEFAULT_LAMBDA)
    parser.add_argument("--d", type=float, default=DEFAULT_D)
    parser.add_argument("--epsilon", type=float, default=DEFAULT_EPSILON)
    parser.add_argument("--n-max", type=int, default=DEFAULT_N_MAX)
    parser.add_argument(
        "--fabrication-mode",
        choices=["additive", "independent"],
        default="additive",
        help="How to combine p and lambda into the true-to-false probability a.",
    )
    parser.add_argument(
        "--show-titles",
        action="store_true",
        help="Add titles inside figures.  Default is title-free for manuscript use.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_matplotlib()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    a = false_production_probability(args.p, args.lam, args.fabrication_mode)
    b_single = args.q
    b_cross_disc = exact_bernoulli_correction(args.q, args.d, n_agents=2)

    f_single = a / (a + b_single)
    f_cross_disc = a / (a + b_cross_disc)
    f_cross_rate = a / (a + args.q + args.d)

    times = np.arange(args.steps + 1)
    single_samples = simulate_two_state(
        a=a,
        b=b_single,
        population=args.population,
        steps=args.steps,
        runs=args.runs,
        rng=rng,
    )
    dual_samples_1 = simulate_two_state(
        a=a,
        b=b_cross_disc,
        population=args.population,
        steps=args.steps,
        runs=args.runs,
        rng=rng,
    )
    dual_samples_2 = simulate_two_state(
        a=a,
        b=b_cross_disc,
        population=args.population,
        steps=args.steps,
        runs=args.runs,
        rng=rng,
    )

    plot_single_network(
        times=times,
        samples=single_samples,
        f_star=f_single,
        output_dir=args.output_dir,
        formats=args.formats,
        show_titles=args.show_titles,
    )
    plot_dual_network(
        times=times,
        samples_1=dual_samples_1,
        samples_2=dual_samples_2,
        f_star=f_cross_disc,
        output_dir=args.output_dir,
        formats=args.formats,
        show_titles=args.show_titles,
    )
    agent_values = plot_agent_count(
        a=a,
        q=args.q,
        d=args.d,
        epsilon=args.epsilon,
        n_max=args.n_max,
        output_dir=args.output_dir,
        formats=args.formats,
        show_titles=args.show_titles,
    )

    single_mean, single_ci = summarize_trajectory(single_samples)
    dual1_mean, dual1_ci = summarize_trajectory(dual_samples_1)
    dual2_mean, dual2_ci = summarize_trajectory(dual_samples_2)

    summary = {
        "p": args.p,
        "q": args.q,
        "lambda": args.lam,
        "d": args.d,
        "epsilon": args.epsilon,
        "fabrication_mode": math.nan,  # stored as text in next row for CSV readability
        "a": a,
        "b_single": b_single,
        "b_cross_disc": b_cross_disc,
        "f_single_theory": f_single,
        "f_cross_disc_theory": f_cross_disc,
        "f_cross_rate_theory": f_cross_rate,
        "single_terminal_mean": float(single_mean[-1]),
        "single_terminal_ci95": float(single_ci[-1]),
        "dual_network_1_terminal_mean": float(dual1_mean[-1]),
        "dual_network_1_terminal_ci95": float(dual1_ci[-1]),
        "dual_network_2_terminal_mean": float(dual2_mean[-1]),
        "dual_network_2_terminal_ci95": float(dual2_ci[-1]),
        **agent_values,
    }
    # CSV writer can handle strings, so write the text mode separately rather than
    # coercing every value to float.
    summary_csv = args.output_dir / "FOO_simulation_summary.csv"
    with summary_csv.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["quantity", "value"])
        writer.writerow(["fabrication_mode", args.fabrication_mode])
        for key, value in summary.items():
            if key != "fabrication_mode":
                writer.writerow([key, value])

    generated = []
    for stem in ("FOO_Single-Network", "FOO_Dual-Network", "FOO_Agent_Count"):
        for ext in args.formats:
            generated.append(args.output_dir / f"{stem}.{ext}")
    generated.append(summary_csv)

    print("Generated files:")
    for path in generated:
        print(f"  {path}")
    print("\nKey theoretical values:")
    print(f"  a = {a:.6f}")
    print(f"  f_single* = {f_single:.6f}")
    print(f"  f_cross,disc* = {f_cross_disc:.6f}")
    print(f"  f_cross,rate* = {f_cross_rate:.6f}")
    print(f"  required total correction for epsilon = {agent_values['required_total_correction_for_epsilon']:.6f}")
    print(f"  exact Bernoulli attainable? {bool(agent_values['discrete_attainable'])}")
    print(f"  n_min,rate = {int(agent_values['n_min_rate'])}")


if __name__ == "__main__":
    main()
