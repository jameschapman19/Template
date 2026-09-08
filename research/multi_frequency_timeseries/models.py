"""The five modelling strategies under comparison. Each returns a fitted
predict function so the backtest loop in experiment.py can treat them uniformly.
"""
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from statsmodels.tsa.seasonal import MSTL

import features as feat

XGB_PARAMS = dict(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
)


def _fit_predict(X_train, y_train, X_test):
    model = XGBRegressor(**XGB_PARAMS)
    model.fit(X_train, y_train)
    return model, model.predict(X_test)


def _dropna_align(X: pd.DataFrame, y: pd.Series):
    mask = X.notna().all(axis=1) & y.notna()
    return X[mask], y[mask]


def baseline_raw(y_train: pd.Series, y_full: pd.Series, test_index: pd.DatetimeIndex):
    """A: single XGBoost on the raw series with short lags + calendar dummies."""
    X_full = feat.baseline_feature_set(y_full)
    X_train, y_tr = _dropna_align(X_full.loc[y_train.index], y_train)
    model, _ = _fit_predict(X_train, y_tr, X_full.loc[test_index])
    pred = pd.Series(model.predict(X_full.loc[test_index]), index=test_index)
    return pred, {"model": model}


def single_stage_full_features(y_train: pd.Series, y_full: pd.Series, test_index: pd.DatetimeIndex):
    """B: one XGBoost, still fit to raw y, but fed both slow and fast features."""
    X_full = feat.full_feature_set(y_full)
    X_train, y_tr = _dropna_align(X_full.loc[y_train.index], y_train)
    model, _ = _fit_predict(X_train, y_tr, X_full.loc[test_index])
    pred = pd.Series(model.predict(X_full.loc[test_index]), index=test_index)
    return pred, {"model": model}


def two_stage_smoothed_residual(y_train: pd.Series, y_full: pd.Series, test_index: pd.DatetimeIndex,
                                 smooth_span: int = 21):
    """C: Stage 1 fits a causal EWMA-smoothed proxy of y (the low-frequency level)
    using only slow features. Stage 2 fits the leftover raw-minus-stage1 residual
    using only fast features. Smoothing is trailing/causal (span-based EWMA on
    past values only) so nothing from the future leaks into either stage.
    """
    smoothed_full = y_full.ewm(span=smooth_span, min_periods=smooth_span // 2).mean()

    X_slow_full = feat.slow_feature_set(y_full)
    X_slow_train, s_tr = _dropna_align(X_slow_full.loc[y_train.index], smoothed_full.loc[y_train.index])
    stage1_model, _ = _fit_predict(X_slow_train, s_tr, X_slow_full.loc[test_index])

    stage1_fitted_train = pd.Series(stage1_model.predict(X_slow_train), index=X_slow_train.index)
    resid_train = y_train.loc[X_slow_train.index] - stage1_fitted_train

    X_fast_full = feat.fast_feature_set(y_full)
    X_fast_train, r_tr = _dropna_align(X_fast_full.loc[resid_train.index], resid_train)
    stage2_model, _ = _fit_predict(X_fast_train, r_tr, X_fast_full.loc[test_index])

    stage1_pred = pd.Series(stage1_model.predict(X_slow_full.loc[test_index]), index=test_index)
    stage2_pred = pd.Series(stage2_model.predict(X_fast_full.loc[test_index]), index=test_index)
    pred = stage1_pred + stage2_pred
    return pred, {"stage1": stage1_pred, "stage2": stage2_pred, "smoothed_full": smoothed_full,
                  "stage1_model": stage1_model, "stage2_model": stage2_model}


def two_stage_slow_feature_residual(y_train: pd.Series, y_full: pd.Series, test_index: pd.DatetimeIndex):
    """E: Stage 1 fits the RAW series directly but is structurally restricted to
    slow-moving features only, so it can only ever express the low-frequency
    component. Stage 2 fits the resulting residual with fast features.
    """
    X_slow_full = feat.slow_feature_set(y_full)
    X_slow_train, y_tr = _dropna_align(X_slow_full.loc[y_train.index], y_train)
    stage1_model, _ = _fit_predict(X_slow_train, y_tr, X_slow_full.loc[test_index])

    stage1_fitted_train = pd.Series(stage1_model.predict(X_slow_train), index=X_slow_train.index)
    resid_train = y_tr - stage1_fitted_train

    X_fast_full = feat.fast_feature_set(y_full)
    X_fast_train, r_tr = _dropna_align(X_fast_full.loc[resid_train.index], resid_train)
    stage2_model, _ = _fit_predict(X_fast_train, r_tr, X_fast_full.loc[test_index])

    stage1_pred = pd.Series(stage1_model.predict(X_slow_full.loc[test_index]), index=test_index)
    stage2_pred = pd.Series(stage2_model.predict(X_fast_full.loc[test_index]), index=test_index)
    pred = stage1_pred + stage2_pred
    return pred, {"stage1": stage1_pred, "stage2": stage2_pred}


def stl_classical(y_train: pd.Series, y_full: pd.Series, test_index: pd.DatetimeIndex):
    """D: classical decomposition benchmark, using MSTL rather than plain STL
    because the series has two seasonal periods (weekly and annual) -- vanilla
    single-period STL has no slot for the annual wave and it leaks into trend
    or residual, which is itself one of the findings (see write-up). Trend is
    extrapolated with a short linear fit on its tail, both seasonal components
    are repeated (seasonal-naive), and only the leftover remainder is modelled
    with XGBoost on fast lag features. NOTE: MSTL's internal smoother is a
    centered/symmetric LOESS filter, so it peeks slightly into its own training
    window in a way a pure trailing filter would not -- see write-up.
    """
    mstl = MSTL(y_train, periods=(7, 365), stl_kwargs={"robust": True}).fit()
    trend, seasonal, resid = mstl.trend, mstl.seasonal, mstl.resid
    seasonal_7, seasonal_365 = seasonal["seasonal_7"], seasonal["seasonal_365"]

    tail = trend.iloc[-90:]
    tt = np.arange(len(tail))
    slope, intercept = np.polyfit(tt, tail.values, 1)
    horizon = np.arange(1, len(test_index) + 1) + len(tail) - 1
    trend_fc = pd.Series(intercept + slope * horizon, index=test_index)

    last_week = seasonal_7.iloc[-7:]
    pattern_by_dow = {date.dayofweek: val for date, val in last_week.items()}
    seasonal_7_fc = pd.Series([pattern_by_dow[d.dayofweek] for d in test_index], index=test_index)
    annual_lag_dates = test_index - pd.Timedelta(days=365)
    seasonal_365_fc = pd.Series(seasonal_365.reindex(annual_lag_dates).values, index=test_index)

    X_fast_full = feat.fast_feature_set(y_full)
    X_fast_train, r_tr = _dropna_align(X_fast_full.loc[resid.index], resid)
    resid_model, _ = _fit_predict(X_fast_train, r_tr, X_fast_full.loc[test_index])
    resid_fc = pd.Series(resid_model.predict(X_fast_full.loc[test_index]), index=test_index)

    pred = trend_fc + seasonal_7_fc + seasonal_365_fc + resid_fc
    return pred, {
        "trend": trend_fc, "seasonal_7": seasonal_7_fc, "seasonal_365": seasonal_365_fc, "resid": resid_fc,
        "mstl_trend": trend, "mstl_seasonal_7": seasonal_7, "mstl_seasonal_365": seasonal_365, "mstl_resid": resid,
    }


METHODS = {
    "A_baseline_raw": baseline_raw,
    "B_single_stage_full_features": single_stage_full_features,
    "C_two_stage_smoothed_residual": two_stage_smoothed_residual,
    "E_two_stage_slow_feature_residual": two_stage_slow_feature_residual,
    "D_stl_classical": stl_classical,
}
