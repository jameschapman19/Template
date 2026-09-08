"""Walk-forward backtest of the two strategies across pre-drought, drought,
and post-drought regimes, plus one flagship plot: a single forecast made
right at the drought's onset, when the naive calendar model has literally
never seen a drought in its training history and the structural model has
nothing to go on either except today's already-falling storage.
"""
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import simulate as sim
import models as model_mod

warnings.filterwarnings("ignore")

PLOTS_DIR = "plots"
INITIAL_TRAIN = 1300
FOLD_SIZE = 100
N_FOLDS = 8
DPI = 150
plt.rcParams.update({"figure.dpi": DPI, "savefig.dpi": DPI, "font.size": 10})


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

        naive_persistence = pd.Series(df_train["generation"].iloc[-1], index=horizon_index)
        preds = {"naive_persistence": naive_persistence}
        for name, cls in model_mod.MODELS.items():
            model = cls().fit(df_train)
            pred = model.forecast(horizon_index).clip(lower=0)
            preds[name] = pred
            records.append({"fold": fold, "train_end": train_end, "regime": regime_label(train_end),
                             "method": name, "rmse": rmse(actual, pred), "mae": mae(actual, pred)})
        records.append({"fold": fold, "train_end": train_end, "regime": regime_label(train_end),
                         "method": "naive_persistence", "rmse": rmse(actual, naive_persistence),
                         "mae": mae(actual, naive_persistence)})
        fold_predictions[fold] = {"actual": actual, **preds}
        print(f"fold {fold} (train_end={train_end}, regime={regime_label(train_end)}) done")
    return pd.DataFrame(records), fold_predictions


def plot_metrics_by_regime(results: pd.DataFrame):
    order = ["pre-drought", "drought", "post-drought"]
    methods = [m for m in results["method"].unique() if m != "naive_persistence"] + ["naive_persistence"]
    agg = results.groupby(["regime", "method"])["rmse"].mean().unstack("method").reindex(order)[methods]

    fig, ax = plt.subplots(figsize=(9, 5.2))
    x = np.arange(len(order))
    width = 0.8 / len(methods)
    colors = {"M_naive_calendar": "#d1495b", "M_structural_esp": "#2f6f9f", "naive_persistence": "#9aa5b1"}
    for i, method in enumerate(methods):
        ax.bar(x + i * width, agg[method].values, width=width, label=method, color=colors.get(method))
    ax.set_xticks(x + width * (len(methods) - 1) / 2)
    ax.set_xticklabels(order)
    ax.set_ylabel("mean RMSE (generation units)")
    ax.set_title("Forecast error by regime: calendar-only vs. structural (ESP-style)")
    ax.legend(fontsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/rmse_by_regime.png")
    plt.close(fig)


def _plot_forecast_from_origin(df, train_end, title, filename, horizon_days=300):
    horizon_index = df.index[train_end:train_end + horizon_days]
    df_train = df.iloc[:train_end]
    actual = df.loc[horizon_index, "generation"]

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.plot(actual.index, actual.values, color="black", lw=1.6, label="actual generation", zorder=5)
    colors = {"M_naive_calendar": "#d1495b", "M_structural_esp": "#2f6f9f"}
    for name, cls in model_mod.MODELS.items():
        model = cls().fit(df_train)
        pred = model.forecast(horizon_index).clip(lower=0)
        ax.plot(pred.index, pred.values, lw=1.4, color=colors[name], label=name)
    ax.axvline(df.index[train_end], color="gray", ls="--", lw=1, label="forecast origin")
    ax.set_title(title)
    ax.set_ylabel("generation")
    ax.legend(fontsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/{filename}")
    plt.close(fig)


def plot_drought_onset_forecast(df: pd.DataFrame):
    """Forecast made the instant the drought starts. Storage is still near
    its seasonal peak -- the drought hasn't had time to show up in the state
    yet -- so NEITHER model can see it coming. This is ESP's fundamental,
    literature-acknowledged limit: it propagates today's state forward
    correctly, it does not predict tomorrow's rain.
    """
    _plot_forecast_from_origin(
        df, sim.DROUGHT_START,
        "At the drought's first day: neither model can see it coming (storage hasn't moved yet)",
        "drought_onset_forecast.png",
    )


def plot_drought_established_forecast(df: pd.DataFrame):
    """Forecast made 100 days into the drought, once the rain deficit has
    already pulled storage down. Now the two models diverge sharply: the
    structural model is anchored on the already-low true storage and
    projects continued constraint; the calendar-only model has no channel
    for that information and keeps forecasting a normal seasonal cycle.
    """
    _plot_forecast_from_origin(
        df, sim.DROUGHT_START + 100,
        "100 days into the drought: storage has already fallen -- now the models diverge",
        "drought_established_forecast.png",
    )


def plot_storage_projection(df: pd.DataFrame):
    """What does the structural model's storage trajectory look like vs.
    reality? It won't get the day-to-day rain right, but does it stay
    anchored to the truth via the starting condition it was given?"""
    train_end = sim.DROUGHT_START
    horizon_index = df.index[train_end:train_end + 300]
    df_train = df.iloc[:train_end]
    model = model_mod.StructuralESPModel().fit(df_train)
    demand_fc = model.demand_model_.forecast(horizon_index).values
    doy = horizon_index.dayofyear.values
    inflow_fc = model.inflow_climatology_[doy - 1]
    storage_fc, _, _ = sim.simulate_dispatch(inflow_fc, demand_fc, initial_storage=model.storage_origin_)

    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(df.index[train_end - 100:train_end + 300], df["storage"].iloc[train_end - 100:train_end + 300],
             color="black", lw=1.6, label="true storage")
    ax.plot(horizon_index, storage_fc, color="#2f6f9f", lw=1.4, ls="--", label="ESP-style projected storage")
    ax.axhline(sim.RULE_CURVE_FRACTION * sim.CAPACITY, color="gray", ls=":", lw=1, label="rule-curve threshold")
    ax.axvline(df.index[train_end], color="gray", ls="--", lw=1)
    ax.set_title("Storage projection: climatological inflow, but anchored on today's true level")
    ax.legend(fontsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/storage_projection.png")
    plt.close(fig)


def main():
    import os

    os.makedirs(PLOTS_DIR, exist_ok=True)
    df = sim.generate()

    results, fold_predictions = run_backtest(df)
    results.to_csv(f"{PLOTS_DIR}/metrics.csv", index=False)

    print(results.groupby(["regime", "method"])[["rmse", "mae"]].mean().round(2))

    plot_metrics_by_regime(results)
    plot_drought_onset_forecast(df)
    plot_drought_established_forecast(df)
    plot_storage_projection(df)

    print("\nPlots written to", PLOTS_DIR)


if __name__ == "__main__":
    main()
