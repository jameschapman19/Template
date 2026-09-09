"""Three follow-up questions, each answered with a sweep rather than a claim:

  A. Does the coefficient collapse depend on the noise level?
     Sweep Var(eps_train) and Var(u) over a grid; check the fitted
     coefficient on W_obs (in the presence of trig) against the closed-form
     Var(eps)/(Var(eps)+Var(u)) prediction at every point, not just one.

  B. Will more data fix it?
     Fix the generative process (same normal-only regime) and grow N. Track
     the coefficient's mean and its standard error across seeds. Bias vs.
     variance: does the estimate's *center* move toward the truth, or does
     it just get more precisely wrong?

  C. What if "more data" means more diverse data?
     Instead of more days of the same small-noise regime, inject occasional
     larger excursions of the true driver into training (still never the
     held-out anomaly itself) and watch Var(eps_train) rise -- and the
     coefficient rise with it, exactly as the formula predicts.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

import simulate as sim

PLOTS_DIR = "plots"
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 10})


def generate_normal_only(n_days_wanted, seed, **kwargs):
    """sim.generate()'s anomaly window sits at a fixed (ANOMALY_START,
    ANOMALY_END), regardless of n_days -- so naively asking for n_days_wanted
    > ANOMALY_START would silently pull the anomaly itself into "training"
    for every sweep below. Over-generate, drop the anomaly rows, then trim.
    """
    total = n_days_wanted + (sim.ANOMALY_END - sim.ANOMALY_START) + 50
    df = sim.generate(n_days=total, seed=seed, **kwargs)
    df = df[~df["anomaly"]].reset_index(drop=True)
    return df.iloc[:n_days_wanted]


def fit_both_coef(df):
    X = sm.add_constant(df[["sin", "cos", "W_obs"]])
    res = sm.OLS(df["Y"], X).fit()
    return res.params["W_obs"], res.bse["W_obs"]


def experiment_a_noise_dependence():
    eps_sigmas = [0.2, 0.4, 0.8, 1.5, 3.0]
    u_sigmas = [0.3, 0.8, 1.5, 3.0, 6.0]
    rows = []
    for eps_s in eps_sigmas:
        for u_s in u_sigmas:
            df = generate_normal_only(40000, seed=1, eps_sigma_normal=eps_s, u_sigma=u_s)
            coef, _ = fit_both_coef(df)
            theory = eps_s ** 2 / (eps_s ** 2 + u_s ** 2)
            rows.append({"eps_sigma": eps_s, "u_sigma": u_s, "fitted": coef, "theory": theory})
    results = pd.DataFrame(rows)
    results.to_csv(f"{PLOTS_DIR}/noise_sweep.csv", index=False)

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.scatter(results["theory"], results["fitted"], c=np.log(results["eps_sigma"] / results["u_sigma"]),
               cmap="coolwarm", s=60, edgecolor="black", linewidth=0.4)
    lims = [0, 1]
    ax.plot(lims, lims, color="gray", ls="--", lw=1, label="y = x (perfect agreement)")
    ax.set_xlabel("theory: Var(eps) / (Var(eps) + Var(u))")
    ax.set_ylabel("fitted coefficient on W_obs (trig available)")
    ax.set_title("A: the collapse is exactly the noise ratio, across 25 regimes")
    ax.legend(fontsize=8)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/a_noise_dependence.png")
    plt.close(fig)
    print("A: max abs error theory vs fitted:", (results["theory"] - results["fitted"]).abs().max())


def experiment_b_more_data_same_regime():
    Ns = [500, 1000, 2000, 5000, 10000, 30000, 100000, 300000]
    seeds = range(20)
    rows = []
    for n in Ns:
        for seed in seeds:
            df = generate_normal_only(n, seed=seed)
            coef, se = fit_both_coef(df)
            rows.append({"n": n, "seed": seed, "coef": coef})
    results = pd.DataFrame(rows)
    agg = results.groupby("n")["coef"].agg(["mean", "std"])
    results.to_csv(f"{PLOTS_DIR}/data_scaling.csv", index=False)

    theory = sim.EPS_SIGMA_NORMAL ** 2 / (sim.EPS_SIGMA_NORMAL ** 2 + sim.U_SIGMA ** 2)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.errorbar(agg.index, agg["mean"], yerr=agg["std"], fmt="o-", color="#2f6f9f", capsize=3,
                label="fitted coefficient on W_obs (mean +/- std over 20 seeds)")
    ax.axhline(1.0, color="black", ls=":", lw=1.2, label="true causal effect (=1)")
    ax.axhline(theory, color="#d1495b", ls="--", lw=1.2, label="theoretical asymptote (biased)")
    ax.set_xscale("log")
    ax.set_xlabel("training days (all from the SAME normal-only regime)")
    ax.set_ylabel("fitted coefficient on W_obs")
    ax.set_title("B: more data of the same regime converges precisely -- to the wrong answer")
    ax.legend(fontsize=8)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/b_more_data_same_regime.png")
    plt.close(fig)
    print("B: coefficient at N=500:", agg.loc[500, "mean"], "+/-", agg.loc[500, "std"])
    print("B: coefficient at N=300000:", agg.loc[300000, "mean"], "+/-", agg.loc[300000, "std"])


def experiment_c_more_diverse_data():
    fracs = [0.0, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20]
    rows = []
    for frac in fracs:
        for seed in range(10):
            df = generate_normal_only(20000, seed=seed, mini_anomaly_frac=frac, mini_anomaly_scale=4.0)
            coef, _ = fit_both_coef(df)
            realized_var_eps = df["eps"].var()
            theory = realized_var_eps / (realized_var_eps + sim.U_SIGMA ** 2)
            rows.append({"frac": frac, "seed": seed, "coef": coef, "theory": theory,
                         "var_eps": realized_var_eps})
    results = pd.DataFrame(rows)
    agg = results.groupby("frac")[["coef", "theory", "var_eps"]].mean()
    results.to_csv(f"{PLOTS_DIR}/diversity_sweep.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.plot(agg.index * 100, agg["coef"], "o-", color="#2f6f9f", label="fitted coefficient on W_obs")
    ax.plot(agg.index * 100, agg["theory"], "s--", color="#d1495b", label="theory at realized Var(eps)")
    ax.axhline(1.0, color="black", ls=":", lw=1, label="true causal effect (=1)")
    ax.set_xlabel("% of training days with a mini-excursion of the true driver")
    ax.set_ylabel("fitted coefficient on W_obs")
    ax.set_title("C: more DIVERSE data (not just more of it) recovers the true driver")
    ax.legend(fontsize=8)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/c_more_diverse_data.png")
    plt.close(fig)
    print("C:\n", agg)


def experiment_d_sequential_fit_fix():
    """One concrete avoidance strategy: don't fit trig and the causal proxy
    symmetrically. Give the causal channel first claim on the variance
    (fit Y ~ W_obs alone, i.e. exactly `causal_only` from analysis.py), and
    only then let trig mop up whatever's left. This is a domain-knowledge
    ordering choice, not something OLS does on its own.
    """
    df = generate_normal_only(sim.TRAIN_END, seed=0)
    coef_joint, _ = fit_both_coef(df)
    X = sm.add_constant(df[["W_obs"]])
    coef_causal_first = sm.OLS(df["Y"], X).fit().params["W_obs"]
    print(f"D: symmetric joint fit coefficient on W_obs: {coef_joint:.3f}")
    print(f"D: causal-first (sequential) fit coefficient on W_obs: {coef_causal_first:.3f}")
    return coef_joint, coef_causal_first


if __name__ == "__main__":
    import os

    os.makedirs(PLOTS_DIR, exist_ok=True)
    print("=== Experiment A: noise dependence ===")
    experiment_a_noise_dependence()
    print("\n=== Experiment B: more data, same regime ===")
    experiment_b_more_data_same_regime()
    print("\n=== Experiment C: more diverse data ===")
    experiment_c_more_diverse_data()
    print("\n=== Experiment D: sequential-fit fix ===")
    experiment_d_sequential_fit_fix()
    print("\nPlots written to", PLOTS_DIR)
