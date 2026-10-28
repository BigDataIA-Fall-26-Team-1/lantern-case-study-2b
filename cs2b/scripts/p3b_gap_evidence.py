"""P3 step 2: for each excluded filing, which candidate cause would close its gap?"""
import sys

import pandas as pd

sys.path.insert(0, "src")
from lookthrough import clean, paths

B = pd.read_pickle("outputs/p3_work/baseline.pkl")
rec, kept, hold = B["rec"], B["kept"], B["holdings"]
cur = hold[hold["is_current"]]
TOL = float(paths.load_params()["reconcile"]["tolerance"])   # P5: the admission tolerance from params.yaml
ex = rec[~rec["admitted"] & rec["filed_fv"].notna() & rec["n_holdings"].gt(0)]

rows = []
for r in ex.itertuples():
    k = kept[kept["adsh"] == r.adsh]
    gap = r.holdings_fv - r.filed_fv

    def closes(x):
        """Would removing x dollars bring the gap within tolerance?"""
        return abs(gap - x) <= TOL * r.filed_fv

    v = k[k["fair_value"].fillna(0) != 0]
    dup_fv = v.loc[v.duplicated(["fair_value", "cost", "principal"]), "fair_value"].sum()
    neg_fv = k.loc[k["fair_value"] < 0, "fair_value"].sum()
    c = cur[cur["adsh"] == r.adsh]
    cash_mask, _ = clean.rule_cash(c)
    cash_fv = c.loc[cash_mask, "fair_value"].sum()
    big = k["fair_value"].max()

    prefix = ""
    words = (k["identifier"].fillna("").str.lower()
             .str.replace(r"[^a-z ]", " ", regex=True).str.split())
    for n in (1, 2, 3):
        pre = words.map(lambda t, n=n: " ".join(t[:n]))
        g = k.groupby(pre)["fair_value"].sum()
        g = g[(g - gap).abs() <= TOL * r.filed_fv]
        if len(g):
            p = g.index[0]
            prefix = f"'{p}' ({int((pre == p).sum())} holdings)"
            break

    rows.append({
        "adsh": r.adsh, "name": r.name, "form": r.form, "gap_pct": r.gap_pct,
        "gap_m": gap / 1e6, "missing_fv": r.missing_fv,
        "dup_m": dup_fv / 1e6, "dup_closes": closes(dup_fv),
        "neg_m": neg_fv / 1e6, "unfunded_closes": closes(neg_fv),
        "cash_m": cash_fv / 1e6, "cash_closes": closes(-cash_fv),
        "big_m": big / 1e6, "big_closes": closes(big),
        "prefix_closes": prefix,
    })

ev = pd.DataFrame(rows).sort_values("gap_m", key=abs, ascending=False)
ev.to_csv("reports/p3_gap_evidence.csv", index=False, lineterminator="\n")   # P5: LF on every OS

flags = ["dup_closes", "unfunded_closes", "cash_closes", "big_closes"]
print(f"=== {len(ev)} excluded filings with holdings and a filed total ===")
for f in flags:
    print(f"{f:16s} {int(ev[f].sum()):3d}")
print(f"{'prefix_closes':16s} {int((ev['prefix_closes'] != '').sum()):3d}")
none = ~ev[flags].any(axis=1) & (ev["prefix_closes"] == "")
print(f"{'nothing closes':16s} {int(none.sum()):3d}")

print("\n=== 25 largest gaps ===")
show = ["name", "gap_pct", "gap_m", "missing_fv", "dup_m", "neg_m", "cash_m",
        "big_m", "prefix_closes"] + flags
print(ev.head(25)[show].round(2).to_string(index=False, max_colwidth=28))
print("\nSaved reports/p3_gap_evidence.csv")