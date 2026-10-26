"""P1 step 3: our parsed numbers for 3 filings, to compare with the filings by hand."""
from pathlib import Path

import pandas as pd

from p1_common import load_current
from lookthrough.load import load_num, load_sub
from lookthrough.paths import load_params, release_dir
from lookthrough.reconcile import filed_totals

rdir = release_dir(load_params())
cur, hold, extra, fields = load_current()
sub = load_sub(rdir)
filed = filed_totals(load_num(rdir, tags=["InvestmentOwnedAtFairValue"]), sub)

own = hold["subsidiary"].isna() & hold["range"].isna()
summ = (hold.assign(own_fv=hold["fair_value"].where(own),
                    jv_fv=hold["fair_value"].where(hold["subsidiary"].notna()))
        .groupby(["adsh", "name"], as_index=False)
        .agg(holdings=("identifier", "size"), own_holdings=("own_fv", "count"),
             own_fv=("own_fv", "sum"), jv_fv=("jv_fv", "sum"))
        .merge(filed, on="adsh", how="left"))
summ["gap_pct"] = (summ["own_fv"] - summ["filed_fv"]) / summ["filed_fv"]
summ.to_csv(Path("reports/p1_filing_summary.csv"), index=False)

small = summ[(summ.own_holdings.between(15, 60)) & summ.gap_pct.abs().lt(0.01)]
CHOSEN = ["0001193125-26-021227", "0001414932-26-000005"] + small["adsh"].head(1).tolist()

for a in CHOSEN:
    s = summ[summ.adsh == a].iloc[0]
    url = cur.loc[cur.adsh == a, "inlineurl"].dropna().iloc[0]
    print(f"\n{'=' * 90}\n{s['name']}  {a}\n{url}")
    print(f"holdings: {s.holdings}  own (non-JV, non-range): {s.own_holdings}")
    print(f"own fair value: ${s.own_fv:,.0f}   JV rows: ${s.jv_fv:,.0f}   "
          f"filed total (NUM): ${s.filed_fv:,.0f}   gap: {s.gap_pct:+.2%}")
    top = hold[(hold.adsh == a) & own].nlargest(5, "fair_value")
    print(top[["identifier", "principal", "cost", "fair_value", "source_rows"]]
          .to_string(index=False, max_colwidth=70))
print("\nSaved reports/p1_filing_summary.csv")
