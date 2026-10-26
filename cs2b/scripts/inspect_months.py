"""P0: inspect the 3 monthly releases before merging them into 2026q1."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lookthrough import load  # noqa: E402

MONTHS = ["2026_01", "2026_02", "2026_03"]
RAW = ROOT / "data" / "raw"

subs, headers = [], {}
for m in MONTHS:
    d = RAW / f"{m}_bdc"
    s = pd.read_csv(d / "datasets" / "sub.tsv", **load.READ)   # all versions, no prevrpt filter
    s["source_release"] = m
    subs.append(s)
    headers[m] = load.soi_header(d)
    with open(d / "soi.tsv", encoding="utf-8") as fh:
        n_soi = sum(1 for _ in fh) - 1
    print(f"{m}: sub {len(s)} filings | forms {s['form'].value_counts().to_dict()} | "
          f"top periods {s['period'].value_counts().head(3).to_dict()} | prevrpt=1: {int((s['prevrpt'] == '1').sum())} | "
          f"soi {n_soi:,} rows, {len(headers[m])} columns")

sub = pd.concat(subs, ignore_index=True)
dup_adsh = sub[sub.duplicated("adsh", keep=False)]
print(f"\nadsh appearing in more than one month: {dup_adsh['adsh'].nunique()}")
print(dup_adsh[["adsh", "name", "form", "period", "source_release"]].head(10).to_string(index=False))

one = sub.drop_duplicates("adsh")
dup_cp = one[one.duplicated(["cik", "period"], keep=False)].sort_values(["cik", "period", "accepted"])
print(f"\ncik + period with more than one filing: {dup_cp.groupby(['cik', 'period']).ngroups}")
print(dup_cp[["adsh", "cik", "name", "form", "period", "accepted", "prevrpt", "source_release"]]
      .head(20).to_string(index=False))

allcols = set().union(*headers.values())
for m in MONTHS:
    print(f"\nSOI columns missing in {m} but present in another month: {sorted(allcols - set(headers[m]))}")