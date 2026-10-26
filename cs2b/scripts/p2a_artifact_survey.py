"""P2a: survey the cleaning artifacts in release 2026q1 before writing any rule.

For each artifact the brief (Part 2) asks us to investigate, plus the ones Part 1 handed over,
count how often it appears in the CURRENT period, how many filings and how much fair value it
touches, and give two examples (adsh / soi_row) a grader can open.
Run from cs2b/:  python scripts/p2a_artifact_survey.py
Writes reports/p2_artifact_survey.csv.
"""
import sys
from pathlib import Path

sys.path.insert(0, "src")
import pandas as pd
from lookthrough import clean, paths, pipeline

ROOT = Path(".")
P = paths.load_params(ROOT)
B = pipeline.run_baseline(paths.release_dir(P, ROOT), P["reconcile"]["tolerance"])
canon, h = B["canon"], B["holdings"]
cur_rows = canon[canon["is_current"]]                 # SOI rows, current period
hc = h[h["is_current"]]                               # coalesced holdings, current period
CAT = ["investment_type", "industry", "affiliation"]
EQUITY = r"\b(?:equity|warrants?|common|preferred|units|shares|stock|membership interest)\b"
ENTITY = r"^\s*total\b[^|]*?\b(?:llc|inc|l\.?p|ltd|limited|corp|corporation|holdings|plc|gmbh|sarl|s\.a)\b"

rows = []


def add(artifact, what, frame, row_col):
    """One survey line: counts, filings, fair value and two examples."""
    fv = pd.to_numeric(frame["fair_value"], errors="coerce")
    ex = frame.head(2)
    rows.append({"artifact": artifact, "measure": what, "count": len(frame),
                 "filings": frame["adsh"].nunique(), "fair_value_musd": round(fv.sum() / 1e6, 1),
                 "examples": "; ".join(f"{a} / soi_row {r}" for a, r in zip(ex["adsh"], ex[row_col]))})


tot, _ = clean.rule_totals(hc)
add("totals_subtotals", "holdings the kit's rule_totals drops", hc[tot], "source_rows")
add("totals_subtotals", "...of which look like borrowers named 'Total ...'",
    hc[tot & hc["identifier"].str.contains(ENTITY, case=False, na=False)], "source_rows")
add("subtotal_rows_no_id", "current SOI rows with no identifier but a type/industry/affiliation axis",
    cur_rows[cur_rows["identifier"].isna() & cur_rows[CAT].notna().any(axis=1)], "soi_row")
add("custom_axis_no_id", "current SOI rows with no identifier, a fair value, and no category axis",
    cur_rows[cur_rows["identifier"].isna() & cur_rows["fair_value"].notna()
             & cur_rows[CAT + ["subsidiary", "range"]].isna().all(axis=1)], "soi_row")
cash, _ = clean.rule_cash(hc)
add("cash_lines", "holdings the kit's rule_cash drops", hc[cash], "source_rows")
add("restated_copies", "holdings built from 2+ SOI rows whose values agree", hc[(hc["n_rows"] > 1) & (hc["n_conflicts"] == 0)], "source_rows")
add("restated_copies", "holdings built from 2+ SOI rows whose values disagree", hc[hc["n_conflicts"] > 0], "source_rows")
add("comparative_rows", "comparative-period SOI rows (prior year-end)", canon[~canon["is_current"]], "soi_row")
add("unfunded_commitments", "holdings with negative fair value", hc[hc["fair_value"] < 0], "source_rows")
add("unfunded_commitments", "holdings with fair value exactly 0", hc[hc["fair_value"] == 0], "source_rows")
add("custom_tag_values", "holdings with no fair value in SOI", hc[hc["fair_value"].isna()], "source_rows")
add("affiliate_control", "holdings with an affiliation on the holding itself", hc[hc["affiliation"].notna()], "source_rows")
add("equity_warrants", "holdings with no principal whose identifier names equity or warrants",
    hc[hc["principal"].isna() & hc["identifier"].str.contains(EQUITY, case=False, na=False)], "source_rows")
add("jv_subsidiary_axis", "holdings on the Nonconsolidated Subsidiary axis", hc[hc["subsidiary"].notna()], "source_rows")
add("range_axis", "holdings on the Range axis", hc[hc["range"].notna()], "source_rows")
add("member_as_identifier", "holdings whose identifier is an XBRL member ('... [Member]')",
    hc[hc["identifier"].str.contains(r"\[Member\]\s*$", na=False)], "source_rows")

out = pd.DataFrame(rows)
out.to_csv("reports/p2_artifact_survey.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
print(f"current SOI rows {len(cur_rows):,} | current holdings {len(hc):,} | filings with SOI rows {canon['adsh'].nunique()}")
print(out.drop(columns="examples").to_string(index=False))
print("\nExamples (adsh / soi_row):")
for r in out.itertuples():
    print(f"  {r.artifact:22s} {r.examples}")
print("\nwrote reports/p2_artifact_survey.csv")
