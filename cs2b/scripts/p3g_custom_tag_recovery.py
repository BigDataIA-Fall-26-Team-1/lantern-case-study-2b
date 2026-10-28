"""P3 stretch: measure recovering missing SOI fair values from NUM (standard, then custom tags)."""
import sys

import pandas as pd

sys.path.insert(0, "src")
from lookthrough.load import load_num
from lookthrough.mapping import parse_segments
from lookthrough.paths import load_params, release_dir

P = load_params()
rdir = release_dir(P)
TOL = float(P["reconcile"]["tolerance"])
B = pd.read_pickle("outputs/p3_work/baseline.pkl")
rec, kept = B["rec"], B["kept"]

miss = kept[kept["fair_value"].isna() & kept["identifier"].notna()]
print(f"SOI holdings with no fair value: {len(miss):,} in {miss['adsh'].nunique()} filings")

num = load_num(rdir, tags=["InvestmentOwnedAtFairValue"],
               adsh=list(miss["adsh"].unique()), custom_fv=True)
num = num[num["dimn"] == "1"].copy()
num["identifier"] = num["segments"].map(lambda s: parse_segments(s).get("InvestmentIdentifierAxis"))
num = num[num["identifier"].notna() & num["value"].notna()]
num["kind"] = (num["version"] == num["adsh"]).map({True: "custom", False: "standard"})
JUNK = (r"Commitment|FinancialSupport|MoneyMarket|CashEquivalent|GainLoss|Realized|"
        r"Transfers|Amortization|Reconciliation")
bad = (num["kind"] == "custom") & num["tag"].str.contains(JUNK)
print(f"custom facts excluded as not a holding's fair value: {bad.sum():,} "
      f"({num.loc[bad, 'tag'].nunique()} tags)")
num = num[~bad]
num = num.sort_values("kind", ascending=False)          # standard first
facts = num.groupby(["adsh", "identifier", "ddate"], as_index=False).agg(
    value=("value", "first"), tag=("tag", "first"), kind=("kind", "first"),
    n_values=("value", "nunique"))

m = miss.merge(facts, on=["adsh", "identifier", "ddate"], how="left")
print(f"recovered from NUM: {m['value'].notna().sum():,} "
      f"(standard tag {(m['kind'] == 'standard').sum():,}, custom tag {(m['kind'] == 'custom').sum():,}); "
      f"ambiguous (several values): {(m['n_values'] > 1).sum()}")
print("custom tags used:", sorted(m.loc[m["kind"] == "custom", "tag"].dropna().unique()))

r = rec.copy()
r["recovered"] = r["adsh"].map(m.groupby("adsh")["value"].sum()).fillna(0.0)
r["new_fv"] = r["holdings_fv"].fillna(0.0) + r["recovered"]
r["new_gap"] = (r["new_fv"] - r["filed_fv"]) / r["filed_fv"]
r["new_admit"] = r["new_gap"].abs().le(TOL) & r["filed_fv"].notna() & r["n_holdings"].gt(0)

gained = r[~r["admitted"] & r["new_admit"]]
lost = r[r["admitted"] & ~r["new_admit"]]
new_adm = r[r["new_admit"]]
print(f"\nfilings gained: {len(gained)}   lost: {len(lost)}")
print(f"coverage: {r['admitted'].sum()} -> {r['new_admit'].sum()} of {len(r)} filings; "
      f"dollars {r.loc[r['admitted'], 'filed_fv'].sum() / r['filed_fv'].sum():.1%} -> "
      f"{new_adm['filed_fv'].sum() / r['filed_fv'].sum():.1%}")
cols = ["adsh", "name", "gap_pct", "new_gap", "recovered", "filed_fv"]
show = lambda d: d[cols].assign(recovered=d.recovered / 1e6, filed_fv=d.filed_fv / 1e6).round(4)
print("\n=== gained ===")
print(show(gained).to_string(index=False, max_colwidth=35))
print("\n=== lost (must be none) ===")
print(show(lost).to_string(index=False, max_colwidth=35))
print("\n=== other filings that recover value but stay excluded (top 10) ===")
print(show(r[~r["new_admit"] & r["recovered"].gt(0)].nlargest(10, "recovered"))
      .to_string(index=False, max_colwidth=35))