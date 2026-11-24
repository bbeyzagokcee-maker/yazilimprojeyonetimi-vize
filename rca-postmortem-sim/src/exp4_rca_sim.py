"""Deney 4: Ishikawa, 5 Neden ve hibrit yaklaşımın sentetik nedensel graflar üzerinde karşılaştırması.

Model varsayımları (bilinçli olarak basit ve parametrik tutulmuştur; sonuçlar bu varsayımlara koşulludur):
  * Nedensel yapı: kökte "sorun", altında 6 kategori (gereksinim, yönetim, süreç, insan, teknoloji, paydaş) ve
    Galton-Watson tipi bir ağaç. Yapraklar (derinlik >= 3) gerçek kök nedenlerdir; en yüksek ağırlıklı 3 yaprak "kritik"tir.
  * Her düğümün görünürlüğü (salience) U(0,1)'dir.
  * Ishikawa: düğüm d. düzeydeyse listelenme olasılığı p0 * decay^(d-1) (görünürlükle ağırlıklı). Nedenler arası sıra bilinmez.
  * 5 Neden: analist başlangıç dalını ve her adımda alt nedeni görünürlük^gamma ile orantılı seçer (en görünür olana eğilim).
  * Hibrit: Ishikawa listesindeki dallar, analistin gürültülü alt-ağaç önem tahminine (lognormal gürültü) göre sıralanır;
    5 Neden zincirleri en önemli k dalda başlatılır.
Çıktılar: kritik kök neden geri çağırma oranı (recall), ortalama ulaşılan derinlik, kategori kapsamı, maliyet birimi.
"""
import numpy as np, pandas as pd

SEED = 42
CATS = 6

class Node:
    __slots__ = ("depth", "cat", "sal", "children", "weight", "parent", "id")
    def __init__(self, depth, cat, parent, id_):
        self.depth, self.cat, self.parent, self.id = depth, cat, parent, id_
        self.children, self.weight = [], 0.0
        self.sal = 0.0

def build_tree(rng, mean_offspring=1.5, max_depth=5):
    nodes, root = [], Node(0, -1, None, 0)
    nodes.append(root)
    frontier = []
    for c in range(CATS):                       # her kategoride 1-3 birinci düzey neden
        for _ in range(rng.integers(1, 4)):
            n = Node(1, c, root, len(nodes)); nodes.append(n); root.children.append(n); frontier.append(n)
    while frontier:
        nxt = []
        for n in frontier:
            if n.depth >= max_depth: continue
            k = rng.poisson(mean_offspring if n.depth < 3 else mean_offspring * 0.7)
            for _ in range(k):
                ch = Node(n.depth + 1, n.cat, n, len(nodes)); nodes.append(ch); n.children.append(ch); nxt.append(ch)
        frontier = nxt
    for n in nodes: n.sal = rng.random()
    leaves = [n for n in nodes if not n.children and n.depth >= 3]
    if len(leaves) < 3: return None
    w = rng.pareto(1.5, len(leaves)) + 1
    for n, wi in zip(leaves, w): n.weight = wi
    order = np.argsort(-w)
    critical = {leaves[i].id for i in order[:3]}
    return nodes, root, leaves, critical

def subtree_importance(n):
    if not n.children: return n.weight
    return sum(subtree_importance(c) for c in n.children)

def five_whys(start, rng, gamma, max_steps=5):
    cur, path, steps = start, [start], 0
    while cur.children and steps < max_steps:
        p = np.array([c.sal for c in cur.children]) ** gamma + 1e-9
        cur = cur.children[rng.choice(len(cur.children), p=p / p.sum())]
        path.append(cur); steps += 1
    return path, steps

def pick_start_pure(root, used, rng, gamma):
    cand = [c for c in root.children if c.id not in used]
    if not cand: return None
    p = np.array([c.sal for c in cand]) ** gamma + 1e-9
    return cand[rng.choice(len(cand), p=p / p.sum())]

def one_trial(rng, k, p0, decay, gamma, noise):
    t = None
    while t is None: t = build_tree(rng)
    nodes, root, leaves, critical = t
    # Ishikawa
    listed = [n for n in nodes[1:] if rng.random() < min(1, p0 * decay ** (n.depth - 1) * (0.5 + 0.5 * n.sal) * 2 / 1.5)]
    listed_ids = {n.id for n in listed}
    ish = {"recall": len(critical & listed_ids) / 3, "depth": np.mean([n.depth for n in listed]) if listed else 0,
           "cat": len({n.cat for n in listed}) / CATS, "cost": len(listed)}
    # 5 Neden (k zincir)
    used, reached, depths, cats, cost = set(), set(), [], set(), 0
    for _ in range(k):
        s = pick_start_pure(root, used, rng, gamma)
        if s is None: break
        used.add(s.id); path, steps = five_whys(s, rng, gamma)
        reached |= {n.id for n in path}; depths.append(path[-1].depth); cats |= {n.cat for n in path}; cost += steps + 1
    fw = {"recall": len(critical & reached) / 3, "depth": np.mean(depths) if depths else 0, "cat": len(cats) / CATS, "cost": cost}
    # Hibrit: Ishikawa listesinden önem tahminine göre en iyi k dal, sonra 5 Neden
    firsts = {}
    for n in listed:
        a = n
        while a.depth > 1: a = a.parent
        firsts[a.id] = a
    ranked = sorted(firsts.values(), key=lambda a: subtree_importance(a) * rng.lognormal(0, noise), reverse=True)[:k]
    reached_h, depths_h, cats_h, cost_h = set(listed_ids), [], {n.cat for n in listed}, len(listed)
    for s in ranked:
        path, steps = five_whys(s, rng, gamma)
        reached_h |= {n.id for n in path}; depths_h.append(path[-1].depth); cats_h |= {n.cat for n in path}; cost_h += steps + 1
    hy = {"recall": len(critical & reached_h) / 3, "depth": np.mean(depths_h) if depths_h else 0, "cat": len(cats_h) / CATS, "cost": cost_h}
    return ish, fw, hy

def run(out, N=5000, k=2, p0=0.9, decay=0.5, gamma=2.0, noise=1.0, seed=SEED):
    rng = np.random.default_rng(seed)
    acc = {"Ishikawa": [], "5 Neden": [], "Hibrit": []}
    for _ in range(N):
        i, f, h = one_trial(rng, k, p0, decay, gamma, noise)
        acc["Ishikawa"].append(i); acc["5 Neden"].append(f); acc["Hibrit"].append(h)
    rows = []
    for m, lst in acc.items():
        df = pd.DataFrame(lst)
        rows.append({"method": m, "k": k, "p0": p0, "decay": decay, "gamma": gamma, "noise": noise, "N": N,
                     "recall_mean": df.recall.mean(), "recall_ci95": 1.96 * df.recall.std() / np.sqrt(N),
                     "recall_all3_share": (df.recall > 0.99).mean(), "depth_mean": df.depth.mean(),
                     "category_coverage": df.cat.mean(), "cost_mean": df.cost.mean(),
                     "recall_per_cost": df.recall.mean() / df.cost.mean()})
    res = pd.DataFrame(rows); res.to_csv(out, index=False); return res

def sweep(out, N=3000):
    frames = []
    for k in (1, 2, 3, 4, 6):
        frames.append(run("/dev/null", N, k=k, seed=SEED + k).assign(sweep="k"))
    for g in (0.0, 1.0, 2.0, 4.0):
        frames.append(run("/dev/null", N, gamma=g, seed=SEED + 100 + int(g * 10)).assign(sweep="gamma"))
    for nz in (0.0, 0.5, 1.0, 2.0):
        frames.append(run("/dev/null", N, noise=nz, seed=SEED + 200 + int(nz * 10)).assign(sweep="noise"))
    for p0 in (0.6, 0.9):
        frames.append(run("/dev/null", N, p0=p0, seed=SEED + 300 + int(p0 * 10)).assign(sweep="p0"))
    df = pd.concat(frames); df.to_csv(out, index=False); return df

if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(run("results/exp4_rca_sim.csv").round(3).to_string(index=False))
    s = sweep("results/exp4_rca_sweep.csv")
    print(s[["sweep", "method", "k", "gamma", "noise", "p0", "recall_mean", "depth_mean", "category_coverage", "cost_mean"]].round(3).to_string(index=False))
