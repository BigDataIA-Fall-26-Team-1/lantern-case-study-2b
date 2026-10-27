"""P3 step 1: reconcile every filing with the team rules and write the outputs."""
import json
import sys

import pandas as pd

sys.path.insert(0, "src")
from lookthrough import paths, pipeline, reconcile, report, rules

root = paths.repo_root()
P = paths.load_params(root)
rdir = paths.release_dir(P, root)
tol = float(P["reconcile"]["tolerance"])

B = pipeline.run_baseline(rdir, tol, rules=rules.TEAM_RULES)
rec, diag, sub = B["rec"], B["diag"], B["sub"]
report.write_outputs(B["kept"], rec, diag, B["log"], root, P)

# coverage.json with the count of SUB filings that have no SOI rows
cov = reconcile.coverage(rec, sub)
(root / P["outputs"]["reports"] / "coverage.json").write_text(json.dumps(cov, indent=2))
work = root / "outputs" / "p3_work"
work.mkdir(parents=True, exist_ok=True)
pd.to_pickle(B, work / "baseline.pkl")
print(json.dumps(cov, indent=2))

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