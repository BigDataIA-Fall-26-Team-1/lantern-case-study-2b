"""P1 step 4: actual date formats in our release, and whether norm_date handles them."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "src")
from lookthrough.load import READ, load_sub, norm_date

RDIR = Path("data/raw/2026q1_bdc")
PATTERNS = {"yyyymmdd": r"\d{8}", "yyyy-mm-dd": r"\d{4}-\d{2}-\d{2}",
            "mm/dd/yyyy": r"\d{1,2}/\d{1,2}/\d{4}"}


def profile(name, s):
    s = s.dropna().astype(str).str.strip()
    counts = {k: int(s.str.fullmatch(p).sum()) for k, p in PATTERNS.items()}
    counts["other"] = len(s) - sum(counts.values())
    lost = int(norm_date(s).isna().sum())
    print(f"{name:34s} non-empty {len(s):7,}  {counts}  lost by norm_date: {lost}")
    if counts["other"]:
        other = s[~s.str.fullmatch("|".join(PATTERNS.values()))]
        print(f"{'':34s} examples of other: {other.unique()[:5].tolist()}")


print("=== Raw date formats ===")
soi = pd.read_csv(RDIR / "soi.tsv", usecols=["ddate", "period", "filed",
                  "Investment Maturity Date"], **READ)
for c in soi.columns:
    profile(f"SOI {c}", soi[c])
raw_sub = pd.read_csv(RDIR / "datasets" / "sub.tsv", usecols=["period", "filed"], **READ)
for c in raw_sub.columns:
    profile(f"SUB {c}", raw_sub[c])
num = next(pd.read_csv(RDIR / "datasets" / "num.tsv", usecols=["ddate"],
                       chunksize=500_000, **READ))
profile("NUM ddate (first 500k rows)", num["ddate"])

print("\n=== Current vs comparative, by form (latest filings) ===")
sub = load_sub(RDIR)
s = pd.read_csv(RDIR / "soi.tsv", usecols=["adsh", "ddate"], **READ)
s = s[s["adsh"].isin(sub["adsh"])]
s["ddate"] = norm_date(s["ddate"])
s = s.merge(sub[["adsh", "form", "period"]], on="adsh")
s["schedule"] = (s["ddate"] == s["period"]).map({True: "current", False: "comparative"})
print(pd.crosstab(s["form"], s["schedule"]).to_string())
f = s.groupby("adsh")["schedule"].agg(lambda x: (x == "current").sum())
print(f"\nfilings with SOI rows: {len(f)}   with no current-period rows: {(f == 0).sum()}")
odd = s[s["schedule"] == "comparative"].groupby(["form", "ddate"]).size()
print("\ncomparative dates (top 8):")
print(odd.sort_values(ascending=False).head(8).to_string())