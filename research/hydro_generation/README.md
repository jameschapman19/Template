# Hydropower generation: water = f(rain), generation = f(water, net demand)

The two earlier studies in this repo (`../multi_frequency_timeseries/`)
treated a series as additively composed of a slow and a fast part. Real
hydro generation isn't additive: it's **constrained**. A reservoir has a
storage level that integrates rainfall over months, and generation is
*dispatched* against demand only up to whatever that storage level allows.
When storage is fine, generation tracks demand's calendar-driven seasonal
pattern almost perfectly — so perfectly that a purely statistical seasonal
model looks like it's doing a great job. Then a drought arrives, and it
completely stops working, because a seasonal curve fit to history has no way
to know the water isn't there this year. This is the actual practical
question the earlier studies were building toward: what do you do when the
"low-frequency component" isn't just a slower wiggle, but a physical state
variable that can independently collapse?

## What's actually standard practice here (research, not assertion)

Hydrology and hydropower operations are a much older, more specialized field
than general time series forecasting, and it has its own established answer:

1. **Conceptual rainfall-runoff models represent the catchment as a cascade
   of linear/nonlinear reservoirs** — HBV, the ABCD model, the Stanford
   Watershed Model/SAC-SMA, IHACRES, the Xinanjiang model. All of them turn
   rain into streamflow/inflow through storage compartments where outflow is
   (often literally) proportional to storage — a "linear reservoir." This is
   exactly `route_inflow()` and the mass balance in `simulate.py` below,
   simplified to a single compartment.
2. **Reservoir operation uses a "rule curve"**: a target/threshold storage
   trajectory that governs how aggressively water can be released. Real
   operating rules cut back release as storage falls below the curve, and
   build storage ahead of high-demand periods. `simulate_dispatch()`'s
   `RULE_CURVE_FRACTION` cutback is a simplified (flat, not seasonal) version
   of this.
3. **Ensemble Streamflow Prediction (ESP)** is the named, standard technique
   for exactly the forecasting problem this file poses: given no skillful
   rainfall forecast beyond a few days, drive the hydrological model forward
   from **today's true, observed state** using historical/climatological
   forcing (one weather scenario per historical year, or its average) rather
   than trying to predict future rain. It's used operationally for
   month-to-season-ahead reservoir forecasts specifically because "predict
   the rain" isn't tractable at that lead time, but "correctly propagate
   what's already true today" is — and, done right, out-performs anything
   that ignores the true state.

The comparison below is exactly M1 (a statistical model that has no channel
for today's true state) vs. an ESP-style model (M2, anchored on it).

## The synthetic system (`simulate.py`)

- **Rain**: seasonal wet-day probability (higher in the "wet season") ×
  gamma-distributed daily amount on wet days — intermittent and bursty, the
  standard stochastic representation of daily rainfall. A ~300-day drought
  window cuts both the wet-day probability and the rain intensity to 30% of
  normal.
- **Inflow**: rain routed through a single linear-reservoir filter (an
  exponential smoother), standing in for catchment travel time.
- **Storage**: mass balance — `storage += inflow - evaporation - env.flow -
  generation`, clipped to capacity (excess spills).
- **Net demand**: the load assigned to hydro after other generation —
  `f(temperature, calendar)`: a heating-degree-day response to temperature
  (a second, independent weather variable — it drives demand, not water)
  plus a day-of-week effect, both linear, plus i.i.d. noise. No AR/ARMA
  anywhere in this module.
- **Generation (the dispatch rule)**: `generation = min(demand, turbine
  capacity, a storage-dependent release ceiling that ramps down below the
  rule-curve threshold, and physically available water)`.

Every constant is calibrated (see the module) so that in normal years mean
inflow comfortably exceeds mean demand — storage oscillates well above the
rule-curve threshold and generation tracks demand almost exactly — and the
drought is long and deep enough to draw storage to zero and keep generation
near zero for months. `plots/sanity_check.png`-style inspection (regenerate
with the snippet in the module docstring) confirms this directly: zero
demand-shortfall days before the drought, all of them during/after it.

## The two models

- **`M_naive_calendar`**: dynamic harmonic regression (Fourier terms + ARMA
  errors — the same recipe validated in `../multi_frequency_timeseries/parametric/`)
  fit directly to historical *generation*. It never sees rain, inflow, or
  storage. This is what "just forecast the output series" looks like, done
  well by ordinary time-series standards.
- **`M_structural_esp`**: ESP logic. Takes today's true observed storage,
  a day-of-year climatological inflow profile (computed only from training
  data), a Fourier+ARMA demand forecast, and runs `simulate_dispatch` —
  the *exact same* mass-balance/rule-curve function used to generate the
  truth — forward from there. It is simplified to the climatological *mean*
  trajectory rather than a full ensemble of historical years; a real ESP
  system would keep the ensemble spread as a forecast uncertainty band,
  which this collapsed version discards (see limitation below).

## Results

Walk-forward backtest, expanding window, 8 folds of 100 days each, spanning
before/during/after the drought (`experiment.py`, `plots/metrics.csv`):

| regime | M_naive_calendar RMSE | M_structural_esp RMSE | naive persistence RMSE |
|---|---|---|---|
| pre-drought | 0.78 | 0.78 | 1.99 |
| drought | 3.10 | 2.93 | **2.62** |
| post-drought | 1.72 | **0.70** | 4.46 |

(`plots/rmse_by_regime.png`)

**Pre-drought: no difference.** When water isn't binding, generation really
is just a calendar-driven series, and the naive model is exactly as good as
the structural one — there's nothing wrong with a seasonal model *when the
constraint isn't active*. This matters: the extra structure isn't free
(it needed rain and storage data, a routing/dispatch model, calibration),
and it earns nothing until the constraint actually bites.

**The moment the drought starts, neither model sees it coming**
(`plots/drought_onset_forecast.png`). Storage is still near its seasonal
peak on day one of the drought — the deficit hasn't had time to show up in
the state yet — so both models forecast a normal season ahead. This is
ESP's real, literature-acknowledged limitation: it propagates today's known
state correctly, it does not predict tomorrow's rain. No amount of
structural correctness substitutes for information nobody has yet.

Notice `naive_persistence` actually *wins* the drought-regime bucket
(2.62) over both real models — repeating yesterday's value tracks a
monotonic collapse-then-flatline better than either a fixed seasonal curve
or a model that (as below) initially overshoots the speed of recovery.
Averaging over a regime that mixes "just starting to fall" with "already
at zero" rewards whichever model happens to have the right bias for most
of that mix, more than it rewards being structurally correct — which is
exactly why the single-fold plot below, not just the regime table, is the
one to trust.

**Once generation has already fallen short of demand, the models sharply
diverge** (`plots/drought_established_forecast.png`, forecast from the
first day the true system is actually rationed). `M_naive_calendar` — now
just a fixed seasonal curve, no ARMA anywhere — keeps riding that curve at
6-8 units, completely blind to the fact that today's true generation is
already down at ~1.2; actual generation stays near zero for another three
months while the naive forecast never reflects it. `M_structural_esp`
starts exactly where it should, right at today's true depleted output, and
climbs — a little too fast, since it assumes climatological (average)
inflow going forward and the drought continues worse than average
(`plots/storage_projection.png` shows the same gap from the storage side:
projected storage climbs back up on assumed-average future rain while the
true curve keeps falling to zero) — but every day of that climb is closer
to the truth than the naive model's flat, oblivious 6-8. It's not perfect;
it's unambiguously anchored to reality in a way nothing else here is.

**After the drought "ends," the gap is largest** (0.70 vs. 1.72 RMSE).
Storage takes a long time to refill even once normal rain resumes, so
generation stays suppressed well past the point a calendar model would
expect a full recovery. The structural model, still anchored on the true
(still-low) storage, gets this right; the calendar-only model — even after
being retrained on data that now includes the drought — has no mechanism to
know recovery isn't yet complete for the current storage level. **The
biggest cost of ignoring state isn't the crisis itself, it's misjudging how
long the recovery takes.**

## Practical takeaway

- Additive slow+fast decomposition (the earlier studies) is the right frame
  when the process really is additive. The moment there's a hard, physical
  *constraint* linking output to an exogenous driver, decomposing the output
  series statistically — however carefully — cannot recover what a
  mechanistic model gets for free: a channel for today's true, observed
  state to enter the forecast.
- The value of that channel is asymmetric with the regime: it's free
  (costs nothing extra vs. a calendar model) when the constraint isn't
  binding, and it's the entire difference between a plausible forecast and
  a badly wrong one once the constraint starts binding — and it stays
  valuable through the recovery, arguably longer than through the event
  itself.
- A structural model still can't predict the rain. ESP-style approaches
  are honest about that: they get today's state right and let the
  forecast be wrong about tomorrow's weather in a bounded, climatologically
  reasonable way, rather than wrong about the state itself. Do not expect
  even a well-built structural model to nail the depth or exact timing of
  an anomalous event — only to be right about the mechanism, which is
  already most of the value.
- If you actually operate a system like this, the natural next step past
  what's here is a real ESP ensemble (many historical rain years run
  through the same dispatch model, not just their mean) so the output is a
  forecast distribution with an honest worst-case tail, not a single
  climatological point estimate that is itself biased during an anomalous
  year — which is a documented failure mode of exactly this simplification.

## Part 2: what if storage isn't observed either?

Part 1 above assumed the operator can read the reservoir's true storage
level off a gauge. That's often not true of the *forecasting* system: many
real setups only have weather (rain, and its lags/accumulations) and
calendar as model inputs, storage is a latent internal state nobody
telemeters into the model, and a separate process (not this one) already
produces a net demand forecast that this system is simply handed. That's a
meaningfully harder and more common problem, and it's the one this section
answers: **given only weather history + calendar, and a demand forecast you
don't have to produce yourself, how should you fit water's effect on
generation — as one joint function, or as two separate functions combined
by the known structural rule?** No AR/ARMA anywhere in this section either
— every model is a plain OLS regression (`decomposition_models.py`), and
`simulate.py`'s demand process was rewired to be genuinely
`f(temperature, calendar)` with i.i.d. noise so there's nothing but real
structure left to model.

Three models, all given the same demand forecast (simulated as the true
future demand — see the caveat below) and the same rain history, differing
only in how they use the rain signal:

- **`demand_only`**: ignore water entirely, `generation_hat = demand_forecast`.
- **`joint`**: one OLS regression of generation on rain-derived features +
  annual calendar + the demand forecast, all at once — additive by
  construction.
- **`separate_cascade`**: a *ceiling* regression — generation ~ rain-derived
  features + annual calendar, fit against historical generation — combined
  with the demand forecast via the actual structural rule,
  `generation_hat = min(demand_forecast, ceiling_hat)`.

Since storage is latent, "rain-derived features" has to proxy for it. The
standard hydrological answer is the **Antecedent Precipitation Index**
(Kohler & Linsley, 1951): `API(t) = rain(t) + k·API(t-1)`, a causal
exponential integrator of past rain. A first version of this study used four
overlapping fixed-window rainfall sums (7/30/90/365 days) instead, and it
barely worked — those windows are highly collinear with each other and none
of them is tuned to the system's actual memory. Switched to two API terms:
a fast one, and a slow one with decay `k = 1 - EVAP_RATE` — deliberately
matched to the true (latent) reservoir's own day-to-day persistence, since
storage that receives no inflow decays geometrically at exactly that rate.
(This is the one place the study "cheats," reusing a simulator constant to
choose a decay rate — done deliberately to show what a *physically matched*
memory length buys over an arbitrary calendar-convenient one; a real
deployment would instead calibrate the decay against historical
recession curves, which is exactly how hydrologists set an API's k in
practice.)

### Results

Same walk-forward backtest, by regime (`decomposition_experiment.py`,
`plots/decomp_metrics.csv`):

| regime | demand_only | joint | separate_cascade |
|---|---|---|---|
| pre-drought | **0.00** | 0.00 | 0.98 |
| drought | **2.78** | 2.77 | 2.92 |
| post-drought | **0.76** | 1.41 | 1.73 |

Headline: with a perfect given demand forecast, **nothing beats
`demand_only` in aggregate** — the opposite of Part 1's conclusion. Two
real mechanisms are behind that, and they're the actual answer to
"jointly or separately":

**`joint` barely uses the rain signal at all.** Across an entire multi-year
history, most days are not water-limited, so the single additive
coefficient on the rain-derived features gets estimated mostly from days
where rain and generation have nothing to do with each other, diluting it
toward ~0. It ends up statistically indistinguishable from `demand_only` —
safe, but not doing the one thing it was added for.

**`separate_cascade`'s explicit `min()` is structurally correct — and it
still isn't enough**, for a sharp, important reason:
`plots/decomp_ceiling_vs_demand.png` and `plots/decomp_drought_established_forecast.png`
show a forecast made 200 days into the drought (fold 4's origin, the fold
where the cascade *does* beat the alternatives — 6.6 vs. 7.8 RMSE). The
ceiling regression's own forecast barely moves off ~6 for the entire
300-day horizon, while true generation is already at 3.7 and cratering to
0. **The regression is extrapolating.** By day 200 of the drought, the
antecedent rain index has fallen well below anything in its training
history — the training window (mostly ordinary years) taught it a roughly
linear relationship between "somewhat low rain" and "somewhat reduced
output," and it has no way to know that relationship gets dramatically
steeper once rain falls into territory it's never seen. This is the exact
same failure mode as the tree-extrapolation finding in the earlier XGBoost
study, now showing up in a linear model: **no amount of correct-within-range
feature engineering fixes a forecast that has to extrapolate past
everything the model was ever fit on.** Quantile regression at low tau and
an explicit hinge/knot feature (both tried; see git history) barely moved
this number, because the constraint is genuinely novel at that point, not
just underweighted.

**And decomposition has a real, recurring cost that `demand_only` and
`joint` don't pay**: pre-drought, when water was never once limiting,
`separate_cascade` still posts RMSE 0.98 against `demand_only`'s exact 0.00.
The ceiling regression's own estimation noise occasionally predicts a
ceiling *below* the true (non-binding) demand, spuriously suppressing an
otherwise-perfect forecast. This is the asymmetry worth remembering: a
`min()`-combined model can only ever help when the constraint is both real
and *within the range the ceiling function has seen before* — everywhere
else, it's pure downside.

### The actual answer to "jointly vs. separately"

- **Separate, combined by the true structural rule (`min`), is the
  correct architecture** — it's the only one of the three that can express
  "generation follows demand until water runs out, then it doesn't," which
  is what's actually happening. `joint`'s additive form cannot express that
  switch at all, at any amount of data.
- **But architecture alone doesn't rescue a function that's extrapolating.**
  Decomposition only pays off in the overlap between "the training history
  has enough precedent to calibrate the ceiling" and "the current event
  hasn't exceeded that precedent" — fold 4 here, not the folds immediately
  before or after it.
- **This is why Part 1's storage-observing model was so much better**: it
  never had to *learn* the constraint from historical rain-to-output pairs
  at all. Mass balance is valid at a storage level regardless of whether
  that level was ever seen historically — a mechanistic model anchored on
  the true current state doesn't extrapolate in the sense that breaks a
  regression, because it isn't fitting a historical relationship in the
  first place. If there is *any* way to get even an imperfect telemetry
  read on the true latent state into this system, it is worth more than
  every feature-engineering trick tried in this section combined.
- **Practically**: fit separately, combine with the true structural rule,
  and treat the ceiling function's performance outside its training range
  as an open question, not an assumption — check it explicitly (as the
  ceiling-vs-demand plot does here) rather than trusting the aggregate
  RMSE, which can hide a model that's right on average and badly wrong
  exactly when it matters.

### Caveat

This section assumes the given net demand forecast is exactly correct
(simulated as true future demand). A real demand-forecasting system carries
its own error, which would partially blur the `min()` combination's sharp
edge — but it doesn't change the core finding, since that finding is about
the *water* function's extrapolation failure, not the demand function.

## Files

- `simulate.py` — the causal generator: rain → inflow → storage → generation
  → net demand `f(temperature, calendar)`, every equation documented with
  citations to the conceptual-hydrology literature it's modelled on.
- `models.py` — Part 1's two storage-observing forecasting strategies.
- `experiment.py` — Part 1's walk-forward backtest by regime + plots.
- `decomposition_models.py` — Part 2's three weather+calendar-only strategies.
- `decomposition_experiment.py` — Part 2's walk-forward backtest + plots.
- `plots/` — every figure referenced above, plus `metrics.csv` /
  `decomp_metrics.csv`.

## Sources

- [Troin et al. (2021), "Generating Ensemble Streamflow Forecasts: A Review of Methods and Approaches Over the Past 40 Years", *Water Resources Research*](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2020WR028392)
- [NOAA/NWS training, "Ensemble Streamflow Prediction (ESP)"](https://training.weather.gov/nwstc/Hydrology/HYDRO/RFS/RFS802.html)
- [Anghileri et al. (2019), "Analysis of the effects of biases in ensemble streamflow prediction (ESP) forecasts on electricity production in hydropower reservoir management", *HESS*](https://hess.copernicus.org/articles/23/2735/2019/)
- ["HBV lumped conceptual hydrological model"](https://medium.com/hydroinformatics/hbv-lumped-conceptual-hydrological-model-b0a75b4e61d0) and the [ABCD conceptual rainfall-runoff model](https://rdrr.io/github/tanerumit/hydrosystems/man/abcdQest.html) — both linear/nonlinear-reservoir-cascade conceptual models
- ["Beyond the Rule Curve: How Reservoir Operations Modeling Is Transforming Water Management Decision-Making", National Hydropower Association](https://hydro.org/powerhouse/article/beyond-the-rule-curve-how-reservoir-operations-modeling-is-transforming-water-management-decision-making/)
- [Neitsch et al., HESS, "Modeling hydropower operations at the scale of a power grid: a demand-based approach"](https://hess.copernicus.org/articles/28/5479/2024/)
- ["Hydropower Generation Forecasting: Flow → Production Chain and Why Forecast Errors Are Costly"](https://renewasoft.com.tr/index.php/en/2026/02/26/hydropower-generation-forecasting/)
- Kohler, M.A. & Linsley, R.K. (1951), "Predicting the Runoff from Storm Rainfall" (U.S. Weather Bureau) — the original Antecedent Precipitation Index; see any modern hydrology text (e.g. the HBV/ABCD sources above) for the standard causal-exponential-decay formulation used here.
