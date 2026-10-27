"""P3 step 4: SOI vs the BDC's own NUM facts, and issuer-subtotal rows."""
import sys

import pandas as pd

sys.path.insert(0, "src")
from lookthrough.load import load_num
from lookthrough.mapping import parse_segments
from lookthrough.paths import load_params, release_dir

rdir = release_dir(load_params())
B = pd.read_pickle("outputs/p3_work/baseline.pkl")
rec, kept = B["rec"], B["kept"]
TOL = 0.01
ex = rec[~rec["admitted"] & rec["filed_fv"].notna() & rec["n_holdings"].gt(0)].copy()
ex["gap"] = ex["holdings_fv"] - ex["filed_fv"]

# 1. The BDC's own identifier-level fair value facts in NUM
num = load_num(rdir, tags=["InvestmentOwnedAtFairValue"], adsh=list(ex["adsh"]))
num = num.merge(ex[["adsh", "period"]], on="adsh")
num = num[num["ddate"] == num["period"]]
num["identifier"] = num["segments"].map(lambda s: parse_segments(s).get("InvestmentIdentifierAxis"))
n1 = num[num["identifier"].notna() & (num["dimn"] == "1")]
num_sum = n1.groupby("adsh")["value"].sum()
pair = kept.merge(n1.groupby(["adsh", "identifier"], as_index=False)["value"].first(),
                  on=["adsh", "identifier"])
pair = pair[pair["value"].abs() > 0]
soi_over_num = (pair["fair_value"] / pair["value"]).groupby(pair["adsh"]).median()


# 2. Issuer subtotals: a holding equal to the sum of holdings whose names extend it
def subtotals(k):
    items = sorted(zip(k["identifier"], k["fair_value"]))
    total, n = 0.0, 0
    for i, (name, fv) in enumerate(items):
        j, s, c = i + 1, 0.0, 0
        while j < len(items) and items[j][0].startswith(name) and len(items[j][0]) > len(name):
            s, c, j = s + items[j][1], c + 1, j + 1
        if c >= 2 and fv and abs(fv - s) <= 0.005 * abs(fv):
            total, n = total + fv, n + 1
    return total, n


rows = []
for r in ex.itertuples():
    k = kept[(kept["adsh"] == r.adsh) & kept["fair_value"].notna() & kept["identifier"].notna()]
    st, sn = subtotals(k)
    ns = num_sum.get(r.adsh, float("nan"))
    rows.append({"adsh": r.adsh, "name": r.name, "gap_pct": r.gap_pct, "gap_m": r.gap / 1e6,
                 "ratio": r.holdings_fv / r.filed_fv,
                 "num_sum_vs_filed": ns / r.filed_fv - 1,
                 "num_sum_vs_holdings": ns / r.holdings_fv - 1,
                 "soi_over_num_median": soi_over_num.get(r.adsh, float("nan")),
                 "subtotal_m": st / 1e6, "n_subtotals": sn,
                 "subtotal_closes": abs(r.gap - st) <= TOL * r.filed_fv})

ev = pd.DataFrame(rows).sort_values("gap_m", key=abs, ascending=False)
ev.to_csv("reports/p3_gap_evidence3.csv", index=False)
pd.set_option("display.width", 250)
print(f"subtotals close the gap:            {int(ev.subtotal_closes.sum())} of {len(ev)}")
print(f"NUM holdings sum within 1% of filed: {int(ev.num_sum_vs_filed.abs().le(TOL).sum())}")
print(f"NUM holdings sum within 1% of ours:  {int(ev.num_sum_vs_holdings.abs().le(TOL).sum())}")
print(f"SOI value != NUM value (median):     {int((ev.soi_over_num_median.sub(1).abs() > 0.001).sum())}")
cols = ["name", "gap_pct", "ratio", "num_sum_vs_filed", "num_sum_vs_holdings",
        "soi_over_num_median", "subtotal_m", "n_subtotals", "subtotal_closes"]
print("\n=== 30 largest gaps ===")
print(ev.head(30)[cols].round(3).to_string(index=False, max_colwidth=32))
print("\n=== Extreme ratios ===")
print(ev[ev.ratio > 2][cols].round(3).to_string(index=False, max_colwidth=32))