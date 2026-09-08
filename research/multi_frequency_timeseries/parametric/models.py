"""Five purely parametric strategies, chosen to reflect what the forecasting
literature actually recommends for a series with both a slow trend/annual
cycle and fast weekly + ARMA structure (see ../README_parametric.md for the
citations). Every one of these has a fixed functional form with estimated
coefficients -- no trees, no LOESS smoothing.

M1  OLS harmonic regression            -- naive parametric baseline: global
                                           linear trend + Fourier terms,
                                           i.i.d. Gaussian errors assumed.
M2  Dynamic harmonic regression         -- Hyndman's textbook recommendation
                                           for long seasonal periods: same
                                           regressors as M1, but with ARMA
                                           errors instead of assuming i.i.d.
                                           noise (fit as SARIMAX with exog).
M3  Structural time series (state space) -- stochastic local-linear trend +
                                           trigonometric seasonal + AR(1)
                                           irregular, MLE via Kalman filter.
                                           The statsmodels-native analogue of
                                           BATS: unlike M1/M2 its trend is not
                                           forced into one fixed global slope.
M4  TBATS                               -- the literature's purpose-built
                                           model for multiple seasonalities
                                           (De Livera, Hyndman & Snyder 2011).
M5  Seasonal ARIMA, weekly period only   -- the naive default a practitioner
                                           reaches for on daily data (SARIMA
                                           can't feasibly take period=365 as
                                           its seasonal period -- that needs
                                           m-1 seasonal parameters). Included
                                           to show what "forgetting" the
                                           annual cycle costs you.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from tbats import TBATS

import features as feat
import data as data_mod

T0 = pd.Timestamp(data_mod.START)


def _design(index):
    return feat.design_matrix(index, T0)


class OLSHarmonic:
    name = "M1_ols_harmonic"

    def fit(self, y_train: pd.Series):
        X = sm.add_constant(_design(y_train.index))
        self.res_ = sm.OLS(y_train.values, X).fit()
        return self

    def forecast(self, horizon_index):
        X = sm.add_constant(_design(horizon_index), has_constant="add")
        return pd.Series(self.res_.predict(X), index=horizon_index)


class DynamicHarmonicRegression:
    name = "M2_dynamic_harmonic_regression"

    def fit(self, y_train: pd.Series, order=(1, 0, 1)):
        X = _design(y_train.index)
        self.mod_ = sm.tsa.SARIMAX(y_train, exog=X, order=order, trend="c",
                                    enforce_stationarity=False, enforce_invertibility=False)
        self.res_ = self.mod_.fit(disp=False, method="lbfgs", maxiter=200)
        return self

    def forecast(self, horizon_index):
        X_future = _design(horizon_index)
        fc = self.res_.get_forecast(steps=len(horizon_index), exog=X_future)
        return pd.Series(fc.predicted_mean.values, index=horizon_index)


class StructuralTimeSeries:
    name = "M3_structural_state_space"

    def fit(self, y_train: pd.Series):
        self.mod_ = sm.tsa.UnobservedComponents(
            y_train, level="local linear trend",
            freq_seasonal=[{"period": 7, "harmonics": 2}, {"period": 365.25, "harmonics": 2}],
            autoregressive=1,
        )
        self.res_ = self.mod_.fit(disp=False, method="lbfgs", maxiter=200)
        return self

    def forecast(self, horizon_index):
        fc = self.res_.get_forecast(steps=len(horizon_index))
        return pd.Series(fc.predicted_mean.values, index=horizon_index)


class TBATSModel:
    name = "M4_tbats"

    def fit(self, y_train: pd.Series):
        self.estimator_ = TBATS(seasonal_periods=[7, 365.25], use_box_cox=False,
                                 use_trend=True, use_damped_trend=False, use_arma_errors=True)
        self.res_ = self.estimator_.fit(y_train.values)
        return self

    def forecast(self, horizon_index):
        preds = self.res_.forecast(steps=len(horizon_index))
        return pd.Series(preds, index=horizon_index)


class SeasonalARIMAWeeklyOnly:
    name = "M5_seasonal_arima_weekly_only"

    def fit(self, y_train: pd.Series, order=(1, 0, 0), seasonal_order=(1, 0, 0, 7)):
        self.mod_ = sm.tsa.SARIMAX(y_train, order=order, seasonal_order=seasonal_order, trend="c",
                                    enforce_stationarity=False, enforce_invertibility=False)
        self.res_ = self.mod_.fit(disp=False, method="lbfgs", maxiter=200)
        return self

    def forecast(self, horizon_index):
        fc = self.res_.get_forecast(steps=len(horizon_index))
        return pd.Series(fc.predicted_mean.values, index=horizon_index)


MODELS = {
    "M1_ols_harmonic": OLSHarmonic,
    "M2_dynamic_harmonic_regression": DynamicHarmonicRegression,
    "M3_structural_state_space": StructuralTimeSeries,
    "M4_tbats": TBATSModel,
    "M5_seasonal_arima_weekly_only": SeasonalARIMAWeeklyOnly,
}
