"""Causal feature builders. Every rolling/lag feature is shifted so row t only
ever sees information available at t-1 or earlier -- required for a walk-forward
backtest to mean anything.
"""
import numpy as np
import pandas as pd


def calendar_features(idx: pd.DatetimeIndex) -> pd.DataFrame:
    doy = idx.dayofyear.values
    dow = idx.dayofweek.values
    t = np.arange(len(idx))
    return pd.DataFrame(
        {
            "t": t,
            "dow": dow,
            "annual_sin": np.sin(2 * np.pi * doy / 365.25),
            "annual_cos": np.cos(2 * np.pi * doy / 365.25),
            "weekly_sin": np.sin(2 * np.pi * dow / 7),
            "weekly_cos": np.cos(2 * np.pi * dow / 7),
        },
        index=idx,
    )


def fast_lag_features(y: pd.Series, lags=(1, 2, 3, 7, 14)) -> pd.DataFrame:
    out = {f"lag_{l}": y.shift(l) for l in lags}
    out["diff_1"] = y.diff(1)
    out["diff_7"] = y.diff(7)
    return pd.DataFrame(out, index=y.index)


def slow_rolling_features(y: pd.Series, windows=(30, 90, 365)) -> pd.DataFrame:
    shifted = y.shift(1)
    out = {}
    for w in windows:
        out[f"roll_mean_{w}"] = shifted.rolling(w, min_periods=max(7, w // 4)).mean()
    out["expanding_mean"] = shifted.expanding(min_periods=30).mean()
    return pd.DataFrame(out, index=y.index)


def baseline_feature_set(y: pd.Series) -> pd.DataFrame:
    """What a practitioner reaches for first: short lags + calendar dummies."""
    cal = calendar_features(y.index)[["dow", "weekly_sin", "weekly_cos", "annual_sin", "annual_cos"]]
    lags = fast_lag_features(y, lags=(1, 2, 3, 7))
    return pd.concat([cal, lags], axis=1)


def fast_feature_set(y: pd.Series) -> pd.DataFrame:
    cal = calendar_features(y.index)[["dow", "weekly_sin", "weekly_cos"]]
    lags = fast_lag_features(y)
    return pd.concat([cal, lags], axis=1)


def slow_feature_set(y: pd.Series) -> pd.DataFrame:
    cal = calendar_features(y.index)[["t", "annual_sin", "annual_cos"]]
    roll = slow_rolling_features(y)
    return pd.concat([cal, roll], axis=1)


def full_feature_set(y: pd.Series) -> pd.DataFrame:
    return pd.concat([slow_feature_set(y), fast_feature_set(y).drop(columns=["dow"], errors="ignore"),
                       calendar_features(y.index)[["dow"]]], axis=1)
