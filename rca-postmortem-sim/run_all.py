"""Tüm deneyleri sırayla çalıştırır ve results/ klasörüne yazar.  Kullanım: python run_all.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
os.makedirs("results", exist_ok=True)
import exp1_evm_pert, exp2_kemerer, exp3_knoi, exp4_rca_sim

print("== Deney 1: EVM/PERT =="); print(exp1_evm_pert.run("results/exp1_evm_pert.csv").to_string(index=False))
print("\n== Deney 2: Kemerer (1987) =="); print(exp2_kemerer.run("data/kemerer_1987.csv", "results/exp2_kemerer.csv").to_string(index=False))
print("\n== Deney 3: KNÖİ Monte Carlo =="); a, b = exp3_knoi.run("results/exp3_knoi.csv"); print(a.to_string(index=False))
print("\n== Deney 4: Ishikawa / 5 Neden / Hibrit =="); print(exp4_rca_sim.run("results/exp4_rca_sim.csv").round(3).to_string(index=False))
exp4_rca_sim.sweep("results/exp4_rca_sweep.csv")
print("\nTamamlandı. Çıktılar: results/")
