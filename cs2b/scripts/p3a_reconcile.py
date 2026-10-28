"""P3 step 1 / P5 stage 'reconcile': reconcile every filing to its filed total; write the panel.

Reads the parse and clean stage outputs and runs the kit's filed_totals, reconcile and diagnose
(pipeline.run_baseline lines 18-21). Writes, and is the only writer of:
  outputs/panel/holdings.parquet   admitted filings only, PANEL_COLS (as report.write_outputs)
  reports/coverage.json            DVC metric, with filings_without_soi_rows (needs SUB)
  outputs/p3_work/baseline.pkl     for the report stage (p3b-p3e) and p3f
coverage.csv, coverage.md and triage.md are written by p3e (report stage); cleaning_log.csv by clean.
Run from cs2b/:  python scripts/p3a_reconcile.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lookthrough import paths, reconcile, report, tables  # noqa: E402
from workio import load_frame  # noqa: E402

root = paths.repo_root()
P = paths.load_params(root)
tol = float(P["reconcile"]["tolerance"])

parse_dir, clean_dir = root / "outputs" / "work" / "parse", root / "outputs" / "work" / "clean"
sub, num, canon, hold = (load_frame(parse_dir, n) for n in ("sub", "num", "canon", "holdings"))
soi_adsh = set(load_frame(parse_dir, "soi_adsh")["adsh"])
kept, log = load_frame(clean_dir, "kept"), load_frame(clean_dir, "log")

filed = reconcile.filed_totals(num, sub)
rec = reconcile.reconcile(kept, filed, sub, tol, soi_adsh=soi_adsh)
diag = reconcile.diagnose(rec, kept, num, canon)

# Panel: exactly as report.write_outputs writes it
admitted = set(rec.loc[rec["admitted"], "adsh"])
panel = kept[kept["adsh"].isin(admitted)][[c for c in report.PANEL_COLS if c in kept]]
panel_path = tables.save_table(panel, root / P["outputs"]["panel"] / "holdings")

# coverage.json with the count of SUB filings that have no SOI rows (LF on every OS)
cov = reconcile.coverage(rec, sub)
with open(root / P["outputs"]["reports"] / "coverage.json", "w", newline="\n") as fh:
    fh.write(json.dumps(cov, indent=2))

# baseline.pkl: the keys the report stage reads
B = {"sub": sub, "num": num, "canon": canon, "holdings": hold, "kept": kept, "log": log,
     "rec": rec, "diag": diag, "soi_adsh": soi_adsh}
work = root / "outputs" / "p3_work"
work.mkdir(parents=True, exist_ok=True)
pd.to_pickle(B, work / "baseline.pkl")
print(json.dumps(cov, indent=2))
print(f"panel: {len(panel):,} rows, {panel['adsh'].nunique()} filings -> {panel_path.relative_to(root).as_posix()}")

no_soi = sub[~sub["adsh"].isin(rec["adsh"])]
print(f"\n=== SUB filings with no SOI rows: {len(no_soi)} ===")
print(no_soi[["adsh", "name", "form", "period"]].to_string(index=False))

# The excluded filings, bucketed by gap
ex = rec[~rec["admitted"]].copy()


def bucket(r):
    if pd.isna(r.filed_fv):
        return "1 no filed total"
    if r.n_holdings == 0:
        return "2 no holdings"
    g = r.gap_pct
    return ("3 below -50%" if g < -0.5 else "4 -50% to -1%" if g < 0
            else "5 +1% to +50%" if g <= 0.5 else "6 above +50%")


ex["bucket"] = ex.apply(bucket, axis=1)
print(f"\n=== Excluded filings: {len(ex)} ===")
print(ex.groupby("bucket").agg(n=("adsh", "size"),
                               filed_bn=("filed_fv", lambda s: s.sum() / 1e9)).round(2).to_string())

top = ex.nlargest(15, "filed_fv").merge(
    diag[["adsh", "rows_without_identifier", "missing_fv_rows",
          "custom_fv_facts_in_num", "negative_type_level_fv"]], on="adsh")
top["hold_m"] = top["holdings_fv"] / 1e6
top["filed_m"] = top["filed_fv"] / 1e6
print("\n=== 15 largest excluded filings ===")
print(top[["adsh", "name", "form", "n_holdings", "hold_m", "filed_m", "gap_pct",
           "rows_without_identifier", "missing_fv_rows", "custom_fv_facts_in_num"]]
      .round(3).to_string(index=False, max_colwidth=30))