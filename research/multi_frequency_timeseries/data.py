"""Synthetic daily time series with well-separated low- and high-frequency components.

Low frequency: a slowly curving trend + an annual (period=365.25) seasonal cycle.
High frequency: a weekly (period=7) seasonal cycle + a short-memory AR(1) noise
process + heteroskedastic white noise that scales with the trend level.

Kept in one place so every model in the experiment is scored against the exact
same generative process, with the true components retained for diagnostic plots.
"""
import numpy as np
import pandas as pd

N_DAYS = 4 * 365 + 30
START = "2019-01-01"


def generate(n_days: int = N_DAYS, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range(START, periods=n_days, freq="D")
    t = np.arange(n_days)

    trend = 50.0 + 0.03 * t
    annual = 12.0 * np.sin(2 * np.pi * t / 365.25 - 0.6)
    low_freq = trend + annual

    weekly = 6.0 * np.sin(2 * np.pi * t / 7 + 0.4) + 2.0 * (pd.Series(idx).dt.dayofweek.isin([5, 6]).values * -3.0)

    ar_noise = np.zeros(n_days)
    innovations = rng.normal(0, 1.4, n_days)
    phi = 0.6
    for i in range(1, n_days):
        ar_noise[i] = phi * ar_noise[i - 1] + innovations[i]

    scale = 0.5 + trend / trend.max()
    white_noise = rng.normal(0, 1.0, n_days) * scale

    high_freq = weekly + ar_noise + white_noise

    y = low_freq + high_freq

    return pd.DataFrame(
        {
            "y": y,
            "trend": trend,
            "annual": annual,
            "low_freq": low_freq,
            "weekly": weekly,
            "ar_noise": ar_noise,
            "white_noise": white_noise,
            "high_freq": high_freq,
        },
        index=idx,
    )


if __name__ == "__main__":
    df = generate()
    print(df.describe())
    print(df.head())
