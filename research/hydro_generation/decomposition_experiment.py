"""Walk-forward backtest of joint vs. separate (cascade) fitting. Storage is
never an input to any model here, only to the true simulator. Net demand for
the whole forecast horizon is given (as if handed over by a separate
demand-forecasting process) -- the only thing genuinely being forecast is
water availability, via antecedent rainfall.
"""
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import simulate as sim
import decomposition_models as dm

warnings.filterwarnings("ignore")

PLOTS_DIR = "plots"
INITIAL_TRAIN = 1300
FOLD_SIZE = 100
N_FOLDS = 8
DPI = 150
plt.rcParams.update({"figure.dpi": DPI, "savefig.dpi": DPI, "font.size": 10})

COLORS = {"demand_only": "#9aa5b1", "joint": "#d1495b", "separate_cascade": "#2f6f9f"}


def regime_label(train_end):
    if train_end < sim.DROUGHT_START:
        return "pre-drought"
    if train_end < sim.DROUGHT_END:
        return "drought"
    return "post-drought"


def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


def mae(a, b):
    return float(np.mean(np.abs(a - b)))


def run_backtest(df: pd.DataFrame):
    records = []
    fold_predictions = {}
    for fold in range(N_FOLDS):
        train_end = INITIAL_TRAIN + fold * FOLD_SIZE
        horizon_index = df.index[train_end:train_end + FOLD_SIZE]
        df_train = df.iloc[:train_end]
        actual = df.loc[horizon_index, "generation"]
        demand_forecast = df.loc[horizon_index, "demand"]

        preds = {}
        for name, cls in dm.MODELS.items():
            model = cls().fit(df_train)
            pred = model.forecast(horizon_index, demand_forecast).clip(lower=0)
            preds[name] = pred
            records.append({"fold": fold, "train_end": train_end, "regime": regime_label(train_end),
                             "method": name, "rmse": rmse(actual, pred), "mae": mae(actual, pred)})
        fold_predictions[fold] = {"actual": actual, **preds}
        print(f"fold {fold} (train_end={train_end}, regime={regime_label(train_end)}) done")
    return pd.DataFrame(records), fold_predictions


def plot_metrics_by_regime(results: pd.DataFrame):
    order = ["pre-drought", "drought", "post-drought"]
    methods = ["demand_only", "joint", "separate_cascade"]
    agg = results.groupby(["regime", "method"])["rmse"].mean().unstack("method").reindex(order)[methods]

    fig, ax = plt.subplots(figsize=(9, 5.2))
    x = np.arange(len(order))
    width = 0.8 / len(methods)
    for i, method in enumerate(methods):
        ax.bar(x + i * width, agg[method].values, width=width, label=method, color=COLORS[method])
    ax.set_xticks(x + width * (len(methods) - 1) / 2)
    ax.set_xticklabels(order)
    ax.set_ylabel("mean RMSE (generation units)")
    ax.set_title("Given a demand forecast: joint regression vs. separate cascade")
    ax.legend(fontsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/decomp_rmse_by_regime.png")
    plt.close(fig)


def plot_forecast_from_origin(df, train_end, title, filename, horizon_days=300):
    horizon_index = df.index[train_end:train_end + horizon_days]
    df_train = df.iloc[:train_end]
    actual = df.loc[horizon_index, "generation"]
    demand_forecast = df.loc[horizon_index, "demand"]

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.plot(actual.index, actual.values, color="black", lw=1.6, label="actual generation", zorder=5)
    for name, cls in dm.MODELS.items():
        model = cls().fit(df_train)
        pred = model.forecast(horizon_index, demand_forecast).clip(lower=0)
        ax.plot(pred.index, pred.values, lw=1.3, color=COLORS[name], label=name)
    ax.axvline(df.index[train_end], color="gray", ls="--", lw=1, label="forecast origin")
    ax.set_title(title)
    ax.set_ylabel("generation")
    ax.legend(fontsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/{filename}")
    plt.close(fig)


def plot_ceiling_vs_demand(df, train_end, horizon_days=300):
    """Decompose SeparateCascade's own forecast: what did it think the
    ceiling was vs. the given demand forecast? A joint model has no separate
    ceiling to show -- this diagnostic is unique to the cascade structure."""
    horizon_index = df.index[train_end:train_end + horizon_days]
    df_train = df.iloc[:train_end]
    demand_forecast = df.loc[horizon_index, "demand"]
    model = dm.SeparateCascade().fit(df_train)
    ceiling_hat = model.ceiling_forecast(horizon_index)

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.plot(df.index[train_end:train_end + horizon_days], df["generation"].iloc[train_end:train_end + horizon_days],
             color="black", lw=1.6, label="actual generation")
    ax.plot(horizon_index, demand_forecast.values, color="#edae49", lw=1.2, ls="--", label="given demand forecast")
    ax.plot(horizon_index, ceiling_hat.values, color="#2f6f9f", lw=1.4, label="cascade's water ceiling forecast")
    ax.axvline(df.index[train_end], color="gray", ls="--", lw=1)
    ax.set_title("Separate cascade's two pieces, shown individually")
    ax.legend(fontsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/decomp_ceiling_vs_demand.png")
    plt.close(fig)


def main():
    import os

    os.makedirs(PLOTS_DIR, exist_ok=True)
    df = sim.generate()

    results, fold_predictions = run_backtest(df)
    results.to_csv(f"{PLOTS_DIR}/decomp_metrics.csv", index=False)
    print(results.groupby(["regime", "method"])[["rmse", "mae"]].mean().round(2))

    plot_metrics_by_regime(results)
    plot_forecast_from_origin(df, sim.DROUGHT_START + 200,
                               "200 days into the drought (fold 4's origin): joint vs. separate",
                               "decomp_drought_established_forecast.png")
    plot_ceiling_vs_demand(df, sim.DROUGHT_START + 200)

    print("\nPlots written to", PLOTS_DIR)


if __name__ == "__main__":
    main()
