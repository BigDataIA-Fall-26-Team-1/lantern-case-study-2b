"""P3 step 3: extra axes and alternative totals for the excluded filings."""
import sys

import pandas as pd

sys.path.insert(0, "src")
from lookthrough.load import READ, load_soi, norm_date, soi_header
from lookthrough.mapping import AXES
from lookthrough.paths import load_params, release_dir

rdir = release_dir(load_params())
B = pd.read_pickle("outputs/p3_work/baseline.pkl")
rec, kept = B["rec"], B["kept"]
TOL = float(load_params()["reconcile"]["tolerance"])   # P5: the admission tolerance from params.yaml
ex = rec[~rec["admitted"] & rec["filed_fv"].notna() & rec["n_holdings"].gt(0)].copy()
ex["gap"] = ex["holdings_fv"] - ex["filed_fv"]
ids = set(ex["adsh"])

# 1. Undimensioned USD facts at the period end, any tag
keep = []
for ch in pd.read_csv(rdir / "datasets" / "num.tsv", chunksize=500_000, **READ):
    keep.append(ch[ch["adsh"].isin(ids) & (ch["dimn"] == "0") & (ch["uom"] == "USD")])
num = pd.concat(keep)
num["ddate"] = norm_date(num["ddate"])
num["value"] = pd.to_numeric(num["value"], errors="coerce")
num = num.merge(ex[["adsh", "period", "holdings_fv"]], on="adsh")
num = num[num["ddate"] == num["period"]]
alt, fvvals = {}, {}
for a, n in num.groupby("adsh"):
    hv = n["holdings_fv"].iloc[0]
    m = n[((n["value"] - hv).abs() <= TOL * abs(hv)) & (n["tag"] != "InvestmentOwnedAtFairValue")]
    alt[a] = "; ".join(sorted(set(m["tag"] + m["version"].eq(a).map({True: "*", False: ""}))))
    fvvals[a] = sorted(set(n.loc[n["tag"] == "InvestmentOwnedAtFairValue", "value"].dropna()))

# 2. Extra SOI axes attached to each kept holding through its source rows
header = soi_header(rdir)
extra = [c for c in header if c.endswith("Axis") and c not in AXES.values()]
sx = load_soi(rdir, usecols=["adsh"] + extra)
sx = sx[sx["adsh"].isin(ids)].set_index("soi_row")
k = kept[kept["adsh"].isin(ids)][["adsh", "fair_value", "source_rows"]].copy()
k["hid"] = k.index
e = k.assign(row=k["source_rows"].astype(str).str.split(";")).explode("row")
e["row"] = pd.to_numeric(e["row"], errors="coerce")
e = e.join(sx[extra], on="row")
k = k.join(e.groupby("hid")[extra].first(), on="hid")

rows = []
for r in ex.itertuples():
    h = k[k["adsh"] == r.adsh]
    found = []
    for c in extra:
        has = h[c].notna()
        if not has.any():
            continue
        if abs(r.gap - h.loc[has, "fair_value"].sum()) <= TOL * r.filed_fv:
            found.append(f"{c} [all, {int(has.sum())}]")
        for mem, s in h[has].groupby(c)["fair_value"].sum().items():
            if abs(r.gap - s) <= TOL * r.filed_fv:
                found.append(f"{c} = {mem} [{int((h[c] == mem).sum())}]")
    present = {c.replace(" Axis", ""): int(h[c].notna().sum()) for c in extra if h[c].notna().any()}
    rows.append({"adsh": r.adsh, "name": r.name, "gap_pct": r.gap_pct, "gap_m": r.gap / 1e6,
                 "ratio": r.holdings_fv / r.filed_fv, "axis_closes": "; ".join(found),
                 "alt_total_tags": alt.get(r.adsh, ""),
                 "undim_fv_m": ", ".join(f"{v / 1e6:,.1f}" for v in fvvals.get(r.adsh, [])[:5]),
                 "axes_present": str(present)})

ev = pd.DataFrame(rows).sort_values("gap_m", key=abs, ascending=False)
ev.to_csv("reports/p3_gap_evidence2.csv", index=False, lineterminator="\n")   # P5: LF on every OS
print(f"axis closes the gap:          {int((ev.axis_closes != '').sum())} of {len(ev)}")
print(f"another tag equals holdings:  {int((ev.alt_total_tags != '').sum())} of {len(ev)}")
print(f"several undimensioned FV facts: {int(ev.undim_fv_m.str.contains(',').sum())}")
pd.set_option("display.width", 250)
print("\n=== 25 largest gaps: axes ===")
print(ev.head(25)[["name", "gap_pct", "ratio", "axis_closes"]]
      .round(2).to_string(index=False, max_colwidth=70))
print("\n=== 25 largest gaps: totals ===")
print(ev.head(25)[["name", "alt_total_tags", "undim_fv_m"]]
      .to_string(index=False, max_colwidth=60))
print("\n=== Extreme ratios (above 2x) ===")
print(ev[ev.ratio > 2][["name", "ratio", "alt_total_tags", "undim_fv_m"]]
      .round(1).to_string(index=False, max_colwidth=60))