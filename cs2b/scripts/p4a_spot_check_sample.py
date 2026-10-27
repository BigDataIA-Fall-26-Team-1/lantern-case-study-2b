"""P4a: draw the Part 4 spot-check sample from the panel and write a lookup sheet.

Same sampling as notebook 07 (the 5 largest filings by fair value, plus 5 more at random,
random_state=7; from each, the largest holding and one more at random). Adds what you need to find
each holding in the filing: the plain document URL (no Inline XBRL viewer) and the values in
thousands, as the schedules print them.
Run from cs2b/:  python scripts/p4a_sample.py   ->  reports/spot_check.csv (filing_* columns to fill in)
"""
import sys
from pathlib import Path

sys.path.insert(0, "src")
import pandas as pd
from lookthrough import load, paths, tables

ROOT = Path(".")
P = paths.load_params(ROOT)
panel = tables.load_table(ROOT / P["outputs"]["panel"] / "holdings")

# notebook 07's sampling, unchanged
size = panel.groupby("adsh")["fair_value"].sum().sort_values(ascending=False)
others = size.index[5:].to_series()
chosen = list(size.index[:5]) + list(others.sample(min(5, len(others)), random_state=7))
picks = []
for a in chosen:
    g = panel[panel["adsh"] == a].sort_values("fair_value", ascending=False)
    picks.append(g.head(1))
    if len(g) > 1:
        picks.append(g.iloc[1:].sample(1, random_state=7))
sample = pd.concat(picks).reset_index(drop=True)

sub = load.load_sub(paths.release_dir(P, ROOT)).set_index("adsh")
k = lambda s: (pd.to_numeric(s, errors="coerce") / 1000).round(0)
sample = sample.assign(
    check=[f"S{i + 1:02d}" for i in range(len(sample))],
    form=sample["adsh"].map(sub["form"]),
    filing_url=sample["adsh"].map(sub["inlineurl"]).str.replace("https://www.sec.gov/ix?doc=", "https://www.sec.gov", regex=False),
    fv_000s=k(sample["fair_value"]), principal_000s=k(sample["principal"]), cost_000s=k(sample["cost"]),
    filing_fair_value="", filing_principal="", matches="", note="")
cols = ["check", "adsh", "name", "form", "period", "identifier", "fair_value", "principal", "cost",
        "fv_000s", "principal_000s", "cost_000s", "maturity", "interest_rate", "source_rows", "filing_url",
        "filing_fair_value", "filing_principal", "matches", "note"]
out = ROOT / P["outputs"]["reports"] / "spot_check.csv"
sample[[c for c in cols if c in sample]].to_csv(out, index=False)

pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 95)
print(f"{len(sample)} holdings across {sample['adsh'].nunique()} filings -> {out}")
for a, g in sample.groupby("adsh", sort=False):
    print(f"\n{g['name'].iloc[0]} | {a} | {g['form'].iloc[0]} {g['period'].iloc[0]}\n  {g['filing_url'].iloc[0]}")
    for r in g.itertuples():
        print(f"  {r.check}  search {r.fv_000s:>12,.0f}  (principal {r.principal_000s:,.0f}, cost {r.cost_000s:,.0f})  {r.identifier[:90]}")
