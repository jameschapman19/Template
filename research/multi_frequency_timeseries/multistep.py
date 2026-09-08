"""Scenario 2: genuine fixed-origin, multi-step-ahead forecasting.

experiment.py's walk-forward backtest is a *rolling one-step* evaluation: at
every test day the model sees the true value of every prior day, including
days inside the "test" window. That's a legitimate and common setup (you get
tomorrow's actual before forecasting the day after), and it structurally
favours any model with a lag_1 feature, since lag_1 is always the truth.

It is NOT the same problem as "forecast the next 90 days from today with
nothing fed back." That fixed-origin case is where naive short-lag models
either can't be scored at all (lag_1..lag_14 don't exist beyond the origin)
or must be run recursively, feeding each step's own prediction back in as
next step's "lag" -- which is exactly how compounding error enters. This
script scores the baseline (A) and the smoothed two-stage model (C) under
that harder, more realistic long-horizon setting and holds every other
feature (calendar, rolling windows) to what was actually knowable at the
origin -- no peeking at the true series past that point for anyone.
"""
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import data as data_mod
import features as feat
import models as model_mod

warnings.filterwarnings("ignore")

PLOTS_DIR = "plots"
TRAIN_END = 1360
HORIZON = 90


def recursive_forecast(model, y_known: pd.Series, horizon_dates, feature_fn):
    """Feed the model's own predictions back in as the lags for later steps.
    y_known already has NaN at every horizon date; we fill them in one at a
    time so feature_fn only ever sees real history or earlier predictions.
    """
    y_work = y_known.copy()
    preds = {}
    for date in horizon_dates:
        x_row = feature_fn(y_work).loc[[date]]
        p = model.predict(x_row)[0]
        y_work.loc[date] = p
        preds[date] = p
    return pd.Series(preds)


def frozen_slow_features(y_full: pd.Series, origin, horizon_dates) -> pd.DataFrame:
    """Deterministic calendar terms (t, annual sin/cos) are legitimately known
    for future dates. Historical-statistic terms (rolling/expanding means)
    are NOT -- computing them naively would use true future y. Freeze them at
    their last value observed at the origin instead.
    """
    X = feat.slow_feature_set(y_full)
    frozen_cols = [c for c in X.columns if c.startswith("roll_mean") or c == "expanding_mean"]
    out = X.loc[horizon_dates].copy()
    out[frozen_cols] = X.loc[origin, frozen_cols].values
    return out


def main():
    df = data_mod.generate()
    y = df["y"]
    y_train = y.iloc[:TRAIN_END]
    origin = y.index[TRAIN_END - 1]
    horizon_dates = y.index[TRAIN_END:TRAIN_END + HORIZON]
    actual = y.loc[horizon_dates]

    _, extra_a = model_mod.baseline_raw(y_train, y, horizon_dates)
    model_a = extra_a["model"]
    _, extra_c = model_mod.two_stage_smoothed_residual(y_train, y, horizon_dates)
    stage1_model, stage2_model = extra_c["stage1_model"], extra_c["stage2_model"]

    y_masked = y.copy()
    y_masked.loc[horizon_dates] = np.nan

    forecast_a = recursive_forecast(model_a, y_masked, horizon_dates, feat.baseline_feature_set)

    X_slow_frozen = frozen_slow_features(y, origin, horizon_dates)
    stage1_fc = pd.Series(stage1_model.predict(X_slow_frozen), index=horizon_dates)

    y_work_c = y_masked.copy()
    stage2_preds = {}
    for date in horizon_dates:
        x_row = feat.fast_feature_set(y_work_c).loc[[date]]
        resid_p = stage2_model.predict(x_row)[0]
        combined = stage1_fc.loc[date] + resid_p
        y_work_c.loc[date] = combined
        stage2_preds[date] = resid_p
    forecast_c = stage1_fc + pd.Series(stage2_preds)

    naive_persistence = pd.Series(y_train.iloc[-1], index=horizon_dates)

    h = np.arange(1, HORIZON + 1)
    err_a = (forecast_a.values - actual.values)
    err_c = (forecast_c.values - actual.values)
    err_naive = (naive_persistence.values - actual.values)

    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(h, pd.Series(np.abs(err_a)).rolling(7, min_periods=1).mean(), color="#d1495b",
            label="A: baseline, recursive lag feedback")
    ax.plot(h, pd.Series(np.abs(err_c)).rolling(7, min_periods=1).mean(), color="#2f6f9f",
            label="C: two-stage smoothed + residual")
    ax.plot(h, pd.Series(np.abs(err_naive)).rolling(7, min_periods=1).mean(), color="#9aa5b1", ls="--",
            label="naive: repeat last known value")
    ax.set_xlabel("days ahead of forecast origin")
    ax.set_ylabel("7-day rolling mean absolute error")
    ax.set_title("Fixed-origin multi-step forecast: error growth over the horizon")
    ax.legend(fontsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/multistep_horizon_error.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(actual.index, actual.values, color="black", lw=1.6, label="actual")
    ax.plot(forecast_a.index, forecast_a.values, color="#d1495b", lw=1.2, label="A: baseline, recursive")
    ax.plot(forecast_c.index, forecast_c.values, color="#2f6f9f", lw=1.2, label="C: two-stage decomposition")
    ax.plot(naive_persistence.index, naive_persistence.values, color="#9aa5b1", lw=1.0, ls="--",
             label="naive: repeat last value")
    ax.set_title(f"90-day-ahead forecast from a single origin ({origin.date()})")
    ax.legend(fontsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/multistep_forecast_trajectory.png")
    plt.close(fig)

    print("Fixed-origin 90-day-ahead RMSE:")
    print(f"  A baseline (recursive):        {np.sqrt(np.mean(err_a ** 2)):.2f}")
    print(f"  C two-stage decomposition:      {np.sqrt(np.mean(err_c ** 2)):.2f}")
    print(f"  naive (repeat last value):      {np.sqrt(np.mean(err_naive ** 2)):.2f}")
    print(f"  A baseline, first 7 days only:   {np.sqrt(np.mean(err_a[:7] ** 2)):.2f}")
    print(f"  C two-stage, first 7 days only:  {np.sqrt(np.mean(err_c[:7] ** 2)):.2f}")
    print(f"  A baseline, last 30 days:        {np.sqrt(np.mean(err_a[-30:] ** 2)):.2f}")
    print(f"  C two-stage, last 30 days:       {np.sqrt(np.mean(err_c[-30:] ** 2)):.2f}")


if __name__ == "__main__":
    main()
