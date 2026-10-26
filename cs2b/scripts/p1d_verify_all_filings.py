"""P1 step 1d: verify the renamed SOI value columns against NUM for every filing."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "src")
from lookthrough.mapping import parse_segments

MERGED = Path("data/raw/2026q1_bdc")
OUT = Path("reports/p1_value_column_check.csv")
READ = dict(sep="\t", dtype=str, keep_default_na=False, na_values=[""])
ID = "Investment, Identifier Axis"
TAGS = {"InvestmentOwnedAtFairValue": "num_fv",
        "InvestmentOwnedAtCost": "num_cost",
        "InvestmentOwnedBalanceShares": "num_shares"}
PAIRS = [("Initial fair value of Investment", "num_fv"),
         ("Adjusted cost basis", "num_cost"),
         ("Investment shares", "num_shares")]


def iso(s):
    return pd.to_datetime(s, errors="coerce", format="mixed").dt.strftime("%Y-%m-%d")


# NUM: facts on these tags that carry an identifier
keep = []
for ch in pd.read_csv(MERGED / "datasets" / "num.tsv", chunksize=500_000, **READ):
    m = ch["tag"].isin(TAGS) & ch["segments"].str.contains("InvestmentIdentifierAxis", na=False)
    keep.append(ch.loc[m, ["adsh", "tag", "ddate", "segments", "value"]])
num = pd.concat(keep, ignore_index=True)
num["identifier"] = num["segments"].map(lambda s: parse_segments(s).get("InvestmentIdentifierAxis"))
num["ddate"] = iso(num["ddate"])
num["value"] = pd.to_numeric(num["value"], errors="coerce")
facts = (num.dropna(subset=["identifier"])
         .groupby(["adsh", "identifier", "ddate", "tag"])["value"].first()
         .unstack("tag").rename(columns=TAGS).reset_index())
print(f"NUM facts with an identifier: {len(num):,}")

# SOI
soi = pd.read_csv(MERGED / "soi.tsv",
                  usecols=["adsh", "name", "ddate", ID] + [p[0] for p in PAIRS], **READ)
soi = soi.rename(columns={ID: "identifier"})
soi["ddate"] = iso(soi["ddate"])
for col, _ in PAIRS:
    soi[col] = pd.to_numeric(soi[col], errors="coerce")
m = soi.merge(facts, on=["adsh", "identifier", "ddate"], how="inner")
print(f"SOI rows matched to NUM: {len(m):,} of {len(soi):,}")

# Overall and per filing
rows = []
print("\n=== Overall ===")
for col, ref in PAIRS:
    ok = m[col].notna() & m[ref].notna() if ref in m else pd.Series(False, index=m.index)
    eq = ok & ((m[col] - m[ref]).abs() <= 0.5)
    m[f"ok_{ref}"], m[f"eq_{ref}"] = ok, eq
    print(f"{col!r:36s} = {ref:10s}: {eq.sum():7,} of {ok.sum():7,} "
          f"({eq.sum() / max(ok.sum(), 1):.2%})")
agg = {f"{k}_{ref}": (f"{k}_{ref}", "sum") for _, ref in PAIRS for k in ("ok", "eq")}
per = m.groupby(["adsh", "name"]).agg(**agg).reset_index()
for _, ref in PAIRS:
    per[f"rate_{ref}"] = per[f"eq_{ref}"] / per[f"ok_{ref}"].where(per[f"ok_{ref}"] > 0)
per.to_csv(OUT, index=False)

print(f"\nFilings compared on fair value: {(per.ok_num_fv > 0).sum()}")
bad = per[per.rate_num_fv < 0.99].sort_values("rate_num_fv")
print(f"Filings with fair-value match below 99%: {len(bad)}")
print(bad[["adsh", "name", "ok_num_fv", "eq_num_fv", "rate_num_fv"]].head(10).to_string(index=False))
print(f"\nSaved {OUT}")
