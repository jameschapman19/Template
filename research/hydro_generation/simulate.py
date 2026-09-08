"""Synthetic hydropower system: rain -> water -> generation, with a genuine
causal chain and a physical constraint, not just three correlated seasonal
curves. Every step is a named, parametric, documented equation, following
the conceptual-hydrology "linear reservoir" family (HBV/ABCD/Stanford
Watershed Model all use cascades of linear/nonlinear reservoirs -- see
README.md for citations) and standard reservoir "rule curve" operating logic.

    rain(t)        stochastic: seasonal wet-day probability x gamma amount,
                   with an explicit multi-year DROUGHT window where both are
                   suppressed.
    inflow(t)      = catchment routing of rain(t): a linear-reservoir filter
                   (exponential smoothing) standing in for travel-time lag
                   through soil and channel storage.
    storage S(t)   mass balance: S(t) = S(t-1) + inflow(t) - evaporation(t)
                   - env_flow - generation(t), clipped to [0, CAPACITY]
                   (excess is spill).
    temperature(t) the weather variable that drives demand (independent of
                   rain, the weather variable that drives water): seasonal +
                   i.i.d. noise, no autocorrelation.
    net_demand(t)  = f(temperature, calendar): a heating-degree-day response
                   to temperature plus a day-of-week effect, both linear,
                   plus i.i.d. noise -- the load assigned to hydro after
                   other generation (solar, wind, thermal) is dispatched.
    generation(t)  dispatch: hydro tries to follow net_demand up to turbine
                   capacity, but a rule-curve constraint cuts the maximum
                   allowed release when storage is below a threshold -- this
                   is the one nonlinearity that makes "just fit a seasonal
                   curve to historical generation" fail once a drought pushes
                   storage below that threshold.

This is what makes the problem genuinely different from the earlier studies:
generation is not additively composed of a slow and a fast part. It is
min(demand-driven target, a water-availability ceiling that can collapse
for months at a time) -- a hard, state-dependent, nonlinear constraint.
"""
import numpy as np
import pandas as pd

N_DAYS = 2200
START = "2018-01-01"

# --- rain -----------------------------------------------------------------
WET_DAY_PEAK = 15          # day-of-year the wet season is centred on
P_WET_MIN, P_WET_MAX = 0.10, 0.32
GAMMA_SHAPE = 1.6
GAMMA_SCALE_BASE = 40.0

DROUGHT_START, DROUGHT_END = 1500, 1800   # ~a year of severely suppressed rain
DROUGHT_FACTOR = 0.30

# --- catchment routing (linear reservoir filter) ---------------------------
ROUTE_K = 0.25             # smaller = longer catchment memory

# --- reservoir --------------------------------------------------------------
# Calibrated so mean inflow comfortably exceeds mean demand in the normal
# regime (storage settles well above the rule-curve threshold, so release is
# unconstrained) but the ~300-day drought's inflow cut is deep and long
# enough to draw storage below that threshold for an extended stretch.
CAPACITY = 2500.0
INITIAL_STORAGE = 0.50 * CAPACITY
EVAP_RATE = 0.004          # fraction of storage evaporated per day
MIN_ENV_FLOW = 0.5         # compliance release, always leaves the reservoir

# --- dispatch ---------------------------------------------------------------
MAX_TURBINE_CAPACITY = 20.0
RULE_CURVE_FRACTION = 0.15   # release capacity ramps down below this * CAPACITY

# --- temperature (the weather variable that drives demand; independent of
# rain, which is the weather variable that drives water) -------------------
TEMP_MEAN = 15.0
TEMP_AMPLITUDE = 10.0        # deg C swing, coldest ~ TEMP_TROUGH_DAY
TEMP_TROUGH_DAY = 15
TEMP_NOISE_SD = 2.0          # i.i.d. day-to-day weather noise, no autocorrelation

# --- net demand assigned to hydro: net_demand = f(temperature, calendar) ---
# No AR/ARMA anywhere in this module: every noise term below is i.i.d. The
# "raw model" this study fits back out of these series should not need to
# invent autocorrelation structure that was never simulated in.
DEMAND_BASE = 5.5
DEMAND_TREND = 0.0009
HEATING_REF_TEMP = 18.0     # demand rises below this temperature (heating)
HEATING_SENSITIVITY = 0.30  # demand units per heating-degree-day
DEMAND_WEEKLY = {"sin1": 0.9, "cos1": 0.5}
DEMAND_NOISE_SD = 0.55


def seasonal_frac(t, peak_day, period=365.25):
    return 0.5 + 0.5 * np.cos(2 * np.pi * (t - peak_day) / period)


def simulate_rain(n_days, seed):
    rng = np.random.default_rng(seed)
    t = np.arange(n_days)
    wet_frac = seasonal_frac(t, WET_DAY_PEAK)
    p_wet = P_WET_MIN + (P_WET_MAX - P_WET_MIN) * wet_frac
    scale = GAMMA_SCALE_BASE * (0.7 + 0.6 * wet_frac)

    drought = (t >= DROUGHT_START) & (t < DROUGHT_END)
    p_wet = np.where(drought, p_wet * DROUGHT_FACTOR, p_wet)
    scale = np.where(drought, scale * DROUGHT_FACTOR, scale)

    is_wet = rng.random(n_days) < p_wet
    amount = rng.gamma(shape=GAMMA_SHAPE, scale=scale)
    rain = np.where(is_wet, amount, 0.0)
    return rain, drought


def route_inflow(rain):
    inflow = np.zeros_like(rain)
    inflow[0] = rain[0]
    for i in range(1, len(rain)):
        inflow[i] = ROUTE_K * rain[i] + (1 - ROUTE_K) * inflow[i - 1]
    return inflow


def simulate_temperature(n_days, seed):
    rng = np.random.default_rng(seed + 2)
    t = np.arange(n_days, dtype=float)
    seasonal = -TEMP_AMPLITUDE * np.cos(2 * np.pi * (t - TEMP_TROUGH_DAY) / 365.25)
    noise = rng.normal(0, TEMP_NOISE_SD, n_days)   # i.i.d. -- no AR
    return TEMP_MEAN + seasonal + noise


def simulate_demand(n_days, seed, temperature):
    """net_demand = f(weather, calendar): a heating-degree-day response to
    temperature (the weather term) plus a day-of-week effect (the calendar
    term), both linear/additive -- the same "raw regression" functional form
    the forecasting models below will try to recover. i.i.d. noise only.
    """
    rng = np.random.default_rng(seed + 1)
    t = np.arange(n_days, dtype=float)
    dow = t.astype(int) % 7
    w_weekly = 2 * np.pi * t / 7
    weekly = DEMAND_WEEKLY["sin1"] * np.sin(w_weekly) + DEMAND_WEEKLY["cos1"] * np.cos(w_weekly)

    heating_degree = np.maximum(HEATING_REF_TEMP - temperature, 0.0)
    weather_component = HEATING_SENSITIVITY * heating_degree

    noise = rng.normal(0, DEMAND_NOISE_SD, n_days)   # i.i.d. -- no AR
    demand = DEMAND_BASE + DEMAND_TREND * t + weather_component + weekly + noise
    return np.maximum(demand, 0.5)


def simulate_dispatch(inflow, demand, initial_storage=INITIAL_STORAGE):
    """The mechanistic core: given inflow and demand for every day, run the
    mass-balance + rule-curve dispatch forward and return storage and
    generation. Deterministic given its inputs -- this same function is both
    "the truth" (fed true simulated inflow) and, later, "the forecasting
    model" (fed a rain/inflow forecast instead).
    """
    n = len(inflow)
    storage = np.zeros(n)
    generation = np.zeros(n)
    spill = np.zeros(n)
    s_prev = initial_storage
    for i in range(n):
        potential = s_prev + inflow[i] - EVAP_RATE * s_prev - MIN_ENV_FLOW
        potential = max(potential, 0.0)
        target_release = min(demand[i], MAX_TURBINE_CAPACITY)
        max_allowed = MAX_TURBINE_CAPACITY * np.clip(s_prev / (RULE_CURVE_FRACTION * CAPACITY), 0.0, 1.0)
        gen = max(0.0, min(target_release, max_allowed, potential))
        s_new = potential - gen
        spill[i] = max(0.0, s_new - CAPACITY)
        s_new = min(s_new, CAPACITY)
        storage[i] = s_new
        generation[i] = gen
        s_prev = s_new
    return storage, generation, spill


def generate(n_days: int = N_DAYS, seed: int = 0) -> pd.DataFrame:
    idx = pd.date_range(START, periods=n_days, freq="D")
    rain, drought = simulate_rain(n_days, seed)
    inflow = route_inflow(rain)
    temperature = simulate_temperature(n_days, seed)
    demand = simulate_demand(n_days, seed, temperature)
    storage, generation, spill = simulate_dispatch(inflow, demand)

    return pd.DataFrame(
        {
            "rain": rain, "inflow": inflow, "temperature": temperature, "demand": demand,
            "storage": storage, "generation": generation, "spill": spill,
            "drought": drought,
        },
        index=idx,
    )


if __name__ == "__main__":
    df = generate()
    print(df.describe())
    print("days with generation < 90% of demand:", (df["generation"] < 0.9 * df["demand"]).sum())
