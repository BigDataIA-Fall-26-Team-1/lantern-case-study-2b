"""P1 step 1b: compare the untagged SOI columns with the canonical ones."""
from pathlib import Path

import pandas as pd

RDIR = Path("data/raw/2026q1_bdc")
READ = dict(sep="\t", dtype=str, keep_default_na=False, na_values=[""])
PAIRS = [
    ("Initial fair value of Investment", "Investment Owned, Fair Value"),
    ("Adjusted cost basis", "Investment Owned, Cost"),
]
ID = "Investment, Identifier Axis"
META = ["adsh", "name", "ddate", "period", "source_release", "source_soi_row", ID]

# 1. Does TAG know these labels at all?
tag = pd.read_csv(RDIR / "datasets" / "tag.tsv", **READ)
hit = tag[tag["tlabel"].str.contains(
    r"initial fair value|adjusted cost|investment shares", case=False, na=False)]
print("=== TAG rows whose label looks similar ===")
print(hit[["tag", "custom", "tlabel"]].drop_duplicates().head(15).to_string(index=False))

# 2. Compare each pair, row by row
cols = META + [c for p in PAIRS for c in p] + ["Investment shares"]
soi = pd.read_csv(RDIR / "soi.tsv", usecols=cols, **READ)
for new, old in PAIRS:
    a = pd.to_numeric(soi[new], errors="coerce")
    b = pd.to_numeric(soi[old], errors="coerce")
    both, only_new, only_old = a.notna() & b.notna(), a.notna() & b.isna(), a.isna() & b.notna()
    same = both & ((a - b).abs() <= 0.5)
    print(f"\n=== {new!r} vs {old!r} ===")
    print(f"both: {both.sum():,}  (equal: {same.sum():,}, different: {(both & ~same).sum():,})")
    print(f"only {new!r}: {only_new.sum():,}")
    print(f"only {old!r}: {only_old.sum():,}")
    # filings where the canonical column is never filled but the new one is
    g = soi.assign(a=a.notna(), b=b.notna()).groupby("adsh")[["a", "b"]].any()
    lost = g[g.a & ~g.b]
    print(f"filings with {new!r} but no {old!r} at all: {len(lost)}")
    show = META + [new, old]
    print("examples, only new column:")
    print(soi.loc[only_new, show].head(3).to_string(index=False))
    print("examples, both but different:")
    print(soi.loc[both & ~same, show].head(3).to_string(index=False))

# 3. Investment shares: what does it look like?
print("\n=== Investment shares, sample ===")
s = soi[soi["Investment shares"].notna()]
print(s[["adsh", "name", ID, "Investment shares"]].head(5).to_string(index=False))