#!/usr/bin/env python3
"""
Generate publication-ready Monte-Carlo plots for the corrected
"Theoretical Validation and Parameter Analysis" section of FlawsOfOthers.tex.

Run from the same directory as FlawsOfOthers.tex:

    python FOO_generate_plots.py

Default outputs, written to the current directory:

    FOO_Single-Network.png / .pdf
    FOO_Dual-Network.png   / .pdf
    FOO_Agent_Count.png    / .pdf
    FOO_simulation_summary.csv
    FOO_single_network_trajectory.csv
    FOO_dual_network_trajectory.csv
    FOO_agent_count_summary.csv

The time-series figures plot Monte-Carlo mean trajectories over repeated runs.
The shaded bands are pointwise intervals.  By default the figures show both the 95% confidence interval for the
Monte-Carlo mean trajectory and the empirical central run interval.  To show
only the mean confidence interval, use:

    python FOO_generate_plots.py --interval mean-ci

For only the visibly wider stochastic variation band, use:

    python FOO_generate_plots.py --interval run-interval

Mathematical model
------------------
The finite-population simulations implement the corrected two-state Bernoulli
model

    F_{t+1} = F_t + X_t - C_t,
    X_t | F_t ~ Binomial(N - F_t, a),
    C_t | F_t ~ Binomial(F_t, b),

which preserves T_t + F_t = N pathwise.  The agent-count figure also displays
the continuous-time rate equilibrium

    f*(n) = a / (a + q + (n-1)d),

from the ODE df/dt = a(1-f) - [q+(n-1)d]f.  The rate branch is not simulated
as a discrete stochastic matrix when q+(n-1)d can exceed 1; it is shown as an
analytic ODE-rate curve.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# Defaults used in Patch 11.
# ---------------------------------------------------------------------------
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
DEFAULT_CONFIDENCE = 0.95
DEFAULT_INTERVAL = "both"


@dataclass(frozen=True)
class IntervalSummary:
    """Pointwise trajectory summaries for a samples-by-time array."""

    mean: np.ndarray
    ci_low: np.ndarray
    ci_high: np.ndarray
    run_low: np.ndarray
    run_high: np.ndarray


@dataclass(frozen=True)
class ScalarSummary:
    """Scalar summary for a vector of repeated Monte-Carlo outcomes."""

    mean: float
    ci_low: float
    ci_high: float
    run_low: float
    run_high: float


# ---------------------------------------------------------------------------
# Matplotlib setup and argument parsing.
# ---------------------------------------------------------------------------

def configure_matplotlib() -> None:
    """Configure Matplotlib for compact, print-friendly output.

    The code intentionally does not choose a custom color palette.  Matplotlib's
    default color cycle is used, and confidence bands inherit the corresponding
    line color.
    """
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
            "savefig.pad_inches": 0.035,
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate corrected FOO Monte-Carlo plots with confidence intervals."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory for generated figures and CSV files. Default: current directory.",
    )
    parser.add_argument(
        "--formats",
        type=parse_formats,
        default=parse_formats("png,pdf"),
        help="Comma-separated output formats: png,pdf,svg. Default: png,pdf.",
    )
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS, help="Number of update steps.")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS, help="Independent Monte-Carlo runs.")
    parser.add_argument("--population", type=int, default=DEFAULT_POPULATION, help="Finite population size N.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed.")
    parser.add_argument("--p", type=float, default=DEFAULT_P, help="Intrinsic true-to-false drift p.")
    parser.add_argument("--q", type=float, default=DEFAULT_Q, help="Intrinsic false-to-true repair q.")
    parser.add_argument("--lambda", dest="lam", type=float, default=DEFAULT_LAMBDA, help="Additional false-production drift lambda.")
    parser.add_argument("--d", type=float, default=DEFAULT_D, help="Per-peer external detection/correction probability or rate d.")
    parser.add_argument("--epsilon", type=float, default=DEFAULT_EPSILON, help="Target false share epsilon.")
    parser.add_argument("--n-max", type=int, default=DEFAULT_N_MAX, help="Maximum number of agents in the agent-count plot.")
    parser.add_argument(
        "--fabrication-mode",
        choices=["additive", "independent"],
        default="additive",
        help=(
            "How to combine p and lambda into the true-to-false probability a. "
            "'additive' uses a=p+lambda; 'independent' uses a=1-(1-p)(1-lambda)."
        ),
    )
    parser.add_argument(
        "--initial-false-fraction",
        type=float,
        default=0.0,
        help="Initial false fraction f_0 for all time-series simulations. Default: 0.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=DEFAULT_CONFIDENCE,
        help="Confidence level for pointwise intervals. Default: 0.95.",
    )
    parser.add_argument(
        "--interval",
        choices=["mean-ci", "run-interval", "both", "none"],
        default=DEFAULT_INTERVAL,
        help=(
            "Band/error-bar type. 'mean-ci' is the CI for the Monte-Carlo mean trajectory; "
            "'run-interval' is the empirical central interval across runs; 'both' plots both. "
            f"Default: {DEFAULT_INTERVAL}."
        ),
    )
    parser.add_argument(
        "--skip-agent-monte-carlo",
        action="store_true",
        help="Do not simulate finite-population terminal outcomes for the agent-count plot.",
    )
    parser.add_argument(
        "--show-titles",
        action="store_true",
        help="Add titles inside figures. Default is title-free for manuscript use.",
    )
    legend_group = parser.add_mutually_exclusive_group()
    legend_group.add_argument(
        "--legend-above",
        dest="legend_above",
        action="store_true",
        default=True,
        help="Place legends above the single/dual figures. This is the default for manuscript use.",
    )
    legend_group.add_argument(
        "--legend-inside",
        dest="legend_above",
        action="store_false",
        help="Place legends inside the single/dual figure area.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Model utilities.
# ---------------------------------------------------------------------------

def validate_probability(name: str, value: float) -> None:
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"{name}={value:.6g} must be in [0,1] for Bernoulli simulation")


def false_production_probability(p: float, lam: float, mode: str) -> float:
    """Return the true-to-false probability a."""
    validate_probability("p", p)
    validate_probability("lambda", lam)
    if mode == "additive":
        a = p + lam
    elif mode == "independent":
        a = 1.0 - (1.0 - p) * (1.0 - lam)
    else:
        raise ValueError(f"unknown fabrication mode: {mode!r}")
    validate_probability("a", a)
    return a


def exact_bernoulli_correction(q: float, d: float, n_agents: int) -> float:
    """Exact one-round false-to-true correction probability.

    A false item survives intrinsic repair with probability (1-q) and survives
    each of n_agents-1 external detectors with probability (1-d).  Therefore
    the total one-round correction probability is 1-(1-q)(1-d)^(n_agents-1).
    """
    validate_probability("q", q)
    validate_probability("d", d)
    if n_agents < 1:
        raise ValueError("n_agents must be at least 1")
    b = 1.0 - (1.0 - q) * (1.0 - d) ** (n_agents - 1)
    # Clamp harmless floating round-off such as 1.0000000000000002.
    return float(min(1.0, max(0.0, b)))


def bernoulli_equilibrium(a: float, b: float) -> float:
    """Equilibrium invalid fraction f*=a/(a+b)."""
    if a < 0.0 or b < 0.0 or a + b <= 0.0:
        raise ValueError("a and b must be nonnegative and not both zero")
    return a / (a + b)


def rate_equilibrium(a: float, q: float, d: float, n_agents: int) -> float:
    """Continuous-time additive-rate equilibrium for n agents."""
    if n_agents < 1:
        raise ValueError("n_agents must be at least 1")
    b_rate = q + (n_agents - 1) * d
    return bernoulli_equilibrium(a, b_rate)


# ---------------------------------------------------------------------------
# Monte-Carlo simulation and summaries.
# ---------------------------------------------------------------------------

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
    """Simulate the fixed-population two-state Bernoulli model.

    Returns
    -------
    samples : ndarray, shape (runs, steps+1)
        False fractions F_t/N for each run and time step.
    """
    validate_probability("a", a)
    validate_probability("b", b)
    if population <= 0:
        raise ValueError("population must be positive")
    if runs <= 0:
        raise ValueError("runs must be positive")
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    if not (0.0 <= f0 <= 1.0):
        raise ValueError("initial false fraction must be in [0,1]")

    samples = np.empty((runs, steps + 1), dtype=float)
    false_counts = np.full(runs, int(round(f0 * population)), dtype=np.int64)
    samples[:, 0] = false_counts / population

    for t in range(1, steps + 1):
        true_counts = population - false_counts
        new_false = rng.binomial(true_counts, a)
        corrected = rng.binomial(false_counts, b)
        false_counts = false_counts + new_false - corrected
        samples[:, t] = false_counts / population

    return samples


def z_value(confidence: float) -> float:
    if not (0.0 < confidence < 1.0):
        raise ValueError("confidence must be in (0,1)")
    return NormalDist().inv_cdf(0.5 + confidence / 2.0)


def summarize_trajectory(samples: np.ndarray, confidence: float) -> IntervalSummary:
    """Pointwise mean, mean-CI, and empirical run interval."""
    if samples.ndim != 2:
        raise ValueError("samples must be a 2D array of shape (runs, times)")
    mean = samples.mean(axis=0)
    alpha = 1.0 - confidence
    run_low = np.quantile(samples, alpha / 2.0, axis=0)
    run_high = np.quantile(samples, 1.0 - alpha / 2.0, axis=0)
    if samples.shape[0] == 1:
        ci_low = mean.copy()
        ci_high = mean.copy()
    else:
        sem = samples.std(axis=0, ddof=1) / math.sqrt(samples.shape[0])
        z = z_value(confidence)
        ci_low = mean - z * sem
        ci_high = mean + z * sem
    return IntervalSummary(
        mean=mean,
        ci_low=np.clip(ci_low, 0.0, 1.0),
        ci_high=np.clip(ci_high, 0.0, 1.0),
        run_low=np.clip(run_low, 0.0, 1.0),
        run_high=np.clip(run_high, 0.0, 1.0),
    )


def summarize_scalar(values: np.ndarray, confidence: float) -> ScalarSummary:
    """Mean, mean-CI, and empirical run interval for repeated scalar outcomes."""
    if values.ndim != 1:
        raise ValueError("values must be a 1D array")
    mean = float(values.mean())
    alpha = 1.0 - confidence
    run_low = float(np.quantile(values, alpha / 2.0))
    run_high = float(np.quantile(values, 1.0 - alpha / 2.0))
    if values.size == 1:
        ci_low = ci_high = mean
    else:
        sem = float(values.std(ddof=1) / math.sqrt(values.size))
        z = z_value(confidence)
        ci_low = mean - z * sem
        ci_high = mean + z * sem
    return ScalarSummary(
        mean=mean,
        ci_low=float(min(1.0, max(0.0, ci_low))),
        ci_high=float(min(1.0, max(0.0, ci_high))),
        run_low=float(min(1.0, max(0.0, run_low))),
        run_high=float(min(1.0, max(0.0, run_high))),
    )


# ---------------------------------------------------------------------------
# CSV output.
# ---------------------------------------------------------------------------

def write_rows_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_csv(path: Path, values: Mapping[str, object]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["quantity", "value"])
        for key, value in values.items():
            writer.writerow([key, value])


def trajectory_csv_rows(times: np.ndarray, invalid: IntervalSummary, prefix: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for idx, t in enumerate(times):
        f_mean = float(invalid.mean[idx])
        rows.append(
            {
                "time": int(t),
                f"{prefix}_invalid_mean": f_mean,
                f"{prefix}_invalid_ci_low": float(invalid.ci_low[idx]),
                f"{prefix}_invalid_ci_high": float(invalid.ci_high[idx]),
                f"{prefix}_invalid_run_low": float(invalid.run_low[idx]),
                f"{prefix}_invalid_run_high": float(invalid.run_high[idx]),
                f"{prefix}_valid_mean": 1.0 - f_mean,
                f"{prefix}_valid_ci_low": 1.0 - float(invalid.ci_high[idx]),
                f"{prefix}_valid_ci_high": 1.0 - float(invalid.ci_low[idx]),
                f"{prefix}_valid_run_low": 1.0 - float(invalid.run_high[idx]),
                f"{prefix}_valid_run_high": 1.0 - float(invalid.run_low[idx]),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Plotting helpers.
# ---------------------------------------------------------------------------

def save_figure(fig: plt.Figure, output_dir: Path, stem: str, formats: Sequence[str]) -> List[Path]:
    written: List[Path] = []
    for ext in formats:
        path = output_dir / f"{stem}.{ext}"
        fig.savefig(path)
        written.append(path)
    return written


def add_light_grid(ax: plt.Axes) -> None:
    ax.grid(True, which="major", linewidth=0.4, alpha=0.35)
    ax.set_axisbelow(True)


def plot_interval_line(
    ax: plt.Axes,
    x: np.ndarray,
    summary: IntervalSummary,
    *,
    label: str,
    interval: str,
    linestyle: str = "-",
    linewidth: float = 1.8,
) -> None:
    """Plot mean trajectory with optional interval bands."""
    (line,) = ax.plot(x, summary.mean, linestyle=linestyle, linewidth=linewidth, label=label)
    color = line.get_color()
    if interval in {"run-interval", "both"}:
        ax.fill_between(x, summary.run_low, summary.run_high, color=color, alpha=0.11, linewidth=0)
    if interval in {"mean-ci", "both"}:
        ax.fill_between(x, summary.ci_low, summary.ci_high, color=color, alpha=0.24, linewidth=0)


def place_legend(ax: plt.Axes, *, above: bool, ncol: int = 1) -> None:
    if above:
        ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, 1.02),
            ncol=ncol,
            frameon=False,
            handlelength=2.2,
            columnspacing=1.0,
        )
    else:
        ax.legend(loc="best", frameon=False, handlelength=2.2)


# ---------------------------------------------------------------------------
# Figure generation.
# ---------------------------------------------------------------------------

def plot_single_network(
    *,
    times: np.ndarray,
    samples: np.ndarray,
    f_star: float,
    output_dir: Path,
    formats: Sequence[str],
    confidence: float,
    interval: str,
    show_titles: bool,
    legend_above: bool,
) -> Tuple[List[Path], IntervalSummary]:
    invalid = summarize_trajectory(samples, confidence)
    valid = IntervalSummary(
        mean=1.0 - invalid.mean,
        ci_low=1.0 - invalid.ci_high,
        ci_high=1.0 - invalid.ci_low,
        run_low=1.0 - invalid.run_high,
        run_high=1.0 - invalid.run_low,
    )

    fig, ax = plt.subplots(figsize=(3.35, 2.35))
    plot_interval_line(ax, times, valid, label="valid mean", interval=interval, linestyle="-")
    plot_interval_line(ax, times, invalid, label="invalid mean", interval=interval, linestyle="--")
    ax.axhline(1.0 - f_star, linestyle=":", linewidth=1.2, label="valid eq.")
    ax.axhline(f_star, linestyle="-.", linewidth=1.2, label="invalid eq.")
    ax.set_xlabel("update step")
    ax.set_ylabel("population fraction")
    ax.set_xlim(times[0], times[-1])
    ax.set_ylim(0.0, 1.0)
    if show_titles:
        ax.set_title("Single-network two-state dynamics")
    add_light_grid(ax)
    place_legend(ax, above=legend_above, ncol=2)
    fig.tight_layout()
    paths = save_figure(fig, output_dir, "FOO_Single-Network", formats)
    plt.close(fig)
    return paths, invalid


def plot_dual_network(
    *,
    times: np.ndarray,
    samples_1: np.ndarray,
    samples_2: np.ndarray,
    f_star: float,
    output_dir: Path,
    formats: Sequence[str],
    confidence: float,
    interval: str,
    show_titles: bool,
    legend_above: bool,
) -> Tuple[List[Path], IntervalSummary, IntervalSummary]:
    invalid_1 = summarize_trajectory(samples_1, confidence)
    invalid_2 = summarize_trajectory(samples_2, confidence)

    fig, ax = plt.subplots(figsize=(3.35, 2.35))
    plot_interval_line(ax, times, invalid_1, label="network 1 mean", interval=interval, linestyle="-")
    plot_interval_line(ax, times, invalid_2, label="network 2 mean", interval=interval, linestyle="--")
    ax.axhline(f_star, linestyle=":", linewidth=1.4, label="equilibrium")
    ax.set_xlabel("update step")
    ax.set_ylabel("invalid fraction")
    ax.set_xlim(times[0], times[-1])
    ax.set_ylim(0.0, 0.70)
    if show_titles:
        ax.set_title("Two identical networks with external detection")
    add_light_grid(ax)
    place_legend(ax, above=legend_above, ncol=1)
    fig.tight_layout()
    paths = save_figure(fig, output_dir, "FOO_Dual-Network", formats)
    plt.close(fig)
    return paths, invalid_1, invalid_2


def compute_agent_count_theory(a: float, q: float, d: float, epsilon: float, n_max: int) -> Dict[str, object]:
    if n_max < 1:
        raise ValueError("n_max must be at least 1")
    validate_probability("q", q)
    validate_probability("d", d)
    if not (0.0 < epsilon < 1.0):
        raise ValueError("epsilon must be in (0,1)")

    n_values = np.arange(1, n_max + 1)
    b_disc = np.array([exact_bernoulli_correction(q, d, int(n)) for n in n_values])
    f_disc = a / (a + b_disc)
    b_rate = q + (n_values - 1) * d
    f_rate = a / (a + b_rate)

    required_b = a * (1.0 / epsilon - 1.0)
    if required_b <= q:
        n_min_disc = 1
        disc_attainable = True
    elif required_b < 1.0:
        n_min_disc = 1 + math.ceil(math.log((1.0 - required_b) / (1.0 - q)) / math.log(1.0 - d))
        disc_attainable = True
    else:
        n_min_disc = math.inf
        disc_attainable = False

    n_min_rate = max(1, math.ceil(1.0 + (required_b - q) / d))
    bernoulli_floor = a / (a + 1.0)

    return {
        "n_values": n_values,
        "b_disc": b_disc,
        "f_disc": f_disc,
        "b_rate": b_rate,
        "f_rate": f_rate,
        "required_total_correction_for_epsilon": required_b,
        "discrete_attainable": disc_attainable,
        "n_min_disc": n_min_disc,
        "n_min_rate": n_min_rate,
        "bernoulli_asymptotic_floor": bernoulli_floor,
    }


def simulate_agent_count_terminals(
    *,
    a: float,
    q: float,
    d: float,
    population: int,
    steps: int,
    runs: int,
    rng: np.random.Generator,
    f0: float,
    n_values: np.ndarray,
    confidence: float,
) -> Dict[int, ScalarSummary]:
    terminal: Dict[int, ScalarSummary] = {}
    for n in n_values:
        b = exact_bernoulli_correction(q, d, int(n))
        samples = simulate_two_state(
            a=a,
            b=b,
            population=population,
            steps=steps,
            runs=runs,
            rng=rng,
            f0=f0,
        )
        terminal[int(n)] = summarize_scalar(samples[:, -1], confidence)
    return terminal


def plot_agent_count(
    *,
    theory: Mapping[str, object],
    terminal_summaries: Optional[Mapping[int, ScalarSummary]],
    epsilon: float,
    output_dir: Path,
    formats: Sequence[str],
    interval: str,
    show_titles: bool,
) -> List[Path]:
    n_values = np.asarray(theory["n_values"])
    f_disc = np.asarray(theory["f_disc"])
    f_rate = np.asarray(theory["f_rate"])
    bernoulli_floor = float(theory["bernoulli_asymptotic_floor"])
    n_min_rate = int(theory["n_min_rate"])

    fig, ax = plt.subplots(figsize=(4.9, 3.15))
    ax.plot(n_values, f_disc, marker="o", markersize=3.0, linewidth=1.45, label="Bernoulli equilibrium")
    ax.plot(n_values, f_rate, marker="s", markersize=2.8, linewidth=1.45, linestyle="--", label="continuous-rate equilibrium")

    if terminal_summaries is not None:
        sim_n = np.array(sorted(terminal_summaries.keys()), dtype=int)
        sim_mean = np.array([terminal_summaries[int(n)].mean for n in sim_n])
        if interval in {"run-interval", "both"}:
            low = np.array([terminal_summaries[int(n)].run_low for n in sim_n])
            high = np.array([terminal_summaries[int(n)].run_high for n in sim_n])
            label = "Bernoulli MC terminal mean + run interval"
        else:
            low = np.array([terminal_summaries[int(n)].ci_low for n in sim_n])
            high = np.array([terminal_summaries[int(n)].ci_high for n in sim_n])
            label = "Bernoulli MC terminal mean + CI"
        yerr = np.vstack([sim_mean - low, high - sim_mean])
        ax.errorbar(sim_n, sim_mean, yerr=yerr, fmt=".", markersize=4.0, elinewidth=0.8, capsize=1.8, label=label)

    ax.axhline(epsilon, linestyle=":", linewidth=1.4, label=fr"target $\varepsilon={epsilon:.2f}$")
    ax.axhline(bernoulli_floor, linestyle="-.", linewidth=1.0, label="Bernoulli floor")
    if n_min_rate <= int(n_values[-1]):
        ax.axvline(n_min_rate, linestyle=":", linewidth=1.0)
        ax.annotate(
            fr"rate $n_{{\min}}={n_min_rate}$",
            xy=(n_min_rate, float(f_rate[n_min_rate - 1])),
            xytext=(n_min_rate + 1.0, epsilon + 0.075),
            arrowprops={"arrowstyle": "->", "linewidth": 0.75},
            fontsize=8,
        )
    ax.set_xlabel("number of agents")
    ax.set_ylabel("long-run invalid fraction")
    ax.set_xlim(1, int(n_values[-1]))
    ax.set_ylim(0.0, 0.65)
    if show_titles:
        ax.set_title("Agent count under Bernoulli and rate regimes")
    add_light_grid(ax)
    ax.legend(loc="upper right", frameon=False, handlelength=2.2)
    fig.tight_layout()
    paths = save_figure(fig, output_dir, "FOO_Agent_Count", formats)
    plt.close(fig)
    return paths


# ---------------------------------------------------------------------------
# Main program.
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    configure_matplotlib()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    a = false_production_probability(args.p, args.lam, args.fabrication_mode)
    b_single = args.q
    b_cross_disc = exact_bernoulli_correction(args.q, args.d, n_agents=2)

    f_single = bernoulli_equilibrium(a, b_single)
    f_cross_disc = bernoulli_equilibrium(a, b_cross_disc)
    f_cross_rate = bernoulli_equilibrium(a, args.q + args.d)

    times = np.arange(args.steps + 1)

    single_samples = simulate_two_state(
        a=a,
        b=b_single,
        population=args.population,
        steps=args.steps,
        runs=args.runs,
        rng=rng,
        f0=args.initial_false_fraction,
    )
    dual_samples_1 = simulate_two_state(
        a=a,
        b=b_cross_disc,
        population=args.population,
        steps=args.steps,
        runs=args.runs,
        rng=rng,
        f0=args.initial_false_fraction,
    )
    dual_samples_2 = simulate_two_state(
        a=a,
        b=b_cross_disc,
        population=args.population,
        steps=args.steps,
        runs=args.runs,
        rng=rng,
        f0=args.initial_false_fraction,
    )

    written: List[Path] = []
    paths, single_summary = plot_single_network(
        times=times,
        samples=single_samples,
        f_star=f_single,
        output_dir=args.output_dir,
        formats=args.formats,
        confidence=args.confidence,
        interval=args.interval,
        show_titles=args.show_titles,
        legend_above=args.legend_above,
    )
    written.extend(paths)

    paths, dual1_summary, dual2_summary = plot_dual_network(
        times=times,
        samples_1=dual_samples_1,
        samples_2=dual_samples_2,
        f_star=f_cross_disc,
        output_dir=args.output_dir,
        formats=args.formats,
        confidence=args.confidence,
        interval=args.interval,
        show_titles=args.show_titles,
        legend_above=args.legend_above,
    )
    written.extend(paths)

    theory = compute_agent_count_theory(a, args.q, args.d, args.epsilon, args.n_max)
    n_values = np.asarray(theory["n_values"])
    terminal_summaries: Optional[Dict[int, ScalarSummary]] = None
    if not args.skip_agent_monte_carlo:
        terminal_summaries = simulate_agent_count_terminals(
            a=a,
            q=args.q,
            d=args.d,
            population=args.population,
            steps=args.steps,
            runs=args.runs,
            rng=rng,
            f0=args.initial_false_fraction,
            n_values=n_values,
            confidence=args.confidence,
        )

    written.extend(
        plot_agent_count(
            theory=theory,
            terminal_summaries=terminal_summaries,
            epsilon=args.epsilon,
            output_dir=args.output_dir,
            formats=args.formats,
            interval=args.interval,
            show_titles=args.show_titles,
        )
    )

    # CSV: single trajectory.
    single_csv = args.output_dir / "FOO_single_network_trajectory.csv"
    single_rows = trajectory_csv_rows(times, single_summary, "single")
    write_rows_csv(single_csv, list(single_rows[0].keys()), single_rows)
    written.append(single_csv)

    # CSV: dual trajectory.
    dual_csv = args.output_dir / "FOO_dual_network_trajectory.csv"
    dual_rows: List[Dict[str, object]] = []
    for idx, t in enumerate(times):
        row: Dict[str, object] = {"time": int(t)}
        for prefix, summary in (("network_1", dual1_summary), ("network_2", dual2_summary)):
            row.update(
                {
                    f"{prefix}_invalid_mean": float(summary.mean[idx]),
                    f"{prefix}_invalid_ci_low": float(summary.ci_low[idx]),
                    f"{prefix}_invalid_ci_high": float(summary.ci_high[idx]),
                    f"{prefix}_invalid_run_low": float(summary.run_low[idx]),
                    f"{prefix}_invalid_run_high": float(summary.run_high[idx]),
                }
            )
        dual_rows.append(row)
    write_rows_csv(dual_csv, list(dual_rows[0].keys()), dual_rows)
    written.append(dual_csv)

    # CSV: agent-count theory and Monte-Carlo terminal summaries.
    agent_csv = args.output_dir / "FOO_agent_count_summary.csv"
    agent_rows: List[Dict[str, object]] = []
    for idx, n in enumerate(n_values):
        row = {
            "n_agents": int(n),
            "b_disc": float(np.asarray(theory["b_disc"])[idx]),
            "f_disc_theory": float(np.asarray(theory["f_disc"])[idx]),
            "b_rate": float(np.asarray(theory["b_rate"])[idx]),
            "f_rate_theory": float(np.asarray(theory["f_rate"])[idx]),
        }
        if terminal_summaries is not None:
            s = terminal_summaries[int(n)]
            row.update(
                {
                    "terminal_mean": s.mean,
                    "terminal_ci_low": s.ci_low,
                    "terminal_ci_high": s.ci_high,
                    "terminal_run_low": s.run_low,
                    "terminal_run_high": s.run_high,
                }
            )
        agent_rows.append(row)
    write_rows_csv(agent_csv, list(agent_rows[0].keys()), agent_rows)
    written.append(agent_csv)

    # CSV: compact scalar summary.
    required_b = float(theory["required_total_correction_for_epsilon"])
    n_min_rate = int(theory["n_min_rate"])
    n_min_disc_raw = theory["n_min_disc"]
    n_min_disc = "unattainable" if not math.isfinite(float(n_min_disc_raw)) else int(n_min_disc_raw)
    summary_values: Dict[str, object] = {
        "p": args.p,
        "q": args.q,
        "lambda": args.lam,
        "d": args.d,
        "epsilon": args.epsilon,
        "fabrication_mode": args.fabrication_mode,
        "interval_plotted": args.interval,
        "confidence": args.confidence,
        "population": args.population,
        "runs": args.runs,
        "steps": args.steps,
        "seed": args.seed,
        "a": a,
        "b_single": b_single,
        "b_cross_disc": b_cross_disc,
        "f_single_theory": f_single,
        "f_cross_disc_theory": f_cross_disc,
        "f_cross_rate_theory": f_cross_rate,
        "single_terminal_mean": float(single_summary.mean[-1]),
        "single_terminal_ci_low": float(single_summary.ci_low[-1]),
        "single_terminal_ci_high": float(single_summary.ci_high[-1]),
        "single_terminal_run_low": float(single_summary.run_low[-1]),
        "single_terminal_run_high": float(single_summary.run_high[-1]),
        "dual_network_1_terminal_mean": float(dual1_summary.mean[-1]),
        "dual_network_1_terminal_ci_low": float(dual1_summary.ci_low[-1]),
        "dual_network_1_terminal_ci_high": float(dual1_summary.ci_high[-1]),
        "dual_network_2_terminal_mean": float(dual2_summary.mean[-1]),
        "dual_network_2_terminal_ci_low": float(dual2_summary.ci_low[-1]),
        "dual_network_2_terminal_ci_high": float(dual2_summary.ci_high[-1]),
        "required_total_correction_for_epsilon": required_b,
        "discrete_attainable": bool(theory["discrete_attainable"]),
        "n_min_disc": n_min_disc,
        "n_min_rate": n_min_rate,
        "bernoulli_asymptotic_floor": float(theory["bernoulli_asymptotic_floor"]),
        "f_rate_at_n_min": rate_equilibrium(a, args.q, args.d, n_min_rate),
        "f_rate_before_n_min": rate_equilibrium(a, args.q, args.d, max(1, n_min_rate - 1)),
    }
    summary_csv = args.output_dir / "FOO_simulation_summary.csv"
    write_summary_csv(summary_csv, summary_values)
    written.append(summary_csv)

    print("Generated files:")
    for path in written:
        print(f"  {path}")
    print("\nKey theoretical values:")
    print(f"  a = {a:.6f}")
    print(f"  f_single* = {f_single:.6f}")
    print(f"  f_cross,disc* = {f_cross_disc:.6f}")
    print(f"  f_cross,rate* = {f_cross_rate:.6f}")
    print(f"  required total correction for epsilon = {required_b:.6f}")
    print(f"  exact Bernoulli attainable? {bool(theory['discrete_attainable'])}")
    print(f"  n_min,rate = {n_min_rate}")
    print("\nInterval note:")
    if args.interval == "mean-ci":
        print("  Shaded bands/error bars are pointwise confidence intervals for the Monte-Carlo mean.")
    elif args.interval == "run-interval":
        print("  Shaded bands/error bars are empirical central intervals across individual runs.")
    elif args.interval == "both":
        print("  Figures show both empirical run intervals and confidence intervals for the mean.")
    else:
        print("  No interval bands requested.")


if __name__ == "__main__":
    main()
