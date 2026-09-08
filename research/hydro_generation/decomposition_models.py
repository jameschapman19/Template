"""Joint vs. separate fitting of generation, given:

  - weather history (rain, and lags/accumulations of it) -- the only source
    of information about water availability, since storage is latent;
  - calendar;
  - a net demand FORECAST, handed to this system already made (by whatever
    demand-forecasting process the grid runs) for every day in the horizon.
    It is not derived here from temperature/calendar -- it's a given input,
    exactly like calendar. (Simulated as the true future demand, i.e. we
    treat the given demand forecast as accurate; see README for the caveat.)

No AR/ARMA anywhere -- every model is a plain ("raw") OLS regression. The
only genuinely *forecast* quantity is water availability, via antecedent
rainfall accumulation (the standard hydrological proxy, see README) -- rain
features are frozen at their value on the forecast origin for every day in
the horizon, since nobody has skillful rain forecasts at this lead time.
Calendar terms vary freely across the horizon (deterministically known).

DemandOnly        generation_hat = the given demand forecast, unmodified.
                   Weather-blind: shows what accounting for water buys you.
JointModel        One OLS regression of generation(t) on rain-accumulation
                   features + annual calendar + the demand forecast, all at
                   once. Additive by construction.
SeparateCascade    A ceiling regression -- generation ~ rain accumulations +
                   annual calendar, fit against historical generation --
                   combined with the given demand forecast via the *true*
                   structural rule: generation = min(demand, ceiling).
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

# Antecedent Precipitation Index (Kohler & Linsley, 1951): API(t) = rain(t)
# + k*API(t-1), a causal exponential integrator of past rain, rather than a
# set of overlapping fixed-window sums. Fixed windows at 7/30/90/365 days are
# highly collinear with each other and, worse, none of them is *tuned* to
# the actual persistence of the system: a first cut of this study used those
# four windows and got a ceiling regression that barely reacted to an
# ongoing drought (see README). Two decays instead: a fast one for short-lived
# rain events, and a slow one set to (1 - EVAP_RATE) -- the same day-to-day
# persistence the true (latent) reservoir mass balance has, since storage
# that receives no inflow decays geometrically at exactly that rate. This is
# the one place this study "cheats" by reusing a simulator constant, done
# deliberately to show what picking a *physically matched* memory length
# buys you over an arbitrary calendar-convenient one -- see README.
API_DECAYS = (0.90, 0.996)


def antecedent_rain_index(rain: pd.Series, decays=API_DECAYS) -> pd.DataFrame:
    shifted = rain.shift(1).fillna(0.0).values
    out = {}
    for k in decays:
        api = np.zeros(len(shifted))
        for i in range(1, len(shifted)):
            api[i] = shifted[i] + k * api[i - 1]
        out[f"api_{k}"] = api
    return pd.DataFrame(out, index=rain.index)


def annual_calendar(index: pd.DatetimeIndex, k: int = 2) -> pd.DataFrame:
    doy = index.dayofyear.values.astype(float)
    cols = {}
    for h in range(1, k + 1):
        w = 2 * np.pi * h * doy / 365.25
        cols[f"annual_sin{h}"] = np.sin(w)
        cols[f"annual_cos{h}"] = np.cos(w)
    return pd.DataFrame(cols, index=index)


def _frozen_rain_block(rain_frozen: pd.Series, horizon_index: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame(np.tile(rain_frozen.values, (len(horizon_index), 1)),
                         columns=rain_frozen.index, index=horizon_index)


class DemandOnly:
    """Weather-blind reference: trust the given demand forecast completely."""

    name = "demand_only"

    def fit(self, df_train: pd.DataFrame):
        return self

    def forecast(self, horizon_index: pd.DatetimeIndex, demand_forecast: pd.Series) -> pd.Series:
        return demand_forecast.clip(lower=0)


class SeparateCascade:
    name = "separate_cascade"

    def fit(self, df_train: pd.DataFrame):
        rain_feats = antecedent_rain_index(df_train["rain"])
        XA = pd.concat([rain_feats, annual_calendar(df_train.index)], axis=1)
        mask = XA.notna().all(axis=1)
        self.model_ceiling_ = sm.OLS(df_train["generation"][mask], sm.add_constant(XA[mask])).fit()
        self.rain_frozen_ = rain_feats.iloc[-1]
        return self

    def forecast(self, horizon_index: pd.DatetimeIndex, demand_forecast: pd.Series) -> pd.Series:
        XA_h = pd.concat([_frozen_rain_block(self.rain_frozen_, horizon_index),
                           annual_calendar(horizon_index)], axis=1)
        ceiling_hat = self.model_ceiling_.predict(sm.add_constant(XA_h, has_constant="add")).clip(lower=0)
        generation_hat = np.minimum(demand_forecast.values, ceiling_hat.values)
        return pd.Series(generation_hat, index=horizon_index)

    def ceiling_forecast(self, horizon_index: pd.DatetimeIndex) -> pd.Series:
        XA_h = pd.concat([_frozen_rain_block(self.rain_frozen_, horizon_index),
                           annual_calendar(horizon_index)], axis=1)
        return self.model_ceiling_.predict(sm.add_constant(XA_h, has_constant="add")).clip(lower=0)


class JointModel:
    """Same information as SeparateCascade -- rain accumulations, annual
    calendar, and the given demand forecast -- but as one OLS fit directly
    on generation. Additive by construction: it can blend the water signal
    and the demand signal, but it has no way to express "whichever binds."
    """

    name = "joint"

    def fit(self, df_train: pd.DataFrame):
        rain_feats = antecedent_rain_index(df_train["rain"])
        X = pd.concat([rain_feats, annual_calendar(df_train.index), df_train[["demand"]]], axis=1)
        mask = X.notna().all(axis=1)
        self.model_ = sm.OLS(df_train["generation"][mask], sm.add_constant(X[mask])).fit()
        self.rain_frozen_ = rain_feats.iloc[-1]
        return self

    def forecast(self, horizon_index: pd.DatetimeIndex, demand_forecast: pd.Series) -> pd.Series:
        X_h = pd.concat(
            [_frozen_rain_block(self.rain_frozen_, horizon_index), annual_calendar(horizon_index),
             pd.DataFrame({"demand": demand_forecast.values}, index=horizon_index)],
            axis=1,
        )
        pred = self.model_.predict(sm.add_constant(X_h, has_constant="add")).clip(lower=0)
        return pd.Series(pred.values, index=horizon_index)


MODELS = {"demand_only": DemandOnly, "joint": JointModel, "separate_cascade": SeparateCascade}
