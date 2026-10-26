"""P0: prove the merge kept every value. For each table, pandas reads (the kit's load.READ) of the
3 months, concatenated by column name, must equal the pandas read of data/raw/2026q1_bdc.
Ignored: the columns the merge adds (source_release, source_soi_row); tag.tsv exact duplicates."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lookthrough import load  # noqa: E402

RAW = ROOT / "data" / "raw"
MONTHS = ["2026_01", "2026_02", "2026_03"]
OUT = RAW / "2026q1_bdc"
TABLES = ["soi.tsv"] + [f"datasets/{t}.tsv" for t in ("sub", "tag", "num", "txt", "pre", "cal", "non")]
ADDED = ["source_release", "source_soi_row"]

ok = True
for t in TABLES:
    parts = [pd.read_csv(RAW / f"{m}_bdc" / t, **load.READ) for m in MONTHS if (RAW / f"{m}_bdc" / t).exists()]
    want = pd.concat(parts, ignore_index=True)
    if t == "datasets/tag.tsv":
        want = want.drop_duplicates(ignore_index=True)
    got = pd.read_csv(OUT / t, **load.READ)
    got = got.drop(columns=[c for c in ADDED if c in got.columns])
    same = set(got.columns) == set(want.columns) and got.equals(want[list(got.columns)])
    ok &= same
    print(f"  {'SAME' if same else 'DIFF'}  {t}: merged {len(got):,} rows x {got.shape[1]} cols | "
          f"months {len(want):,} x {want.shape[1]}")
print("merge verified: every value equals the monthly files" if ok else "MERGE DIFFERS: send this output")
sys.exit(0 if ok else 1)