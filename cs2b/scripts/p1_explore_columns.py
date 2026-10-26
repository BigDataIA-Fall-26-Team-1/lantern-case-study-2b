"""P1 step 1: which SOI columns map to each canonical field, and what is left over."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "src")
from lookthrough.mapping import AXES, CANONICAL, META, map_soi_columns

RDIR = Path("data/raw/2026q1_bdc")
OUT = Path("reports/p1_soi_columns.csv")
READ = dict(sep="\t", dtype=str, keep_default_na=False, na_values=[""])

# 1. SOI header and TAG table
header = pd.read_csv(RDIR / "soi.tsv", nrows=0, **READ).columns.tolist()
tag = pd.read_csv(RDIR / "datasets" / "tag.tsv", **READ)
print(f"SOI columns: {len(header)}   TAG rows: {len(tag):,}")

# 2. How much each column is used (read in chunks to save memory)
nonnull = pd.Series(0, index=header)
filings = {c: set() for c in header}
for ch in pd.read_csv(RDIR / "soi.tsv", chunksize=50_000, **READ):
    nn = ch.notna()
    nonnull += nn.sum()
    for c in header:
        filings[c].update(ch.loc[nn[c], "adsh"].unique())

# 3. Which tag(s) carry each column's label
labels = {}
for r in tag.dropna(subset=["tlabel"]).itertuples():
    kind = "custom" if r.custom == "1" else "std"
    labels.setdefault(r.tlabel, set()).add(f"{r.tag} ({kind})")

# 4. The kit's own mapping
colmap = map_soi_columns(header, tag)
field_of = {c: f for f, cols in colmap.items() for c in cols}
axis_of = {col: f for f, col in AXES.items()}


def role(c):
    if c in field_of:
        return "canonical:" + field_of[c]
    if c in axis_of:
        return "axis:" + axis_of[c]
    if c in META:
        return "meta"
    if c.startswith("source_"):
        return "provenance"
    return "unmapped"


df = pd.DataFrame({
    "column": header,
    "role": [role(c) for c in header],
    "tags": ["; ".join(sorted(labels.get(c, []))) for c in header],
    "nonnull_rows": [int(nonnull[c]) for c in header],
    "n_filings": [len(filings[c]) for c in header],
}).sort_values(["role", "nonnull_rows"], ascending=[True, False])
OUT.parent.mkdir(exist_ok=True)
df.to_csv(OUT, index=False)

# 5. Summary
print("\n=== Canonical fields -> SOI columns ===")
for f in CANONICAL:
    cols = colmap.get(f, [])
    print(f"{f:15s} {cols if cols else 'NOT MAPPED'}")
print("\n=== Axes ===")
for f, col in AXES.items():
    print(f"{f:15s} {col!r} present={col in header}")
print("\n=== Top 25 unmapped columns by rows used ===")
un = df[df.role == "unmapped"].head(25)
print(un[["column", "tags", "nonnull_rows", "n_filings"]].to_string(index=False))
print(f"\nUnmapped total: {(df.role == 'unmapped').sum()}   Saved: {OUT}")