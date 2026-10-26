"""P1 step 2b: JV rows, and the conflicts that remain once they are set aside."""
import pandas as pd

from p1_common import SUBAX, load_current
from lookthrough.holdings import KEY

cur, hold, extra, fields = load_current()

# 1. JV (nonconsolidated subsidiary) rows in the current period
jv = cur[cur[SUBAX].notna()]
print(f"=== JV rows: {len(jv):,} current rows in {jv['adsh'].nunique()} filings, "
      f"fair value ${jv['fair_value'].sum() / 1e6:,.1f}m ===")
by = jv.groupby(["adsh", "name"]).agg(rows=("fair_value", "size"),
                                      fv_m=("fair_value", lambda s: s.sum() / 1e6),
                                      jvs=(SUBAX, "nunique"))
print(by.sort_values("rows", ascending=False).head(10).round(1).to_string())
rng = cur[cur["Range Axis"].notna()] if "Range Axis" in cur else cur.iloc[0:0]
print(f"\nRange Axis rows (valuation inputs?): {len(rng):,} in {rng['adsh'].nunique()} filings")

# 2. Conflicts once JV and Range rows are set aside
base = cur[cur["identifier"].notna() & cur[SUBAX].isna()]
if "Range Axis" in base:
    base = base[base["Range Axis"].isna()]
conf = base.groupby(KEY, dropna=False)[fields].nunique().gt(1)
print("\n=== Conflicts remaining, by field ===")
print(conf.sum()[lambda s: s > 0].sort_values(ascending=False).to_string())

# 3. For each remaining field: where, and two examples with what differs
show = ["adsh", "source_soi_row", "identifier", "fair_value", "principal",
        "interest_rate", "spread", "pik_rate"]
for f in conf.columns[conf.sum() > 0]:
    keys = conf.index[conf[f]]
    rows = base.set_index(KEY).loc[keys].reset_index()
    print(f"\n##### {f}: {len(keys)} holdings #####")
    print(rows.groupby(["adsh", "name"])[KEY].apply(lambda d: d.drop_duplicates().shape[0])
          .nlargest(5).to_string())
    for k in list(keys[:2]):
        ex = rows[(rows[KEY] == pd.Series(k, index=KEY)).all(axis=1)]
        ax = [c for c in extra if ex[c].nunique(dropna=False) > 1]
        print(ex[[c for c in show if c in ex] + ax].to_string(index=False))