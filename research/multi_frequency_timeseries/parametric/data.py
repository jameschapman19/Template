"""Carefully specified synthetic daily series -- every component is a named,
documented parametric form, so any model's fitted parameters can be checked
against a known truth (not just judged by holdout error).

y(t) = trend(t) + annual(t) + weekly(t) + eta(t)

trend(t):  piecewise LINEAR with one changepoint at t=CHANGEPOINT. Growth
           decelerates after the changepoint (a maturing product/market).
           This is deliberately something a plain single-slope linear trend
           gets wrong forever after the changepoint -- it is the one feature
           in this dataset a rigid global-linear model structurally cannot
           fit, by design, to test how each model handles trend misspecification.
annual(t): 2 harmonics (4 Fourier terms) at period 365.25 days -- an
           asymmetric annual cycle (single sin/cos alone would be symmetric).
weekly(t): 2 harmonics (4 Fourier terms) at period 7 days -- an asymmetric
           weekday/weekend pattern.
eta(t):    a stationary Gaussian ARMA(1,1) process. This is the entire
           "high-frequency, not deterministic" component: no calendar
           regressor will ever explain it, only a correctly specified error
           model (or a lag-based one) can.
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.arima_process import arma_generate_sample

N_DAYS = 1600
START = "2019-01-01"
CHANGEPOINT = 900

TREND_INTERCEPT = 40.0
TREND_SLOPE_PRE = 0.05
TREND_SLOPE_POST = 0.015

ANNUAL_PERIOD = 365.25
ANNUAL_COEFS = {"sin1": 10.0, "cos1": 4.0, "sin2": 3.0, "cos2": 2.0}

WEEKLY_PERIOD = 7.0
WEEKLY_COEFS = {"sin1": 5.0, "cos1": 2.0, "sin2": 2.0, "cos2": -1.0}

ARMA_AR = [1, -0.55]
ARMA_MA = [1, 0.30]
ARMA_SIGMA = 1.3


def trend(t: np.ndarray) -> np.ndarray:
    out = np.where(
        t < CHANGEPOINT,
        TREND_INTERCEPT + TREND_SLOPE_PRE * t,
        TREND_INTERCEPT + TREND_SLOPE_PRE * CHANGEPOINT + TREND_SLOPE_POST * (t - CHANGEPOINT),
    )
    return out


def harmonic(t: np.ndarray, period: float, coefs: dict) -> np.ndarray:
    w = 2 * np.pi * t / period
    return (
        coefs["sin1"] * np.sin(w) + coefs["cos1"] * np.cos(w)
        + coefs["sin2"] * np.sin(2 * w) + coefs["cos2"] * np.cos(2 * w)
    )


def generate(n_days: int = N_DAYS, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range(START, periods=n_days, freq="D")
    t = np.arange(n_days, dtype=float)

    trend_c = trend(t)
    annual_c = harmonic(t, ANNUAL_PERIOD, ANNUAL_COEFS)
    weekly_c = harmonic(t, WEEKLY_PERIOD, WEEKLY_COEFS)
    eta = arma_generate_sample(ARMA_AR, ARMA_MA, n_days, scale=ARMA_SIGMA, distrvs=rng.standard_normal)

    y = trend_c + annual_c + weekly_c + eta

    return pd.DataFrame(
        {"y": y, "trend": trend_c, "annual": annual_c, "weekly": weekly_c, "eta": eta},
        index=idx,
    )


if __name__ == "__main__":
    df = generate()
    print(df.describe())
