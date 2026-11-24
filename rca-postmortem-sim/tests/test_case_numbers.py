"""Makaledeki temel sayıların kodla tutarlılığını denetler.  Çalıştırma: python tests/test_case_numbers.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pandas as pd
from exp1_evm_pert import evm, pert
r = evm(2_400_000, 1_600_000, 900_000, 2_100_000, 18)
assert abs(r["CPI"] - 0.4286) < 1e-3 and abs(r["SPI"] - 0.5625) < 1e-4
assert abs(r["EAC"] - 5_600_000) < 1 and abs(r["overrun_pct"] - 133.33) < 0.01
assert abs(r["TCPI"] - 5.0) < 1e-9 and abs(r["forecast_months"] - 32) < 1e-9
e, s, z, p = pert(3, 5, 12, 11)
assert abs(e - 5.8333) < 1e-3 and abs(s - 1.5) < 1e-12 and abs(z - 3.4444) < 1e-3
d = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "data", "kemerer_1987.csv"))
mm = lambda c: 100 * ((d[c] - d.actual_effort_pm).abs() / d.actual_effort_pm).mean()
assert abs(mm("cocomo_estimate_pm") - 583.82) < 0.01 and abs(mm("fpa_estimate_pm") - 102.74) < 0.01
print("Tüm denetimler geçti.")
