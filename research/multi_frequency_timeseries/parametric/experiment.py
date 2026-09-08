"""Walk-forward backtest for the five parametric strategies. At every fold,
each model is refit on the expanding training window and asked for a genuine
multi-step-ahead forecast over the whole fold horizon via its own native
`.get_forecast` / `.forecast` machinery -- no hand-rolled recursion, no
lag features that need future truth. That is the correct, standard way to
evaluate a state-space / ARIMA-family model, and it sidesteps the
recursive-error-compounding failure mode entirely (see the tree-based study
in ../ for what happens when a model has no such native multi-step forecast).
"""
import time
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import data as data_mod
import models as model_mod

warnings.filterwarnings("ignore")

PLOTS_DIR = "plots"
INITIAL_TRAIN = 1000
FOLD_SIZE = 120
N_FOLDS = 4
INCLUDE_TBATS = False  # see README: TBATS's exhaustive model search takes
                        # minutes per fit, which makes repeated walk-forward
                        # refitting impractical in this environment.
DPI = 150
plt.rcParams.update({"figure.dpi": DPI, "savefig.dpi": DPI, "font.size": 10})


def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


def mae(a, b):
    return float(np.mean(np.abs(a - b)))


def active_models():
    return {k: v for k, v in model_mod.MODELS.items() if INCLUDE_TBATS or k != "M4_tbats"}


def run_backtest(df: pd.DataFrame):
    y = df["y"]
    records = []
    fold_predictions = {}

    for fold in range(N_FOLDS):
        train_end = INITIAL_TRAIN + fold * FOLD_SIZE
        test_start, test_end = train_end, train_end + FOLD_SIZE
        y_train = y.iloc[:train_end]
        horizon_index = y.index[test_start:test_end]
        actual = y.loc[horizon_index]

        naive_pred = pd.Series(y_train.iloc[-1], index=horizon_index)
        preds = {"naive": naive_pred}
        for name, cls in active_models().items():
            t0 = time.time()
            model = cls().fit(y_train)
            pred = model.forecast(horizon_index)
            dt = time.time() - t0
            preds[name] = pred
            records.append({"fold": fold, "method": name, "rmse": rmse(actual, pred),
                             "mae": mae(actual, pred), "fit_seconds": dt})
        records.append({"fold": fold, "method": "naive_persistence", "rmse": rmse(actual, naive_pred),
                         "mae": mae(actual, naive_pred), "fit_seconds": 0.0})
        fold_predictions[fold] = {"actual": actual, **preds}
        print(f"fold {fold} done (train_end={train_end})")

    return pd.DataFrame(records), fold_predictions


def plot_metric_bars(results: pd.DataFrame):
    for metric in ["rmse", "mae"]:
        agg = results.groupby("method")[metric].agg(["mean", "std"]).sort_values("mean")
        fig, ax = plt.subplots(figsize=(10, 5.2))
        colors = ["#9aa5b1" if m.startswith("naive") else "#2f6f9f" for m in agg.index]
        ax.barh(agg.index, agg["mean"], xerr=agg["std"].fillna(0), color=colors, capsize=3)
        ax.set_xlabel(metric.upper() + " across walk-forward folds (lower is better)")
        ax.set_title(f"Multi-step-ahead {metric.upper()} by parametric strategy")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        fig.savefig(f"{PLOTS_DIR}/metric_{metric}.png")
        plt.close(fig)


def plot_last_fold_overlay(fold_predictions, fold):
    fp = fold_predictions[fold]
    actual = fp["actual"]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(actual.index, actual.values, color="black", lw=1.6, label="actual", zorder=5)
    palette = {"naive": "#9aa5b1", "M1_ols_harmonic": "#d1495b", "M2_dynamic_harmonic_regression": "#2f6f9f",
               "M3_structural_state_space": "#00798c", "M5_seasonal_arima_weekly_only": "#edae49",
               "M4_tbats": "#66a182"}
    for name, series in fp.items():
        if name == "actual":
            continue
        ax.plot(series.index, series.values, lw=1.1, alpha=0.85, color=palette.get(name), label=name)
    ax.set_title(f"Held-out fold {fold}: actual vs. each strategy's {len(actual)}-day-ahead forecast")
    ax.legend(fontsize=7, ncol=2, loc="upper left")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/last_fold_overlay.png")
    plt.close(fig)


def plot_horizon_error(fold_predictions, fold):
    fp = fold_predictions[fold]
    actual = fp["actual"]
    h = np.arange(1, len(actual) + 1)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    palette = {"naive": "#9aa5b1", "M1_ols_harmonic": "#d1495b", "M2_dynamic_harmonic_regression": "#2f6f9f",
               "M3_structural_state_space": "#00798c", "M5_seasonal_arima_weekly_only": "#edae49",
               "M4_tbats": "#66a182"}
    for name, series in fp.items():
        if name == "actual":
            continue
        err = np.abs(series.values - actual.values)
        ax.plot(h, pd.Series(err).rolling(7, min_periods=1).mean(), color=palette.get(name), label=name,
                 ls="--" if name == "naive" else "-")
    ax.set_xlim(1, len(actual))
    ax.set_xlabel("days ahead of forecast origin")
    ax.set_ylabel("7-day rolling mean absolute error")
    ax.set_title("Does error grow over a 120-day horizon, or stay flat?")
    ax.legend(fontsize=7)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/horizon_error.png")
    plt.close(fig)


def plot_trend_recovery(df):
    """Same origin as the last backtest fold (900 pre-changepoint days, 460
    post-changepoint days in training): by this point M3's stochastic local
    trend has had enough post-changepoint evidence to adapt toward the new,
    slower slope, while M1's single global-regression slope is still an
    average over the whole (mostly pre-changepoint) history and stays biased
    high. This is exactly why M3 beat M1/M2 in the walk-forward backtest.
    """
    import models as mm

    y = df["y"]
    origin = INITIAL_TRAIN + (N_FOLDS - 1) * FOLD_SIZE
    y_train = y.iloc[:origin]
    horizon_index = y.index[origin:origin + 250]

    fig, ax = plt.subplots(figsize=(10, 5.2))
    window = slice(data_mod.CHANGEPOINT - 100, origin + 250)
    ax.plot(df.index[window], df["trend"].values[window], color="black", lw=1.8, label="true trend")
    ax.axvline(y.index[data_mod.CHANGEPOINT], color="gray", ls=":", lw=1, label="changepoint")
    ax.axvline(y.index[origin], color="gray", ls="--", lw=1, label="forecast origin (last backtest fold)")

    for name, cls, color in [("M1_ols_harmonic", mm.OLSHarmonic, "#d1495b"),
                              ("M3_structural_state_space", mm.StructuralTimeSeries, "#00798c")]:
        model = cls().fit(y_train)
        fc_future = model.forecast(horizon_index)
        ax.plot(horizon_index, fc_future.values, lw=1.3, color=color, label=f"{name} forecast")

    ax.set_title("Trend behaviour after a regime change: rigid global slope vs. stochastic local trend")
    ax.legend(fontsize=7)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/trend_recovery_check.png")
    plt.close(fig)


def main():
    import os

    os.makedirs(PLOTS_DIR, exist_ok=True)
    df = data_mod.generate()

    results, fold_predictions = run_backtest(df)
    results.to_csv(f"{PLOTS_DIR}/metrics.csv", index=False)

    summary = results.groupby("method")[["rmse", "mae", "fit_seconds"]].mean().sort_values("rmse")
    print(summary)

    plot_metric_bars(results)
    plot_last_fold_overlay(fold_predictions, N_FOLDS - 1)
    plot_horizon_error(fold_predictions, N_FOLDS - 1)
    plot_trend_recovery(df)

    print("\nPlots written to", PLOTS_DIR)


if __name__ == "__main__":
    main()
