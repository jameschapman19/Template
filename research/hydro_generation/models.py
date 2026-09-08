"""Two forecasting strategies for generation, reflecting a real choice in
hydropower forecasting practice:

M_naive_calendar    Treat generation as just another seasonal series and
                    fit it directly: Fourier terms for the annual/weekly
                    cycle, plain OLS (no AR/ARMA -- a "raw" regression).
                    This model never looks at rain, inflow, or storage.

M_structural_esp    Ensemble Streamflow Prediction (ESP) logic (the named,
                    standard hydrological forecasting technique for exactly
                    this situation -- see README for citation): take TODAY's
                    true, observed reservoir storage, drive the same
                    mass-balance + rule-curve dispatch simulator forward
                    using a *climatological* (day-of-year average, computed
                    only from training data) inflow scenario -- because no
                    one has skillful rain forecasts months out -- plus a
                    plain OLS Fourier demand forecast, and let the
                    mechanistic model's own constraint produce the forecast.

The comparison isolates one thing: does today's observed water level get to
influence the forecast at all? M_naive_calendar has no channel for it to;
M_structural_esp's entire forecast is anchored on it.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

import simulate as sim


def fourier_design(index: pd.DatetimeIndex, t0: pd.Timestamp) -> pd.DataFrame:
    t = (index - t0).days.values.astype(float)
    w_a = 2 * np.pi * t / 365.25
    w_w = 2 * np.pi * t / 7
    return pd.DataFrame(
        {
            "t": t,
            "annual_sin1": np.sin(w_a), "annual_cos1": np.cos(w_a),
            "annual_sin2": np.sin(2 * w_a), "annual_cos2": np.cos(2 * w_a),
            "weekly_sin1": np.sin(w_w), "weekly_cos1": np.cos(w_w),
        },
        index=index,
    )


class HarmonicRegression:
    """Fourier terms, plain OLS -- no AR/ARMA. Fit to whichever series is
    passed in (`generation` for the naive strategy, `demand` for the
    structural strategy's demand forecast)."""

    def __init__(self, t0: pd.Timestamp):
        self.t0 = t0

    def fit(self, y_train: pd.Series):
        X = fourier_design(y_train.index, self.t0)
        self.res_ = sm.OLS(y_train, sm.add_constant(X)).fit()
        return self

    def forecast(self, horizon_index):
        X_future = fourier_design(horizon_index, self.t0)
        pred = self.res_.predict(sm.add_constant(X_future, has_constant="add"))
        return pd.Series(pred.values, index=horizon_index)


T0 = pd.Timestamp(sim.START)


class NaiveCalendarModel:
    name = "M_naive_calendar"

    def fit(self, df_train: pd.DataFrame):
        self.model_ = HarmonicRegression(T0).fit(df_train["generation"])
        return self

    def forecast(self, horizon_index):
        return self.model_.forecast(horizon_index)


def climatology(series: pd.Series, smooth_window: int = 15) -> np.ndarray:
    """Mean value by day-of-year, smoothed circularly (wrapping December
    into January) so a 366-slot lookup table has no seams."""
    doy = series.index.dayofyear.values
    table = np.array([series.values[doy == d].mean() if np.any(doy == d) else np.nan for d in range(1, 367)])
    table = pd.Series(table)
    table = table.fillna(table.mean())
    tiled = pd.concat([table, table, table], ignore_index=True)
    smoothed = tiled.rolling(smooth_window, center=True, min_periods=1).mean()
    return smoothed.iloc[366:732].values


class StructuralESPModel:
    """Ensemble Streamflow Prediction, collapsed to its climatological mean
    trajectory rather than a full ensemble (see README for the simplification
    this makes and what a full implementation would add)."""

    name = "M_structural_esp"

    def fit(self, df_train: pd.DataFrame):
        self.inflow_climatology_ = climatology(df_train["inflow"])
        self.demand_model_ = HarmonicRegression(T0).fit(df_train["demand"])
        self.storage_origin_ = float(df_train["storage"].iloc[-1])
        return self

    def forecast(self, horizon_index):
        demand_fc = self.demand_model_.forecast(horizon_index).values
        doy = horizon_index.dayofyear.values
        inflow_fc = self.inflow_climatology_[doy - 1]
        _, generation_fc, _ = sim.simulate_dispatch(inflow_fc, demand_fc, initial_storage=self.storage_origin_)
        return pd.Series(generation_fc, index=horizon_index)


MODELS = {"M_naive_calendar": NaiveCalendarModel, "M_structural_esp": StructuralESPModel}
