"""Deney 2: Halka açık Kemerer (1987) veri setiyle tahmin hatası analizi ve K1 kuralının sınanması."""
import numpy as np, pandas as pd
from scipy import stats

SEED = 42

def mre(est, act): return np.abs(est - act) / act

def run(path, out):
    d = pd.read_csv(path)
    rows = []
    # 1) Yayımlanan MMRE ile doğrulama
    for col, pub in [("fpa_estimate_pm", 102.74), ("cocomo_estimate_pm", 583.82)]:
        mm = 100 * mre(d[col], d.actual_effort_pm).mean()
        rows += [(f"MMRE_pct_{col}", round(mm, 2)), (f"MMRE_pct_{col}_published", pub), (f"MMRE_match_{col}", abs(mm - pub) < 0.5)]
    # 2) Gerçekleşen/tahmin oranı (aşım oranı)
    rng = np.random.default_rng(SEED)
    for col in ["fpa_estimate_pm", "cocomo_estimate_pm"]:
        ratio = d.actual_effort_pm / d[col]
        boots = [100 * mre(d[col].values[i], d.actual_effort_pm.values[i]).mean()
                 for i in (rng.integers(0, len(d), len(d)) for _ in range(5000))]
        rows += [(f"overrun_share_actual>estimate_{col}", int((ratio > 1).sum())),
                 (f"ratio_median_{col}", round(float(ratio.median()), 3)),
                 (f"ratio_max_{col}", round(float(ratio.max()), 3)),
                 (f"MMRE_bootstrap95_lo_{col}", round(float(np.quantile(boots, .025)), 1)),
                 (f"MMRE_bootstrap95_hi_{col}", round(float(np.quantile(boots, .975)), 1)),
                 (f"share_ratio>=2.2_{col}", float((ratio >= 2.2).mean()))]
    # 3) K1 kuralı: iki bağımsız tahmin arasındaki fark > %25 ise plan onaylanmaz
    lo = d[["fpa_estimate_pm", "cocomo_estimate_pm"]].min(axis=1)
    hi = d[["fpa_estimate_pm", "cocomo_estimate_pm"]].max(axis=1)
    div = hi / lo - 1
    d["divergence"] = div; d["K1_flag"] = div > 0.25
    d["MRE_fpa"] = mre(d.fpa_estimate_pm, d.actual_effort_pm)
    # Daha az sapmalı tahmin olarak "iki tahminin geometrik ortalaması" (üçgenleme) da değerlendirilir
    d["geo_mean_est"] = np.sqrt(d.fpa_estimate_pm * d.cocomo_estimate_pm)
    d["MRE_geo"] = mre(d.geo_mean_est, d.actual_effort_pm)
    rows += [("K1_flagged_projects", int(d.K1_flag.sum())), ("n_projects", len(d)),
             ("divergence_median", round(float(div.median()), 3))]
    rho, p = stats.spearmanr(div, d.MRE_fpa)
    rows += [("spearman_divergence_vs_MRE_fpa", round(float(rho), 3)), ("spearman_p", round(float(p), 4))]
    rows += [("MMRE_pct_geometric_mean_estimate", round(100 * float(d.MRE_geo.mean()), 2))]
    # K1 eşiği duyarlılığı
    for thr in (0.25, 0.5, 1.0, 2.0):
        fl = div > thr
        rows.append((f"K1_flagged_at_threshold_{int(thr*100)}pct", int(fl.sum())))
        if 0 < fl.sum() < len(d):
            rows.append((f"MMRE_fpa_flagged_{int(thr*100)}pct", round(100 * float(d.MRE_fpa[fl].mean()), 1)))
            rows.append((f"MMRE_fpa_unflagged_{int(thr*100)}pct", round(100 * float(d.MRE_fpa[~fl].mean()), 1)))
    # 4) Dayanıklılık: türetilmiş FPA satırları (proje 7, 10) dışarıda bırakıldığında
    c = d[d.fpa_estimate_derived == 0]
    rows += [("n_projects_excluding_derived", len(c)),
             ("MMRE_pct_fpa_excluding_derived", round(100 * float(c.MRE_fpa.mean()), 2)),
             ("K1_flagged_excluding_derived_25pct", int((c.divergence > 0.25).sum())),
             ("overrun_share_actual>estimate_fpa_excluding_derived", int((c.actual_effort_pm > c.fpa_estimate_pm).sum()))]
    rho2, p2 = stats.spearmanr(c.divergence, c.MRE_fpa)
    rows += [("spearman_divergence_vs_MRE_fpa_excluding_derived", round(float(rho2), 3)), ("spearman_p_excluding_derived", round(float(p2), 4))]
    pd.DataFrame(rows, columns=["metric", "value"]).to_csv(out, index=False)
    d.to_csv(out.replace(".csv", "_projects.csv"), index=False)
    return pd.DataFrame(rows, columns=["metric", "value"])

if __name__ == "__main__":
    print(run("data/kemerer_1987.csv", "results/exp2_kemerer.csv").to_string(index=False))
