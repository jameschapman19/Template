# Why trig terms are a shortcut, not a substitute for physics — and there is exact theory for it

The hypothesis: in a causal chain like

```
generation = h(water, net_demand)
water      = f(rain)
rain       = g(t)          -- rain has a seasonal component
net_demand = e(t, temperature)
```

trig/calendar terms only ever proxy for the *predictable, seasonal part* of
the true physical drivers. A model given both trig(t) and a real (but noisy)
measurement of the physical driver will systematically prefer trig(t) —
not because it's more correct, but because it's noiseless, so it wins on
training loss — and will starve the true driver's coefficient down toward
zero. This reproduces, in miniature, exactly what happened in the earlier
hydro study: a water-availability regression kept losing to a plain
calendar fit, and a joint model's rain coefficient was diluted to
near-irrelevance. This folder isolates that mechanism in the smallest
possible example and shows it is not a modelling accident — it is the
textbook combination of two named, exact results.

## The theory

**1. Errors-in-variables / attenuation bias** (Frisch, 1934; standard
reference: Fuller, *Measurement Error Models*, 1987). If the true model is
`Y = β·X_true + noise` but you only observe a noisy proxy
`X_obs = X_true + u`, OLS of `Y` on `X_obs` gives a *biased-toward-zero*
estimate:

```
β_hat → β · Var(X_true) / (Var(X_true) + Var(u))
```

the classical "reliability ratio." The noisier the measurement relative to
the true signal, the more the estimated effect shrinks toward zero — even
though the true causal effect never changed.

**2. The Frisch–Waugh–Lovell theorem** (Frisch & Waugh, 1933; Lovell, 1963).
In a multiple regression, the coefficient on any one regressor equals the
coefficient you'd get from (a) regressing the outcome on every *other*
regressor and taking the residual, (b) regressing the regressor of interest
on every other regressor and taking *its* residual, and (c) regressing (a)
on (b). Applied here: once trig(t) is in the model, the coefficient on
`W_obs` is determined entirely by the part of `Y` and `W_obs` that trig(t)
*can't* explain — i.e. the anomalous, non-seasonal residual.

**Combine them and the mechanism is exact, not qualitative.** Decompose the
true driver as `W_true = S(t) + eps(t)`, where `S(t)` is the seasonal part
(exactly what trig(t) represents) and `eps(t)` is the genuine idiosyncratic
signal — the only part of `W_true` trig cannot see. By Frisch–Waugh–Lovell,
adding trig(t) to the regression reduces the problem to regressing
`Y`'s trig-residual (≈ `eps + η`) on `W_obs`'s trig-residual (≈ `eps + u`).
That is now a pure errors-in-variables problem *in the residual*, so its
attenuation ratio uses only the idiosyncratic variance:

```
coefficient on W_obs, once trig(t) is available  ≈  Var(eps) / (Var(eps) + Var(u))
```

Trig(t) doesn't just compete with the true driver for credit — it *absorbs
the easy, low-noise, seasonal part for free*, leaving the real driver to
fight only for the noisy, idiosyncratic residual, where it usually loses
badly. This is the closed-form prediction validated numerically below.

**3. Why this fails specifically under distribution shift.** Peters,
Bühlmann & Meinshausen's *Invariant Causal Prediction* (JRSS-B, 2016)
formalizes exactly the diagnostic this demo exploits: a causal predictor's
relationship to the outcome is invariant across environments/interventions,
while a merely-correlated predictor's relationship is not. trig(t) and
`W_true` are correlated only because `S(t)` dominates `W_true` in the
"normal" environment; that correlation is not a structural fact and breaks
the moment `eps(t)` stops being small — which is exactly what an anomaly
is. Fit on a single environment (as plain OLS does), trig(t) and the true
cause are statistically indistinguishable; you cannot tell them apart
without either multiple environments or a model that structurally
privileges the true causal channel.

**4. The general name for this failure mode in ML** is Geirhos et al.'s
*shortcut learning* (Nature Machine Intelligence, 2020): models exploit
whatever spuriously-predictive feature is easiest to fit, achieve excellent
in-distribution performance, and fail — often catastrophically — the
moment the shortcut and the true signal decouple. Their canonical example
(a network classifying stars vs. moons by screen position instead of shape)
is structurally the same story as a regression using calendar position
instead of water. Granger & Newbold's classic warning about *spurious
regression* (1974) is the econometric ancestor of the same point: two
series that share a trend or seasonal pattern will look related by OLS
with no genuine structural link at all.

## The minimal demonstration (`simulate.py`, `analysis.py`)

One causal chain: `Y` is caused *only* by `W_true = S(t) + eps(t)`.
`eps(t)` is small noise in training and a large, sustained, never-before-seen
shock (an "anomaly") in a held-out window. The only way `W_true` can enter a
regression is through `W_obs = W_true + u`, a noisy proxy (think: an
antecedent-rainfall index standing in for true unmeasured storage). `trig(t)`
(sin/cos of day-of-year) is noiseless and reproduces `S(t)` exactly.

Three OLS models, fit on data that never includes the anomaly:

| model | features |
|---|---|
| `trig_only` | sin, cos |
| `causal_only` | W_obs |
| `both` | sin, cos, W_obs |

### Result 1 — the coefficient collapse is exactly what the theory predicts

| | fitted coefficient on W_obs |
|---|---|
| `causal_only` | 0.858 |
| `both` (trig available too) | **0.037** |
| theory: Var(eps_train)/(Var(eps_train)+Var(u)) | **0.038** |

(`plots/coefficient_collapse.png`) The true causal effect is exactly 1.
Given `W_obs` alone, OLS recovers a reasonable (if attenuated) 0.86. The
instant trig(t) is available, the coefficient on the *actual physical
driver* collapses to 0.037 — matching the closed-form Frisch–Waugh–Lovell
+ attenuation prediction (0.038) to within sampling noise. This is not a
qualitative tendency; it is a specific, computable number, and the
regression finds it.

### Result 2 — indistinguishable normal-time performance, then divergence

| model | normal-holdout RMSE | anomaly RMSE |
|---|---|---|
| `trig_only` | 0.37 | 7.99 |
| `both` | **0.37** | 7.71 |
| `causal_only` | 1.46 | **2.07** |

(`plots/forecast_through_anomaly.png`, `plots/driver_vs_proxy.png`) In
normal times, `trig_only` and `both` are not just competitive with
`causal_only` — they're *better* (0.37 vs. 1.46), because they get to use
`S(t)` for free with zero measurement noise, while `causal_only` has to
reconstruct the same seasonal shape through a noisy proxy. There is nothing
wrong with using trig terms when the causal driver really does just add
seasonal-shaped noise around a value the calendar predicts. The problem
shows up only in the anomaly: `trig_only` and `both` (which is really just
`trig_only` in a thin disguise, per Result 1) keep riding the fitted
seasonal curve straight through a collapse they have no way to see, while
`causal_only` — noisy, imperfect, unglamorous — tracks the true collapse
because it is the only one of the three actually connected to the cause.

## What this says about the hydro study

The earlier finding — a water-ceiling regression using antecedent rainfall
got its signal diluted once combined with other features, and separately,
a purely calendar-driven model was competitive right up until a drought —
is this exact mechanism, not a coincidence of that particular simulation.
Any time a "physical" feature is (a) a noisy proxy for a latent true driver
and (b) correlated with a noiseless calendar feature only because the
driver is usually seasonal, OLS (or any loss-minimizing fit) will prefer
the calendar feature and hollow out the physical one — right up until the
day the physical driver does something the calendar never predicted.

## Practical implications

- **A low in-sample or normal-period error is not evidence a model has
  learned the physics.** This demo's `both` model has excellent normal-time
  RMSE and a coefficient on the true cause that is off by 27x. Check the
  coefficient/attribution, not just the fit.
- **Forcing the causal feature to fight only for out-of-sample validity is
  a name for how to detect this**: hold out an environment where the
  seasonal-cause correlation plausibly breaks (a known anomaly, a different
  regime, a different site) and check whether performance survives —
  exactly ICP's prescription.
- **If you must include both a calendar term and a noisy physical proxy,
  expect the calendar term to win the "cheap" variance and leave the
  physical proxy starved**, regardless of which one is *actually* causal.
  Fixes include: orthogonalizing deliberately in the other direction (fit
  the physical driver first, calendar only on its residual), regularizing
  toward the physical feature on structural/domain grounds rather than
  trusting OLS's default allocation, or reducing `Var(u)` — i.e., investing
  in a better measurement of the true driver rather than more calendar
  features.

## Files

- `simulate.py` — the one-cause data-generating process, every constant documented.
- `analysis.py` — fits the three OLS models, validates the closed-form
  attenuation prediction, and produces every plot below.
- `plots/` — `driver_vs_proxy.png`, `coefficient_collapse.png`,
  `forecast_through_anomaly.png`, `metrics.csv`.

## Sources

- Frisch, R. (1934), *Statistical Confluence Analysis by Means of Complete Regression Systems* — origin of errors-in-variables/attenuation bias; standard modern treatment: Fuller, W.A. (1987), *Measurement Error Models*.
- Frisch, R. & Waugh, F.V. (1933), "Partial Time Regressions as Compared with Individual Trends," *Econometrica*; Lovell, M.C. (1963), "Seasonal Adjustment of Economic Time Series," *JASA* — the Frisch–Waugh–Lovell theorem.
- Granger, C.W.J. & Newbold, P. (1974), "Spurious Regressions in Econometrics," *Journal of Econometrics*.
- [Peters, J., Bühlmann, P. & Meinshausen, N. (2016), "Causal inference by using invariant prediction: identification and confidence intervals," *Journal of the Royal Statistical Society: Series B*, 78(5), 947-1012](https://rss.onlinelibrary.wiley.com/doi/10.1111/rssb.12167)
- [Geirhos, R. et al. (2020), "Shortcut learning in deep neural networks," *Nature Machine Intelligence*, 2, 665-673](https://www.nature.com/articles/s42256-020-00257-z)
