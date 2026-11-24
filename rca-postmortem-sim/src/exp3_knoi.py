"""Deney 3: KNÖİ (P = E*T*Y) puanlarının Monte Carlo duyarlılık analizi."""
import numpy as np, pandas as pd
from scipy import stats

SEED = 42
N = 10_000
BASE = {"KN1": (5, 4, 4), "KN2": (5, 5, 5), "KN3": (4, 4, 4), "KN4": (3, 3, 4), "KN5": (2, 2, 3)}
NAMES = list(BASE)

def run(out):
    base = np.array([BASE[k] for k in NAMES])           # 5x3
    base_p = base.prod(axis=1)
    base_order = np.argsort(-base_p)
    rng = np.random.default_rng(SEED)
    scenarios = {"S1: her puan p=0.5 ile ±1": ("pm1", 0.5), "S2: her puan {-1,0,+1} eşit olasılık": ("u1", None),
                 "S3: her puan {-2..+2} eşit olasılık": ("u2", None)}
    rows, rank_rows = [], []
    for name, (kind, p) in scenarios.items():
        if kind == "pm1":
            delta = rng.choice([-1, 1], size=(N, 5, 3)) * (rng.random((N, 5, 3)) < p)
        elif kind == "u1":
            delta = rng.integers(-1, 2, size=(N, 5, 3))
        else:
            delta = rng.integers(-2, 3, size=(N, 5, 3))
        s = np.clip(base[None] + delta, 1, 5)
        P = s.prod(axis=2)                                # N x 5
        kn2 = NAMES.index("KN2")
        strict_first = (P[:, kn2] > np.delete(P, kn2, axis=1).max(axis=1)).mean()
        tie_first = (P[:, kn2] >= np.delete(P, kn2, axis=1).max(axis=1)).mean()
        srt = -np.sort(-P, axis=1)
        top3_strict = srt[:, 2] > srt[:, 3]
        top3_same = np.array([set(np.argsort(-P[i])[:3]) == set(base_order[:3]) for i in range(N)]) & top3_strict
        rho = np.array([stats.spearmanr(P[i], base_p)[0] for i in range(N)])
        order_same = np.array([(np.argsort(-P[i], kind="stable") == base_order).all() for i in range(N)]) & (np.diff(-srt, axis=1) != 0).all(axis=1)
        rows.append({"scenario": name, "P_KN2_strictly_first": round(strict_first, 4), "P_KN2_first_incl_ties": round(tie_first, 4),
                     "P_top3_set_unchanged_strict": round(top3_same.mean(), 4), "P_full_order_unchanged_strict": round(order_same.mean(), 4),
                     "mean_spearman_rho": round(float(np.nanmean(rho)), 4), "min_KN2_score": int(P[:, kn2].min())})
        ranks = stats.rankdata(-P, axis=1, method="min")
        for j, k in enumerate(NAMES):
            rank_rows.append({"scenario": name, "cause": k, **{f"P_rank_{r}": round(float((ranks[:, j] == r).mean()), 4) for r in range(1, 6)}})
    pd.DataFrame(rows).to_csv(out, index=False)
    pd.DataFrame(rank_rows).to_csv(out.replace(".csv", "_ranks.csv"), index=False)
    return pd.DataFrame(rows), pd.DataFrame(rank_rows)

if __name__ == "__main__":
    a, b = run("results/exp3_knoi.csv")
    print(a.to_string(index=False)); print(b.to_string(index=False))
