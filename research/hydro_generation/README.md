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
- **Net demand**: the load assigned to hydro after other generation — reuses
  the annual+weekly harmonic structure from the earlier studies.
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
| pre-drought | 0.73 | 0.70 | 2.43 |
| drought | 4.32 | **3.58** | 4.18 |
| post-drought | 2.79 | **0.81** | 4.45 |

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

**100 days in, once the deficit has shown up in storage, the models sharply
diverge** (`plots/drought_established_forecast.png`). `M_naive_calendar`
just keeps riding its fitted seasonal curve down through a slow ARMA-driven
decay — plausible-looking, completely wrong; actual generation is at zero
for months while the naive forecast is still predicting 6-14 units.
`M_structural_esp` drops immediately toward the true collapse because it
starts from today's already-depleted true storage, and its rule-curve logic
correctly turns that into a generation ceiling. It's not perfect — it
assumes climatological (average) inflow going forward, so when the drought
continues worse than average it recovers too early and too high relative
to the truth (`plots/storage_projection.png` shows the same gap: the
projected storage curve dips toward the threshold, then climbs back up
on assumed-average future rain, while the true curve keeps falling to
zero) — but it is unambiguously closer to reality throughout, and it
correctly identifies *that* a shortfall is happening, which the naive
model cannot do at all.

**After the drought "ends," the gap is largest** (0.81 vs. 2.79 RMSE).
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

## Files

- `simulate.py` — the causal generator: rain → inflow → storage → generation,
  every equation documented with citations to the conceptual-hydrology
  literature it's modelled on.
- `models.py` — the two forecasting strategies.
- `experiment.py` — walk-forward backtest by regime + all plots.
- `plots/` — every figure referenced above, plus `metrics.csv`.

## Sources

- [Troin et al. (2021), "Generating Ensemble Streamflow Forecasts: A Review of Methods and Approaches Over the Past 40 Years", *Water Resources Research*](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2020WR028392)
- [NOAA/NWS training, "Ensemble Streamflow Prediction (ESP)"](https://training.weather.gov/nwstc/Hydrology/HYDRO/RFS/RFS802.html)
- [Anghileri et al. (2019), "Analysis of the effects of biases in ensemble streamflow prediction (ESP) forecasts on electricity production in hydropower reservoir management", *HESS*](https://hess.copernicus.org/articles/23/2735/2019/)
- ["HBV lumped conceptual hydrological model"](https://medium.com/hydroinformatics/hbv-lumped-conceptual-hydrological-model-b0a75b4e61d0) and the [ABCD conceptual rainfall-runoff model](https://rdrr.io/github/tanerumit/hydrosystems/man/abcdQest.html) — both linear/nonlinear-reservoir-cascade conceptual models
- ["Beyond the Rule Curve: How Reservoir Operations Modeling Is Transforming Water Management Decision-Making", National Hydropower Association](https://hydro.org/powerhouse/article/beyond-the-rule-curve-how-reservoir-operations-modeling-is-transforming-water-management-decision-making/)
- [Neitsch et al., HESS, "Modeling hydropower operations at the scale of a power grid: a demand-based approach"](https://hess.copernicus.org/articles/28/5479/2024/)
- ["Hydropower Generation Forecasting: Flow → Production Chain and Why Forecast Errors Are Costly"](https://renewasoft.com.tr/index.php/en/2026/02/26/hydropower-generation-forecasting/)
