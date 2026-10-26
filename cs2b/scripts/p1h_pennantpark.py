"""P1 step 3b: are PennantPark's 'plain' rows its JV's (PSSL's) loans?"""
from p1_common import load_current

A, FILED = "0001193125-26-021227", 1_287_273_000
PREFIX = r"\s*I?nvestments in"
cur, hold, extra, fields = load_current()
h = hold[(hold.adsh == A) & hold.subsidiary.isna() & hold.range.isna()].copy()
h["style"] = h["identifier"].str.match(PREFIX).map({True: "prefixed", False: "plain"})

print("=== Corrected styles vs filed total ===")
for s, df in h.groupby("style"):
    fv = df["fair_value"].sum()
    print(f"{s:9s} holdings {len(df):4d}  fv ${fv / 1e6:,.1f}m  gap vs filed {(fv - FILED) / FILED:+.2%}")
missing_i = h["identifier"].str.match(r"\s*nvestments in").sum()
print(f"missing 'I': {missing_i} holdings")

# Do the plain rows carry any other axis that marks them as the JV's?
rows = cur[cur.adsh == A].copy()
rows["style"] = rows["identifier"].str.match(PREFIX).map({True: "prefixed", False: "plain"})
print("\n=== Non-empty extra axes, by style (row counts) ===")
print(rows.groupby("style")[extra].count().T[lambda d: d.sum(axis=1) > 0].to_string())

# Same borrower in both styles?
iss = h["identifier"].str.extract(r"Issuer Name (.+?) (?:Acquisition|Maturity|Industry)")[0]
both = set(iss[h["style"] == "plain"].dropna()) & set(iss[h["style"] == "prefixed"].dropna())
print(f"\nborrowers in plain: {iss[h['style'] == 'plain'].nunique()}, "
      f"also in prefixed: {len(both)}")
print("examples:", sorted(both)[:5])