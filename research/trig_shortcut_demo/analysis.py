"""Fit three OLS models on TRAIN (days 0-1999, no anomaly ever seen):

    trig_only     Y ~ sin + cos
    causal_only   Y ~ W_obs
    both          Y ~ sin + cos + W_obs

Then:
  1. Show `both`'s coefficient on W_obs collapses relative to `causal_only`'s
     -- trig steals the cheap (noiseless, seasonal) variance, leaving W_obs
     to fight for only the anomalous residual, where its own noise dominates.
  2. Check that collapse against the closed-form prediction from the
     Frisch-Waugh-Lovell theorem + classical errors-in-variables attenuation:
     coef_on_W_obs (both) ~= Var(eps_train) / (Var(eps_train) + Var(u)).
  3. Score all three OUT OF SAMPLE on a normal window and on the anomaly --
     the point of the whole exercise.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

import simulate as sim

PLOTS_DIR = "plots"
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 10})


def fit_ols(df, y_col, x_cols):
    X = sm.add_constant(df[list(x_cols)])
    return sm.OLS(df[y_col], X).fit()


def predict(res, df, x_cols):
    X = sm.add_constant(df[list(x_cols)], has_constant="add")
    return res.predict(X)


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def main():
    import os

    os.makedirs(PLOTS_DIR, exist_ok=True)
    df = sim.generate()
    train = df.iloc[:sim.TRAIN_END]
    normal_test = df.iloc[sim.ANOMALY_END:sim.ANOMALY_END + 200]
    anomaly_test = df.iloc[sim.ANOMALY_START:sim.ANOMALY_END]

    m_trig = fit_ols(train, "Y", ["sin", "cos"])
    m_causal = fit_ols(train, "Y", ["W_obs"])
    m_both = fit_ols(train, "Y", ["sin", "cos", "W_obs"])

    var_eps_train = train["eps"].var()
    theoretical_ratio = var_eps_train / (var_eps_train + sim.U_SIGMA ** 2)

    print("=== Coefficient on W_obs ===")
    print(f"causal_only model: {m_causal.params['W_obs']:.4f}")
    print(f"both model:        {m_both.params['W_obs']:.4f}")
    print(f"theory (Var(eps)/(Var(eps)+Var(u))): {theoretical_ratio:.4f}")
    print()

    rows = []
    for name, res, cols in [("trig_only", m_trig, ["sin", "cos"]),
                             ("causal_only", m_causal, ["W_obs"]),
                             ("both", m_both, ["sin", "cos", "W_obs"])]:
        for label, test in [("normal_holdout", normal_test), ("anomaly", anomaly_test)]:
            pred = predict(res, test, cols)
            rows.append({"model": name, "window": label, "rmse": rmse(test["Y"], pred)})
    results = pd.DataFrame(rows)
    print(results.pivot(index="model", columns="window", values="rmse").round(3))
    results.to_csv(f"{PLOTS_DIR}/metrics.csv", index=False)

    # --- plot 1: the true driver, its noisy proxy, and what trig can see ---
    window = slice(sim.ANOMALY_START - 200, sim.ANOMALY_END + 200)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(df["t"].iloc[window], df["W_true"].iloc[window], color="black", lw=1.4, label="W_true (the real cause)")
    ax.plot(df["t"].iloc[window], df["W_obs"].iloc[window], color="#2f6f9f", lw=0.8, alpha=0.6,
             label="W_obs (noisy proxy -- all a model can measure)")
    ax.plot(df["t"].iloc[window], df["S"].iloc[window], color="#d1495b", lw=1.6, ls="--",
             label="S(t) -- everything trig(t) can ever represent")
    ax.axvspan(sim.ANOMALY_START, sim.ANOMALY_END, color="gray", alpha=0.15, label="anomaly (never in training)")
    ax.set_xlabel("t"); ax.set_title("The anomaly is real in W_true/W_obs -- invisible to trig(t)")
    ax.legend(fontsize=8)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/driver_vs_proxy.png")
    plt.close(fig)

    # --- plot 2: coefficient collapse ---
    fig, ax = plt.subplots(figsize=(7, 5.2))
    bars = ax.bar(["causal_only\n(W_obs alone)", "both\n(trig available too)", "theory\n(FWL + attenuation)"],
                   [m_causal.params["W_obs"], m_both.params["W_obs"], theoretical_ratio],
                   color=["#2f6f9f", "#d1495b", "#9aa5b1"])
    ax.axhline(1.0, color="black", ls=":", lw=1, label="true causal effect of W_true on Y (=1)")
    ax.set_ylabel("fitted coefficient on W_obs")
    ax.set_title("Adding a noiseless trig proxy crushes the real driver's coefficient")
    ax.legend(fontsize=8)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/coefficient_collapse.png")
    plt.close(fig)

    # --- plot 3: forecasts through the anomaly ---
    window2 = slice(sim.ANOMALY_START - 100, sim.ANOMALY_END + 100)
    sub = df.iloc[window2]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(sub["t"], sub["Y"], color="black", lw=1.6, label="actual Y")
    ax.plot(sub["t"], predict(m_trig, sub, ["sin", "cos"]), color="#d1495b", lw=1.3, label="trig_only")
    ax.plot(sub["t"], predict(m_both, sub, ["sin", "cos", "W_obs"]), color="#edae49", lw=1.3, label="both")
    ax.plot(sub["t"], predict(m_causal, sub, ["W_obs"]), color="#2f6f9f", lw=1.3, label="causal_only (W_obs)")
    ax.axvspan(sim.ANOMALY_START, sim.ANOMALY_END, color="gray", alpha=0.12)
    ax.set_xlabel("t"); ax.set_title("Out-of-sample forecasts through the never-seen anomaly")
    ax.legend(fontsize=8)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/forecast_through_anomaly.png")
    plt.close(fig)

    print("\nPlots written to", PLOTS_DIR)


if __name__ == "__main__":
    main()
