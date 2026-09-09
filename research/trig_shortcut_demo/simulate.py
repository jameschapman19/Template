"""The smallest possible example of the hypothesis under test:

    trig/calendar terms are a stand-in for missing physics. A regression
    given both the true (but noisy) physical driver and a noiseless trig
    proxy for its typical seasonal shape will select the trig proxy and
    starve the real driver of weight -- because that's what minimizes
    training error -- and will then fail exactly when the real driver
    departs from its typical seasonal shape.

One causal chain, three variables:

    t          time
    W_true(t)  the true physical driver ("water"): a seasonal component
               S(t) that trig terms can represent exactly, plus a small
               idiosyncratic shock eps(t) that is NOT a function of t --
               it is genuinely exogenous, and it is what actually varies
               interestingly. eps(t) is small (mostly noise) during
               TRAIN/normal periods and a large, sustained, one-off drop
               during a held-out ANOMALY window (a "drought") that never
               appears in training.
    Y(t)       the observed outcome ("generation"), causally = W_true(t)
               plus small direct noise. Nothing else causes Y.
    W_obs(t)   what a model actually gets to use as a feature for the
               physical driver: a NOISY measurement/proxy of W_true (think:
               an antecedent-rainfall index standing in for a reservoir's
               true, unobserved storage). This is the only channel by which
               the true cause can enter a regression at all.
    trig(t)    sin/cos of day-of-year: noiseless, deterministic, exactly
               reproduces S(t)'s shape.

Y is never a function of t. It only looks like one because W_true has a
seasonal component. That's the whole setup.
"""
import numpy as np
import pandas as pd

N_DAYS = 3000
PERIOD = 365.25

SEASONAL_AMPLITUDE_SIN = 5.0
SEASONAL_AMPLITUDE_COS = 2.0

EPS_SIGMA_NORMAL = 0.3       # true idiosyncratic driver: small noise normally
ANOMALY_START, ANOMALY_END = 2000, 2200
ANOMALY_LEVEL = -8.0         # ... and a large, sustained, unprecedented shock here

ETA_SIGMA = 0.2              # Y's own direct noise on top of W_true
U_SIGMA = 1.5                # measurement noise: how noisy W_obs is as a proxy for W_true

TRAIN_END = 2000             # training never sees a single day of the anomaly


def seasonal(t: np.ndarray) -> np.ndarray:
    w = 2 * np.pi * t / PERIOD
    return SEASONAL_AMPLITUDE_SIN * np.sin(w) + SEASONAL_AMPLITUDE_COS * np.cos(w)


def generate(n_days: int = N_DAYS, seed: int = 0, eps_sigma_normal: float = EPS_SIGMA_NORMAL,
             u_sigma: float = U_SIGMA, mini_anomaly_frac: float = 0.0,
             mini_anomaly_scale: float = 4.0) -> pd.DataFrame:
    """mini_anomaly_frac/scale let training data include occasional smaller
    excursions of the true driver away from its seasonal shape -- i.e. more
    *diversity* in eps, as opposed to just more days of the same normal
    noise. Used to separate "more data" from "more informative data."
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_days)
    idx = pd.RangeIndex(n_days, name="t")

    S = seasonal(t)
    eps = rng.normal(0, eps_sigma_normal, n_days)
    if mini_anomaly_frac > 0:
        hits = rng.random(n_days) < mini_anomaly_frac
        eps[hits] += rng.normal(0, mini_anomaly_scale, hits.sum())
    anomaly = (t >= ANOMALY_START) & (t < ANOMALY_END)
    eps[anomaly] += ANOMALY_LEVEL

    W_true = S + eps
    Y = W_true + rng.normal(0, ETA_SIGMA, n_days)
    W_obs = W_true + rng.normal(0, u_sigma, n_days)

    w_ = 2 * np.pi * t / PERIOD
    return pd.DataFrame(
        {
            "t": t, "sin": np.sin(w_), "cos": np.cos(w_),
            "S": S, "eps": eps, "W_true": W_true, "W_obs": W_obs, "Y": Y,
            "anomaly": anomaly,
        },
        index=idx,
    )


if __name__ == "__main__":
    df = generate()
    print(df.describe())
    print("\nvar(eps) in training (normal-only):", df["eps"].iloc[:TRAIN_END].var())
    print("var(u) =", U_SIGMA ** 2)
    print("theoretical attenuation ratio Var(eps)/(Var(eps)+Var(u)) =",
          df["eps"].iloc[:TRAIN_END].var() / (df["eps"].iloc[:TRAIN_END].var() + U_SIGMA ** 2))
