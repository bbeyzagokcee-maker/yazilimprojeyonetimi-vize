"""Deney 1: Simüle vaka için EVM/PERT hesaplarının yeniden üretimi ve PERT'in Monte Carlo sınaması."""
import numpy as np, pandas as pd
from scipy import stats

SEED = 42

def evm(bac, pv, ev, ac, planned_months):
    cpi, spi = ev / ac, ev / pv
    eac = bac / cpi
    return {"CPI": cpi, "SPI": spi, "EAC": eac, "overrun_pct": 100 * (eac - bac) / bac,
            "TCPI": (bac - ev) / (bac - ac), "forecast_months": planned_months / spi}

def pert(a, m, b, T):
    e, s = (a + 4 * m + b) / 6, (b - a) / 6
    z = (T - e) / s
    return e, s, z, stats.norm.sf(z)

def run(out):
    rows = []
    r = evm(2_400_000, 1_600_000, 900_000, 2_100_000, 18)
    for k, v in r.items(): rows.append(("EVM_" + k, round(v, 4)))
    # PERT (normal yaklaşım) - denklem (5)-(7)
    a, m, b, T = 3, 5, 12, 11
    e, s, z, p_norm = pert(a, m, b, T)
    rows += [("PERT_E", round(e, 4)), ("PERT_sigma", s), ("PERT_Z", round(z, 4)), ("P_T>=11_normal", p_norm)]
    # Beta-PERT (lambda=4): Monte Carlo ve kesin değer
    alpha = 1 + 4 * (m - a) / (b - a); beta = 1 + 4 * (b - m) / (b - a)
    rng = np.random.default_rng(SEED)
    samples = a + (b - a) * rng.beta(alpha, beta, 1_000_000)
    rows += [("betaPERT_alpha", round(alpha, 4)), ("betaPERT_beta", round(beta, 4)),
             ("P_T>=11_betaPERT_exact", stats.beta.sf((T - a) / (b - a), alpha, beta)),
             ("P_T>=11_betaPERT_MC_1e6", float((samples >= T).mean())),
             ("betaPERT_mean", float(samples.mean())), ("betaPERT_p95", float(np.quantile(samples, .95)))]
    # Üçgen dağılım duyarlılığı
    tri = rng.triangular(a, m, b, 1_000_000)
    rows.append(("P_T>=11_triangular_MC_1e6", float((tri >= T).mean())))
    df = pd.DataFrame(rows, columns=["metric", "value"]); df.to_csv(out, index=False); return df

if __name__ == "__main__":
    print(run("results/exp1_evm_pert.csv").to_string(index=False))
