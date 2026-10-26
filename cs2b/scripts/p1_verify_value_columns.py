"""P1 step 1c: which SOI column really holds fair value and cost? Check against NUM."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "src")
from lookthrough.mapping import parse_segments

RAW = Path("data/raw")
MERGED = RAW / "2026q1_bdc"
READ = dict(sep="\t", dtype=str, keep_default_na=False, na_values=[""])
FV_NEW, CO_NEW = "Initial fair value of Investment", "Adjusted cost basis"
FV_OLD, CO_OLD = "Investment Owned, Fair Value", "Investment Owned, Cost"
ID = "Investment, Identifier Axis"
WATCH = [FV_NEW, CO_NEW, FV_OLD, CO_OLD]

# A. The raw monthly files, before our merge
print("=== A. Monthly SOI files (before merge) ===")
for p in sorted(RAW.glob("**/soi.tsv")):
    if MERGED in p.parents:
        continue
    hdr = pd.read_csv(p, nrows=0, **READ).columns
    present = [c for c in WATCH if c in hdr]
    df = pd.read_csv(p, usecols=present, **READ)
    counts = {c: int(df[c].notna().sum()) for c in present}
    print(p, "| missing:", [c for c in WATCH if c not in hdr], "| non-null:", counts)

# B. How often are the two new columns identical?
soi = pd.read_csv(MERGED / "soi.tsv",
                  usecols=["adsh", "ddate", "source_soi_row", ID, FV_NEW, CO_NEW], **READ)
fv = pd.to_numeric(soi[FV_NEW], errors="coerce")
co = pd.to_numeric(soi[CO_NEW], errors="coerce")
both = fv.notna() & co.notna()
print("\n=== B. Initial fair value vs Adjusted cost basis ===")
print(f"rows with both: {both.sum():,}   identical: {(both & (fv == co)).sum():,}")

# C. Ground truth from NUM for one filing (PennantPark)
ADSH = "0001193125-26-021227"
TAGS = {"InvestmentOwnedAtFairValue": "num_fv", "InvestmentOwnedAtCost": "num_cost"}
keep = []
for ch in pd.read_csv(MERGED / "datasets" / "num.tsv", chunksize=500_000, **READ):
    keep.append(ch[(ch["adsh"] == ADSH) & ch["tag"].isin(TAGS)])
num = pd.concat(keep)
num["identifier"] = num["segments"].map(lambda s: parse_segments(s).get("InvestmentIdentifierAxis"))
num = num[num["identifier"].notna()]
num["ddate"] = pd.to_datetime(num["ddate"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
num["value"] = pd.to_numeric(num["value"], errors="coerce")
facts = (num.groupby(["identifier", "ddate", "tag"])["value"].first()
         .unstack("tag").rename(columns=TAGS).reset_index())

one = soi[soi["adsh"] == ADSH].rename(columns={ID: "identifier"})
one["ddate"] = pd.to_datetime(one["ddate"]).dt.strftime("%Y-%m-%d")
one[FV_NEW] = pd.to_numeric(one[FV_NEW], errors="coerce")
one[CO_NEW] = pd.to_numeric(one[CO_NEW], errors="coerce")
m = one.merge(facts, on=["identifier", "ddate"], how="inner")
print(f"\n=== C. {ADSH}: SOI rows {len(one):,}, matched to NUM facts {len(m):,} ===")
for col in (FV_NEW, CO_NEW):
    for ref in ("num_fv", "num_cost"):
        if ref in m:
            ok = m[col].notna() & m[ref].notna()
            eq = ok & ((m[col] - m[ref]).abs() <= 0.5)
            print(f"{col!r:36s} equals {ref:8s}: {eq.sum():5d} of {ok.sum():5d}")
cols = ["source_soi_row", "identifier", "ddate", FV_NEW, CO_NEW, "num_fv", "num_cost"]
print(m[[c for c in cols if c in m]].head(5).to_string(index=False))
