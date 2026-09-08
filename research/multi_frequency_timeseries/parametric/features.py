"""Deterministic (fully known for any future date, no leakage possible)
regressors shared by the OLS, dynamic-harmonic-regression and seasonal-ARIMA
models: a linear time index and Fourier terms for each seasonal period.
"""
import numpy as np
import pandas as pd


def fourier_terms(index: pd.DatetimeIndex, t0: pd.Timestamp, period: float, n_harmonics: int, name: str) -> pd.DataFrame:
    t = (index - t0).days.values.astype(float)
    cols = {}
    for k in range(1, n_harmonics + 1):
        w = 2 * np.pi * k * t / period
        cols[f"{name}_sin{k}"] = np.sin(w)
        cols[f"{name}_cos{k}"] = np.cos(w)
    return pd.DataFrame(cols, index=index)


def design_matrix(index: pd.DatetimeIndex, t0: pd.Timestamp) -> pd.DataFrame:
    t = (index - t0).days.values.astype(float)
    X = pd.DataFrame({"t": t}, index=index)
    X = pd.concat(
        [X, fourier_terms(index, t0, 365.25, 2, "annual"), fourier_terms(index, t0, 7, 2, "weekly")],
        axis=1,
    )
    return X
