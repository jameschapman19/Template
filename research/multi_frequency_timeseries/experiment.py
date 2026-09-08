"""Walk-forward backtest comparing five ways of handling a series that mixes a
slow trend/annual cycle with a fast weekly cycle + short-memory noise.

Run: python experiment.py
Writes PNGs to ./plots and a metrics table to ./plots/metrics.csv (a table is
kept alongside the plots only as raw backing data, not as the deliverable).
"""
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

import data as data_mod
import models as model_mod

warnings.filterwarnings("ignore")

PLOTS_DIR = "plots"
INITIAL_TRAIN = 1000
FOLD_SIZE = 90
N_FOLDS = 5
FIGSIZE_WIDE = (10, 5.2)
FIGSIZE_SQUARE = (7.5, 5.2)
DPI = 150
plt.rcParams.update({"figure.dpi": DPI, "savefig.dpi": DPI, "font.size": 10})


def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


def mae(a, b):
    return float(np.mean(np.abs(a - b)))


def mase(actual, pred, naive_errors_mae):
    return mae(actual, pred) / naive_errors_mae


def run_backtest(df: pd.DataFrame):
    y = df["y"]
    records = []
    fold_predictions = {}

    for fold in range(N_FOLDS):
        train_end = INITIAL_TRAIN + fold * FOLD_SIZE
        test_start, test_end = train_end, train_end + FOLD_SIZE
        y_train = y.iloc[:train_end]
        test_index = y.index[test_start:test_end]
        actual = y.loc[test_index]

        naive_pred = y.shift(7).loc[test_index]
        naive_mae = mae(actual, naive_pred)

        preds = {}
        for name, fn in model_mod.METHODS.items():
            pred, _ = fn(y_train, y, test_index)
            preds[name] = pred
            records.append(
                {
                    "fold": fold,
                    "method": name,
                    "rmse": rmse(actual, pred),
                    "mae": mae(actual, pred),
                    "mase": mase(actual, pred, naive_mae),
                }
            )
        records.append(
            {"fold": fold, "method": "naive_seasonal_lag7", "rmse": rmse(actual, naive_pred),
             "mae": naive_mae, "mase": 1.0}
        )
        fold_predictions[fold] = {"actual": actual, "naive": naive_pred, **preds}

    return pd.DataFrame(records), fold_predictions


def plot_metric_bars(results: pd.DataFrame):
    for metric in ["rmse", "mae", "mase"]:
        agg = results.groupby("method")[metric].agg(["mean", "std"]).sort_values("mean")
        fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
        colors = ["#9aa5b1" if m.startswith("naive") else "#2f6f9f" for m in agg.index]
        ax.barh(agg.index, agg["mean"], xerr=agg["std"], color=colors, capsize=3)
        ax.set_xlabel(metric.upper() + " across walk-forward folds (lower is better)")
        ax.set_title(f"Out-of-sample {metric.upper()} by modelling strategy")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        fig.savefig(f"{PLOTS_DIR}/metric_{metric}.png")
        plt.close(fig)


def plot_last_fold_overlay(fold_predictions, fold=N_FOLDS - 1):
    fp = fold_predictions[fold]
    actual = fp["actual"]
    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    ax.plot(actual.index, actual.values, color="black", lw=1.6, label="actual", zorder=5)
    palette = {
        "naive": "#9aa5b1",
        "A_baseline_raw": "#d1495b",
        "B_single_stage_full_features": "#edae49",
        "C_two_stage_smoothed_residual": "#2f6f9f",
        "E_two_stage_slow_feature_residual": "#00798c",
        "D_stl_classical": "#66a182",
    }
    for name, series in fp.items():
        if name == "actual":
            continue
        ax.plot(series.index, series.values, lw=1.1, alpha=0.85, color=palette.get(name), label=name)
    ax.set_title(f"Held-out fold {fold}: actual vs. each strategy's forecast")
    ax.set_ylabel("y")
    ax.legend(fontsize=7, ncol=2, loc="upper left")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/last_fold_overlay.png")
    plt.close(fig)


def plot_small_multiples(fold_predictions, fold=N_FOLDS - 1):
    fp = fold_predictions[fold]
    actual = fp["actual"]
    methods = [k for k in fp if k not in ("actual", "naive")]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
    axes = axes.ravel()
    for ax, name in zip(axes, ["naive"] + methods):
        pred = fp[name]
        ax.plot(actual.index, actual.values, color="black", lw=1.4, label="actual")
        ax.plot(pred.index, pred.values, color="#2f6f9f", lw=1.2, label="forecast")
        ax.set_title(name, fontsize=9)
        ax.tick_params(axis="x", labelrotation=30, labelsize=7)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
    axes[0].legend(fontsize=7)
    fig.suptitle(f"Held-out fold {fold}: each strategy in isolation")
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/small_multiples.png")
    plt.close(fig)


def plot_residual_acf(fold_predictions, fold=N_FOLDS - 1):
    fp = fold_predictions[fold]
    actual = fp["actual"]
    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)
    for ax, name, title in [
        (axes[0], "A_baseline_raw", "Residual ACF: baseline XGBoost on raw series"),
        (axes[1], "C_two_stage_smoothed_residual", "Residual ACF: two-stage smoothed+residual"),
    ]:
        resid = (actual - fp[name]).values
        plot_acf(resid, ax=ax, lags=21, title=title)
        ax.set_ylim(-1, 1)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/residual_acf_comparison.png")
    plt.close(fig)


def plot_decomposition_recovery(df: pd.DataFrame, fold_predictions, fold=N_FOLDS - 1):
    """Sanity-check plot: does the two-stage model's stage-1 output actually
    track the TRUE low-frequency component we simulated?"""
    _, extra = model_mod.two_stage_smoothed_residual(
        df["y"].iloc[: INITIAL_TRAIN + fold * FOLD_SIZE], df["y"], fold_predictions[fold]["actual"].index
    )
    true_low_freq = df["low_freq"].loc[fold_predictions[fold]["actual"].index]
    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    ax.plot(true_low_freq.index, true_low_freq.values, color="black", lw=1.6, label="true low-frequency component")
    ax.plot(extra["stage1"].index, extra["stage1"].values, color="#2f6f9f", lw=1.4, ls="--",
             label="stage-1 model output")
    ax.set_title("Does stage 1 recover the true slow-moving component?")
    ax.legend(fontsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/stage1_recovery_check.png")
    plt.close(fig)


def main():
    import os

    os.makedirs(PLOTS_DIR, exist_ok=True)
    df = data_mod.generate()

    results, fold_predictions = run_backtest(df)
    results.to_csv(f"{PLOTS_DIR}/metrics.csv", index=False)

    summary = results.groupby("method")[["rmse", "mae", "mase"]].mean().sort_values("rmse")
    print(summary)

    plot_metric_bars(results)
    plot_last_fold_overlay(fold_predictions)
    plot_small_multiples(fold_predictions)
    plot_residual_acf(fold_predictions)
    plot_decomposition_recovery(df, fold_predictions)

    print("\nPlots written to", PLOTS_DIR)


if __name__ == "__main__":
    main()
