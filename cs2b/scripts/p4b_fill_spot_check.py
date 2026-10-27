"""P4b: write the hand-checked filing values into reports/spot_check.csv.

Each result below was read from the filing's human-readable schedule (plain document URL in the
CSV), on 27 Oct 2026. Values are as printed in the filing, in the filing's own units (filing_units).
matches = yes | no | not a holding. Run from cs2b/ after p4a:  python scripts/p4b_fill_spot_check.py
"""
from pathlib import Path

import pandas as pd

OUT = Path("reports/spot_check.csv")

# check: (filing_fair_value, filing_principal, filing_units, matches, where_in_filing, note)
R = {
    "S01": ("1,903.4", "—", "millions", "yes", "Consolidated Schedule of Investments, Dec 31 2025, p. F-21",
            "Ivy Hill Asset Management, L.P., member interest (100.00%); cost 1,700.5. Equity, no principal. Schedule in millions to one decimal; matches at that precision."),
    "S02": ("—", "—", "millions", "not a holding", "Consolidated Schedule of Investments, Dec 31 2025",
            "Panel row (soi_row 58925) is a company-level row with no fair value, cost or principal; in the SOI it carries only 'Investment Company, Financial Support to Investee Contractually Required' 7.3m and '... Not Provided' 2.2m. The filing's three Repairify lines (revolver 5.1, first lien 5.0, Class A units 2.7; subtotal 12.8) match panel rows 58923, 58921, 58920 exactly."),
    "S03": ("322,696", "325,134", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Aerospace & Defense",
            "MRO Holdings, Inc., First Lien Secured Debt - Term Loan, S+450, 0.50% floor, maturity 10/4/2032; cost 324,277. SOI identifier prefixes the industry and group header ('Aerospace & Defense MRO Holdings ...')."),
    "S04": ("106", "— (100 shares)", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Pharmaceuticals, p. 124",
            "PAI Co-Investor FT Aggregator LLC, Common Equity - Stock, 100 shares; cost 100."),
    "S05": ("391,000.0", "391,000.0", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, p. F-19",
            "ADLP LLC, Subordinated certificates, 10.00%, maturity 10/2035; cost 391,000.0. Footnote (14): $2.0bn committed, $391.0m funded."),
    "S06": ("15,563.5", "16,135.0", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, p. F-38",
            "University Support Services LLC, first lien senior secured loan, 6.47%, SOFR (M) + 2.75%, maturity 02/2029; cost 16,111.4."),
    "S07": ("339,635", "354,710", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Health Care Providers & Services",
            "Snoopy Bidco, Inc., First Lien Debt, SOFR + 6.50%, 10.53% (incl. 5.50% PIK), maturity 6/1/2028; cost 352,390."),
    "S08": ("33,718", "33,718", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Electric Utilities, p. 158",
            "Qualus Power Services Corp., First Lien Debt, SOFR + 4.25%, 8.02%, acquired 5/9/2024; cost 33,498. SOI suffix '4' = fourth of four Qualus lines; not in the filing."),
    "S09": ("169,615", "169,615", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, p. 24",
            "MYOB Invest Co Pty Ltd, One stop, A + 5.25%, 6.19% cash / 2.75% PIK, maturity 06/2030; cost 163,635. Principal column is 'Principal ($)', so USD."),
    "S10": ("8,563", "8,521", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Aerospace & Defense, p. 8",
            "Signia Aerospace, LLC, Senior secured, SF + 2.75%, 6.57%, maturity 12/2031; cost 8,519. SOI suffix '1' = first of two Signia lines."),
    "S11": ("9,264", "9,264", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Software",
            "Anaplan, Inc., One stop, SF + 4.50%, 8.32%, maturity 06/2029; cost 9,218. SOI suffix '1' = first of two Anaplan lines."),
    "S12": ("712", "716", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Life Sciences Tools & Services",
            "Celerion Buyer, Inc., One stop, SF + 5.00%, 8.89%, maturity 11/2029; cost 710. SOI suffix '3' = third of four Celerion lines (unfunded line counted)."),
    "S13": ("24,625", "24,625", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Transportation & Logistics",
            "CSG Buyer, Inc., Senior Secured First Lien Term Loan, 3M S + 6.25%, 10.09%, maturity 7/29/2029; cost 24,260."),
    "S14": ("—", "— (3,500,000 units)", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Warrants",
            "MB Precision Investment Holdings LLC, Warrant Units, 3,500,000 units; filing prints cost — and fair value —, consistent with the panel's empty values. Schedule Total Investments 776,189."),
    "S15": ("31,309", "31,867", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Consumer Goods: Non-Durable",
            "Vivos Holdings, LLC, First Lien Term Loan, S + 6.00%, 9.74%, maturity 8/13/2030; cost 31,556."),
    "S16": ("(2)", "-", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, FIRE: Finance",
            "Allworth Financial Group, L.P., First Lien Revolving Loan, S + 4.75%, 8.47%, maturity 12/23/2027; cost (2). Undrawn revolver marked below par; par '-' matches empty principal."),
    "S17": ("41,857", "41,857", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Business Services, p. 77",
            "Viper Bidco, Inc., First Lien, SOFR(Q) + 4.75%, 8.42%, maturity 11/2031; cost 41,673."),
    "S18": ("5,381", "5,381", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Distribution & Logistics, p. 86",
            "Radwell Parent, LLC, First Lien, SOFR(Q) + 5.50%, 9.17%, maturity 04/2029; cost 5,334."),
    "S19": ("12,796", "12,906", "thousands", "yes", "Consolidated Schedule of Investments, Dec 31 2025, Professional Services, p. 90",
            "Deerfield Dakota Holding, LLC, First Lien Debt, S + 5.75% (incl. 2.75% PIK), 9.42%, maturity 09/13/2032; cost 12,783."),
    "S20": ("—", "—", "thousands", "not a holding", "Unfunded commitments table in the Consolidated Schedule of Investments, Dec 31 2025",
            "Panel row (soi_row 120878) is Granicus, Inc.'s Delayed Draw Term Loan commitment (expiration 07/31/2026; unfunded commitment 398; fair value —), not a funded holding. In the SOI it carries fair value 0 and 'Financial Support ... Not Provided' 398,000. Granicus's three schedule lines are separate panel rows (soi_rows 133425-133427)."),
}

s = pd.read_csv(OUT, dtype=str)
missing = set(s["check"]) - set(R)
assert not missing, f"no result recorded for {sorted(missing)}"
for col in ["filing_fair_value", "filing_principal", "filing_units", "matches", "where_in_filing", "note"]:
    if col not in s:
        s[col] = ""
for i, c in s["check"].items():
    fv, pr, units, m, where, note = R[c]
    s.loc[i, ["filing_fair_value", "filing_principal", "filing_units", "matches", "where_in_filing", "note"]] = [fv, pr, units, m, where, note]
s.to_csv(OUT, index=False)
print(s["matches"].value_counts().to_string())
print(f"\n{len(s)} holdings across {s['adsh'].nunique()} filings written to {OUT}")
