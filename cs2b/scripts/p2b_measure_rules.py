"""P2b: apply the team rules to 2026q1, write the cleaning log, and measure each rule.

Writes reports/cleaning_log.csv (rule, artifact, rows affected, example adsh / soi_row) and
reports/p2_rule_ablation.csv (coverage with all rules, and with each rule removed in turn).
Run from cs2b/:  python scripts/p2b_measure_rules.py
"""
import sys
from pathlib import Path

sys.path.insert(0, "src")
import pandas as pd
from lookthrough import clean, paths, pipeline, reconcile, rules

ROOT = Path(".")
P = paths.load_params(ROOT)
tol = P["reconcile"]["tolerance"]
B = pipeline.run_baseline(paths.release_dir(P, ROOT), tol)          # kit rules: the baseline
hc = B["holdings"][B["holdings"]["is_current"]]
filed = reconcile.filed_totals(B["num"], B["sub"])
soi_adsh = set(B["soi"]["adsh"])


def run(rule_list):
    kept, log = clean.apply_rules(hc, rule_list)
    rec = reconcile.reconcile(kept, filed, B["sub"], tol, soi_adsh=soi_adsh)
    return reconcile.coverage(rec, B["sub"]), rec, log


kit, rec_kit, _ = run([clean.rule_totals, clean.rule_cash])
team, rec_team, log = run(rules.TEAM_RULES)
log.to_csv("reports/cleaning_log.csv", index=False)

lines = [{"run": "kit rules (rule_totals, rule_cash)", **kit}, {"run": "all team rules", **team}]
for r in rules.TEAM_RULES:
    c, _, _ = run([x for x in rules.TEAM_RULES if x is not r])
    lines.append({"run": f"without {r.__name__}", **c})
abl = pd.DataFrame(lines)[["run", "filings_admitted", "filings_attempted", "share_of_filings", "share_of_dollars"]]
abl.to_csv("reports/p2_rule_ablation.csv", index=False)

pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print("Cleaning log:"); print(log.to_string(index=False))
print("\nCoverage:"); print(abl.to_string(index=False))
m = rec_kit[["adsh", "name", "gap_pct", "admitted"]].merge(
    rec_team[["adsh", "gap_pct", "admitted"]], on="adsh", suffixes=("_kit", "_team"))
print("\nFilings whose admission changed (kit -> team):")
print(m[m["admitted_kit"] != m["admitted_team"]].round(4).to_string(index=False))
print("\nwrote reports/cleaning_log.csv and reports/p2_rule_ablation.csv")
