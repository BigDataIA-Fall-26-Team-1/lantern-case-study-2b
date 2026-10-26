"""Bonus: evidence for reports/issue_draft.md (SOI value columns whose headers are missing from TAG).

For each monthly release, counts filled rows under the TAG-labelled fair value / cost columns and
under the headers that actually hold the values, and checks whether TAG has those headers as labels.
Run from cs2b/:  python scripts/bonus_issue_evidence.py   ->  reports/issue_evidence.csv
"""
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
COLS = ["Investment Owned, Fair Value", "Initial fair value of Investment",
        "Investment Owned, Cost", "Adjusted cost basis"]
rows = []
for m in ["2026_01", "2026_02", "2026_03"]:
    d = RAW / f"{m}_bdc"
    header = pd.read_csv(d / "soi.tsv", sep="\t", nrows=0).columns
    soi = pd.read_csv(d / "soi.tsv", sep="\t", dtype=str, keep_default_na=False, na_values=[""],
                      usecols=[c for c in COLS if c in header])
    tag = pd.read_csv(d / "datasets" / "tag.tsv", sep="\t", dtype=str, keep_default_na=False)
    labels = tag[tag["tag"].isin(["InvestmentOwnedAtFairValue", "InvestmentOwnedAtCost"])]
    row = {"release": m, "soi_rows": len(soi)}
    for c in COLS:
        row[f"filled: {c}"] = int(soi[c].notna().sum()) if c in soi else "column absent"
        row[f"in TAG tlabel: {c}"] = bool((tag["tlabel"] == c).any())
    row["TAG labels for the two tags"] = "; ".join(
        sorted(set(labels["tag"] + " " + labels["version"] + " = " + labels["tlabel"])))
    rows.append(row)

out = pd.DataFrame(rows)
out.to_csv("reports/issue_evidence.csv", index=False)
print(out.T.to_string(header=False))
print("\nwrote reports/issue_evidence.csv")
