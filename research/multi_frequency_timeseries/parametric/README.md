# Multi-frequency time series, parametric models only: what the literature recommends and whether it holds up

The earlier study in the parent folder used gradient-boosted trees and
STL/MSTL. Trees have no fixed functional form (they're the textbook example
of a *nonparametric* regression method) and STL/MSTL decompose via LOESS, a
nonparametric smoother. This folder redoes the problem restricted to models
with a fixed, named functional form and estimated coefficients — the actual
industry/academic state of the art for series with both a slow and a fast
seasonal/trend component. Findings below are grounded in the sources listed
at the bottom, not just asserted.

## What the literature actually recommends

For a series with more than one seasonal period (here: weekly + annual) —
sometimes called "complex" or "multiple" seasonality — three parametric
approaches dominate the forecasting literature:

1. **Dynamic harmonic regression**: replace the seasonal component with
   Fourier (sin/cos) terms at each period, and replace the "assume i.i.d.
   errors" of plain regression with an ARMA error process fit jointly.
   Hyndman & Athanasopoulos's *Forecasting: Principles and Practice*
   explicitly recommends this over seasonal ARIMA/ETS once the seasonal
   period gets long (daily data with annual seasonality, m=365, needs m-1
   seasonal parameters in a classical seasonal model — "almost impossible"
   to estimate) — Fourier terms need only 2 parameters per harmonic,
   regardless of the period length.
2. **TBATS** (Trigonometric seasonality, Box-Cox transform, ARMA errors,
   Trend, Seasonal — De Livera, Hyndman & Snyder, 2011): a fully parametric
   exponential-smoothing state-space model purpose-built for multiple,
   possibly non-integer seasonal periods, using the same trigonometric
   seasonal representation as dynamic harmonic regression but estimating
   trend, seasonal strength, and a Box-Cox transform jointly, with the
   seasonal shape itself allowed to evolve slowly rather than being fixed
   forever (unlike plain harmonic regression, where the fitted seasonal
   shape is the same in year 1 and year 10).
3. **Prophet** (Taylor & Letham, 2017): the generalized-additive-model
   formulation industry reaches for most often in practice —
   `y = piecewise-linear-or-logistic trend + Fourier seasonality + holidays
   + error`, by default a 10-harmonic annual + 3-harmonic weekly Fourier
   series on top of a piecewise-linear trend with automatically placed
   changepoints. Structurally, it's dynamic harmonic regression's Fourier
   seasonality plus an explicit answer to "what if the trend isn't one
   straight line" — which is exactly the scenario tested below.

All three share the same recipe: **Fourier terms for the seasonal part,
something other than a single rigid line for the trend part.** That's the
detail a naive parametric approach (plain OLS on Fourier terms with a global
linear trend) skips, and it's the one this experiment is built to expose.

## The synthetic data (parametric ground truth, not just "realistic-looking")

`data.py` generates a daily series with every component specified as a named
formula (see the module docstring for exact values):

- **Trend**: piecewise LINEAR with one changepoint at day 900 — growth
  decelerates from slope 0.05/day to 0.015/day. A single global linear trend
  is structurally *unable* to fit this after the changepoint — that's
  deliberate. This is the "what if trend isn't one straight line" case
  TBATS/Prophet's damped/piecewise trend machinery exists for.
- **Annual seasonal**: 2 harmonics (asymmetric shape, not a pure sine).
- **Weekly seasonal**: 2 harmonics (asymmetric weekday/weekend shape).
- **Noise**: a genuine stationary Gaussian ARMA(1,1) — the part no calendar
  regressor can ever explain, only a correctly specified error model can.

Every model below is refit from scratch is a walk-forward backtest with an
expanding window (`experiment.py`, `INITIAL_TRAIN=1000` growing by 120 days
per fold, 4 folds), and each fold's forecast is a genuine multi-step-ahead
forecast — `model.get_forecast(120)` / `model.forecast(120)` — using each
model's own native forecasting machinery. No hand-rolled recursion anywhere
in this folder: propagating a fitted ARIMA/state-space model forward in time
is exactly what its Kalman filter / difference equation is *for*, which is
itself one advantage of this model class over the lag-feature tree models in
the parent study (which had no native multi-step mechanism and had to be
recursively simulated by hand, with the compounding-error consequences
documented there).

## Results

| method | mean RMSE | mean MAE | mean fit time |
|---|---|---|---|
| M3 structural state space (stochastic trend + trig seasonal + AR(1)) | **2.70** | **2.22** | 4.8s |
| M2 dynamic harmonic regression (Fourier + ARMA(1,1) errors) | 7.40 | 6.71 | 4.9s |
| M1 OLS harmonic regression (Fourier, i.i.d. errors, naive parametric baseline) | 7.54 | 7.19 | 0.02s |
| naive: repeat last known value | 9.62 | 7.84 | — |
| M5 seasonal ARIMA, weekly period only (annual cycle unmodelled) | 11.43 | 9.36 | 0.7s |

(`plots/metric_rmse.png`, `plots/metric_mae.png`, `plots/last_fold_overlay.png`)

TBATS (M4) was implemented (`models.py`, `TBATSModel`) but excluded from
this table: a single fit on 1000 days with 2 seasonal periods did not
converge in over 11 minutes in this environment, which matches the
literature's own caveat that TBATS's search over Box-Cox/trend/damping/ARMA
options "can be slow... minutes on long series" — and repeating that 20
times (5 models × 4 folds) for a backtest is not practical here. This is
itself a finding, not just an excuse: **TBATS's generality has a real,
literature-documented cost**, which is exactly why dynamic harmonic
regression and structural state-space models — cheaper, only slightly less
general — are the more common production choice.

### Why the structural state-space model (M3) wins by 2-3x

`plots/trend_recovery_check.png` shows why directly. It fits M1 and M3 from
the same origin (the last backtest fold, with 900 pre-changepoint and 460
post-changepoint training days) and forecasts forward: M1's oscillation
band drifts visibly above the true trend line and keeps widening the gap,
while M3's band stays centered on it. The mechanism is exactly what the
literature describes as TBATS/Prophet's reason to exist:

- M1 and M2 both fit **one global linear slope** over the whole training
  window. With 900 old-regime days and only 460 new-regime days by the last
  fold, that single slope is still a weighted average dominated by the
  faster pre-changepoint growth — and it *never* fully corrects, no matter
  how much new-regime data arrives, because OLS/SARIMAX-with-fixed-exog
  can't distinguish "the true rate changed" from "there's a positive
  residual right now."
- M3's local linear trend is a **stochastic** state (a random walk in the
  level and slope, estimated via Kalman filter), so it can and does drift
  toward the new, slower rate as post-changepoint evidence accumulates.
  That adaptivity is the entire practical case for TBATS/Prophet/structural
  models over plain harmonic regression once you don't trust the trend to
  stay a single straight line — which, for any real business or economic
  series over a multi-year horizon, you generally shouldn't.

`plots/horizon_error.png` shows the same effect from a different angle:
M1/M2's error grows roughly linearly across the 120-day horizon (a
*systematic bias* compounding because the true trend keeps pulling away
from their fixed line — not the variance-driven blow-up the recursive
tree model showed in the parent study), M5 grows even faster (missing the
annual cycle entirely on top of the same trend bias), while M3 stays flat
across the whole horizon.

### Where dynamic harmonic regression (M2) does earn its keep

M2 and M1 finish close overall (7.40 vs. 7.54), but not for the same reason
throughout the horizon. In `plots/horizon_error.png`, M2 is visibly *better*
than M1 in the first ~20 days of each forecast (its fitted AR(1)/MA(1) error
term is correctly leaning on the still-warm recent shock) and converges to,
even slightly exceeds, M1's error by day 100+ (once the shared trend bias
dominates and the ARMA state's own extrapolated drift adds a little extra
long-run error). **The ARMA-errors upgrade over plain OLS buys you short-
horizon accuracy and correct uncertainty intervals, not long-horizon trend
robustness** — that's a separate problem, solved only by giving the trend
itself somewhere to move (M3), not by a better error model on top of a
trend that still can't move.

### The naive "just use SARIMA" default (M5) is the FPP3 chapter's cautionary case, reproduced

M5 fits a seasonal ARIMA at period 7 only, which is what period-365
"seasonal ARIMA" would nominally require, but 364 seasonal parameters is
infeasible — exactly the FPP3 point cited above. Skipping the annual term
entirely rather than fighting that estimation problem is what a lot of
practitioners actually do, and it's the worst model here, worse even than
repeating yesterday's value. The annual cycle is roughly a third of this
series' explained variance; leaving it out isn't a minor omission.

## Practical takeaway

- If your series has more than one seasonal period, don't reach for plain
  seasonal ARIMA/ETS — the classical machinery needs one parameter per
  season-minus-one and breaks down long before you get to an annual period
  on daily data. Fourier terms (dynamic harmonic regression) or a purpose-
  built multi-seasonal model (TBATS) are the standard fix.
- Don't stop at "Fourier terms + OLS." The seasonal part being handled well
  says nothing about the trend part. If there's any chance the trend isn't
  a single straight line over your whole history — normal for anything
  spanning a few years — use a model whose trend can move (a structural/
  state-space local trend, or Prophet's/TBATS's piecewise or damped trend),
  not a model that commits to one slope for life.
  This mattered more than the choice of error model in this experiment: M3
  beat M1 by ~3x on a trend-adaptivity difference alone.
- ARMA errors on top of a regression (dynamic harmonic regression) are
  worth having for short-horizon accuracy and honest uncertainty intervals,
  but don't expect them to fix long-horizon trend bias — that needs a
  trend component that can actually change, not a better-modelled residual.
- TBATS is the textbook name most associated with this problem, but budget
  for its cost: this experiment's single fit didn't finish in 11+ minutes
  on a 1000-point series with 2 seasonal periods. A statsmodels structural
  time series model (`UnobservedComponents`) got a comparable stochastic-
  trend-plus-trigonometric-seasonal specification fitting in ~5 seconds per
  fold and won this backtest outright — worth trying first.

## Files

- `data.py` — synthetic generator with every component a documented formula.
- `features.py` — deterministic (Fourier + time index) regressors.
- `models.py` — the five strategies (M1-M5 above).
- `experiment.py` — walk-forward backtest (native multi-step forecasts, no
  recursion) + all plots.
- `plots/` — every figure referenced above, plus `metrics.csv`.

## Sources

- [Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* (3rd ed), Ch. 10.5 "Dynamic harmonic regression"](https://otexts.com/fpp3/dhr.html)
- [Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* (3rd ed), Ch. 12.1 "Complex seasonality"](https://otexts.com/fpp3/complexseasonality.html)
- [Rob J Hyndman, "Forecasting with long seasonal periods"](https://robjhyndman.com/hyndsight/longseasonality/)
- [Rob J Hyndman, TBATS slides (NYC 2018)](https://robjhyndman.com/nyc2018/3-2-TBATS.pdf)
- [De Livera, Hyndman & Snyder (2011), the TBATS model — summarised in "TBATS in R: Forecast Multiple Seasonalities"](https://r-statistics.co/TBATS-Model-in-R.html)
- [Taylor & Letham (2017), Prophet — summary via DataCamp, "Facebook Prophet: A New Approach to Time Series Forecasting"](https://www.datacamp.com/tutorial/facebook-prophet)
