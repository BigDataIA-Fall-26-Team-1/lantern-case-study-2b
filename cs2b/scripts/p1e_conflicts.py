"""P1 step 2: coalesce current-period rows into holdings and diagnose conflicts."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "src")
from lookthrough.holdings import KEY, TEXT, coalesce_holdings, split_periods
from lookthrough.load import load_soi, load_sub, load_tag, norm_date, soi_header
from lookthrough.mapping import AXES, CANONICAL, map_soi_columns, soi_usecols, to_canonical
from lookthrough.paths import load_params, release_dir

OUT = Path("reports")
rdir = release_dir(load_params())
print("release dir:", rdir)

# 1. Load with the kit, keeping provenance and the extra (unmapped) axes
sub, tag, header = load_sub(rdir), load_tag(rdir), soi_header(rdir)
colmap = map_soi_columns(header, tag)
EXTRA_AXES = [c for c in header if c.endswith("Axis") and c not in AXES.values()]
PROV = [c for c in ("source_release", "source_soi_row") if c in header]
soi = load_soi(rdir, usecols=soi_usecols(header, colmap) + PROV + EXTRA_AXES)
if "soi_row" not in soi:
    soi["soi_row"] = soi.index
canon = to_canonical(soi, colmap)
for c in PROV + EXTRA_AXES:
    canon[c] = soi[c]
canon["ddate"], canon["period"] = norm_date(canon["ddate"]), norm_date(canon["period"])
canon = canon[canon["adsh"].isin(sub["adsh"])]

# 2. Current period only, then coalesce
h = split_periods(canon, sub)
cur = h[h["is_current"]]
hold = coalesce_holdings(cur)
print(f"\nSOI rows (latest filings): {len(canon):,}   current: {len(cur):,}   "
      f"comparative: {(~h['is_current']).sum():,}")
print(f"current rows without identifier: {cur['identifier'].isna().sum():,}")
print(f"holdings: {len(hold):,}   multi-row: {(hold['n_rows'] > 1).sum():,}   "
      f"with conflicts: {(hold['n_conflicts'] > 0).sum():,}   "
      f"filings: {hold['adsh'].nunique()}")

# 3. Which fields conflict
fields = [f for f in list(CANONICAL) + TEXT if f in cur]
ided = cur[cur["identifier"].notna()]
conf = ided.groupby(KEY, dropna=False)[fields].nunique().gt(1)
print("\n=== Holdings with conflicting values, by field ===")
print(conf.sum().sort_values(ascending=False).to_string())

# 4. Fair value conflicts: which other axes differ between the rows?
fv_keys = conf.index[conf["fair_value"]]
rows = ided.set_index(KEY).loc[fv_keys].reset_index()
varies = rows.groupby(KEY)[EXTRA_AXES + TEXT].nunique(dropna=False).gt(1)
spread = rows.groupby(KEY)["fair_value"].agg(lambda s: s.max() - s.min())
print(f"\n=== Fair value conflicts: {len(fv_keys):,} holdings, "
      f"${spread.sum() / 1e6:,.1f}m total max-min spread ===")
print("axes that differ between the conflicting rows (holdings count):")
print(varies.sum()[lambda s: s > 0].sort_values(ascending=False).to_string())
print(f"no axis differs (true duplicates or restated copies): {(~varies.any(axis=1)).sum():,}")

# 5. Where they are
fvc = hold.set_index(KEY).loc[fv_keys].reset_index()
print("\n=== Filings with most fair value conflicts ===")
print(fvc.groupby(["adsh", "name"]).size().nlargest(10).to_string())

# 6. Examples with evidence
show = ["adsh", "source_release", "source_soi_row", "identifier", "fair_value", "cost", "principal"]
for k in list(fv_keys[:3]):
    ex = rows[(rows[KEY] == pd.Series(k, index=KEY)).all(axis=1)]
    ax = [c for c in EXTRA_AXES + TEXT if ex[c].nunique(dropna=False) > 1]
    print("\n--- example ---")
    print(ex[[c for c in show if c in ex] + ax].to_string(index=False))

rows.to_csv(OUT / "p1_fv_conflict_rows.csv", index=False)
hold.drop(columns=[c for c in EXTRA_AXES if c in hold]).to_csv(
    OUT / "p1_holdings_current.csv", index=False)
print(f"\nSaved {OUT / 'p1_fv_conflict_rows.csv'} and {OUT / 'p1_holdings_current.csv'}")