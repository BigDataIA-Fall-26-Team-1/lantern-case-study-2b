# Cleaning log (Part 2)

Release 2026q1 (2026_01 + 2026_02 + 2026_03, merged in Part 0). Rules live in
`src/lookthrough/rules.py` (`TEAM_RULES`) and run, in this order, on current-period holdings
after coalescing. Every rule follows the kit's contract: a drop mask and a one-line artifact.
Machine-readable log: `reports/cleaning_log.csv`. Measurements: `reports/p2_artifact_survey.csv`
(`scripts/p2a_artifact_survey.py`) and `reports/p2_rule_ablation.csv` (`scripts/p2b_measure_rules.py`).
`soi_row` is the 0-based data row in `data/raw/2026q1_bdc/soi.tsv`.

## Result

| Rules | Filings admitted (of 171) | Share of filed fair value |
|---|---:|---:|
| Kit baseline (`rule_totals`, `rule_cash`) | 72 | 24.2% |
| Team rules | 79 | 27.0% |

Newly admitted: Bain Capital Specialty Finance (0001193125-26-077703, gap +90.5% to 0.00%),
New Mountain Finance (0001496099-26-000008, +58.7% to +0.93%), PennantPark Floating Rate
(0001193125-26-042778, +53.3% to +0.29%), Oaktree Specialty Lending (0001414932-26-000005,
+18.3% to +0.98%), PennantPark Investment 10-K/A (0001193125-26-021227, +98.3% to 0.00%),
New Mountain Private Credit (0002037804-26-000005, +13.6% to +0.67%), TriplePoint Venture
Growth (0001580345-26-000008, -2.85% to 0.00%). No filing lost admission.

## Rules

### 1. `rule_jv_subsidiary`: JV portfolio rows on the subsidiary axis
**Artifact.** Some BDCs disclose the loans held by their joint ventures in separate schedules,
tagged on `Investment Company, Nonconsolidated Subsidiary Axis`. The BDC's own stake in the JV is
already one holding in its schedule, so counting the JV's loans counts the same money twice.
Part 1 kept these rows apart by adding the axis to the coalescing key; this rule drops them.
**Example.** Bain Capital Specialty Finance 0001193125-26-077703, soi_row 12576: "Aerospace &
Defense ATS First Lien Senior Secured Loan ..." on `Bain Capital Senior Loan Program, LLC [Member]`,
fair value $20,114,000.
**Rows affected.** 788 holdings in 10 filings ($4,847.3m).
**Effect.** Without it, 75 filings are admitted instead of 79 (27.0% to 25.1% of dollars).
**Test.** `test_rule_jv_subsidiary_drops_jv_portfolio_rows`.

### 2. `rule_jv_schedule_style`: JV rows with no subsidiary axis (PennantPark)
**Artifact.** PennantPark lists the loans of its JV, PennantPark Senior Loan Fund (PSSL), with no
subsidiary member, so rule 1 cannot see them. The two schedules use different identifier styles:
PennantPark's own holdings start "Investments in ..."; the PSSL rows start with the instrument
type and then "Issuer Name" (for example "Equity Securities Issuer Name Wash & Wax Group, LP - ...").
We first tried to separate them with the PRE table, as Part 1 suggested. That does not work:
in 0001193125-26-021227 the tag `InvestmentOwnedAtFairValue` appears in 10 reports, and NUM
facts do not record which report they belong to.
**Example.** PennantPark Investment 10-K/A 0001193125-26-021227, soi_row 160;161.
**Rows affected.** 415 holdings in 3 filings, all PennantPark; no other filer matches the pattern.
In 0001193125-26-021227, 117 rows ($1,265.9m), the same 117 Part 1 found against the filing.
**Effect.** Without it, 77 filings are admitted instead of 79. PennantPark Investment's 10-Q
(0001193125-26-042780) improves from +141.5% to +30.1% but is still not admitted (Part 3 triage).
**Not yet verified.** The 171 rows in 0001193125-26-042778 and 127 in 0001193125-26-042780 match
by pattern and reconciliation, not yet by a check against those filings.
**Test.** `test_rule_jv_schedule_style_drops_pssl_rows_not_own_holdings` (keeps PennantPark's own
"Investments in ... Issuer Name AKW Holdings Limited" holding).

### 3. `rule_range_axis`: range bounds
**Artifact.** Rows on `Range Axis` (Minimum, Maximum, Weighted Average) are ranges of valuation
inputs, not holdings.
**Example.** New Mountain Finance 0001496099-26-000008, soi_row 13343: "First Lien Investments"
on `Weighted Average`. Log example: 0001628280-26-011734, soi_row 72803.
**Rows affected.** 530 holdings (534 before earlier rules; 14 filings).
**Effect.** No change in coverage (79 filings, 27.0% either way). The rule exists because these
rows are not holdings, not to make any filing reconcile; its evidence is the test.
**Test.** `test_rule_range_axis_drops_range_bounds`.

### 4. `rule_category_member`: category members used as identifiers
**Artifact.** Three filers use XBRL members as identifiers. Some are categories, which are
subtotals: "First Lien Secured Debt [Member]" carries $1,203.4m in Lord Abbett Private Credit Fund.
Others are real borrowers: "Accel International Holdings, Inc. (Revolver) [Member]" (Lord Abbett
Private Credit Fund S, soi_row 92537). Dropping every "[Member]" identifier would remove 54
borrowers, so the rule drops only category members (lien, equity, joint venture, affiliation words).
**Example.** Lord Abbett Private Credit Fund S 0000930413-26-000842, soi_row 76694 (and 20 more
rows of the same holding): "First Lien - Secured Debt [Member]". This was the 1 conflict left
after Part 1.
**Rows affected.** 12 holdings (of 66 member identifiers) in 3 filings.
**Effect.** No change in coverage. Evidence: the test.
**Test.** `test_rule_category_member_drops_categories_not_borrowers`.

### 5. `rule_totals_v2`: totals and subtotals, sparing borrowers named "Total ..."
**Artifact.** Total and subtotal rows sit beside holdings. The kit's `rule_totals` drops any
identifier starting with "Total", which also drops real borrowers: 12 holdings in 4 filings
($50.3m), for example Gladstone 0001143513-26-000004 "Total Access Elevator, LLC Term Debt"
(soi_row 64141, $17,500,000) and TriplePoint "Total Expert Inc. | Growth Capital Loan 2"
(soi_row 161016). Our rule keeps the kit's pattern but spares "Total <name>, LLC / Inc. / Ltd ..."
and any row with a spread or maturity (MidCap Apollo's PAI Pharma revolver, soi_row 150389).
**Example.** Saratoga 0001213900-26-002153, soi_row 2816: "Total cash and cash equivalents".
**Rows affected.** 31 holdings (the kit's rule: 45).
**Effect.** Without it, 78 filings are admitted instead of 79 (TriplePoint Venture Growth).
**Test.** `test_rule_totals_v2_keeps_borrowers_named_total`.

### 6. `rule_cash` (kit rule, kept)
**Artifact.** Cash and money-market lines in the schedule. Part 1 found Andalusian Credit
(0001104659-26-027134) reports "Total investments and cash and cash equivalents" while its filed
total ($316,015k) excludes cash.
**Example.** Saratoga 0001213900-26-002153, soi_row 2826.
**Rows affected.** 34 holdings.
**Effect.** Without it, filings admitted stay at 79 but dollar coverage falls from 27.0% to 24.5%.
Whether a filed total includes cash varies by filer; filings where it does would show a negative
gap and are triaged in Part 3.

## Investigated, no rule

| Artifact | What we found (current period) | Why no rule |
|---|---|---|
| Comparative-period rows | 76,622 prior year-end rows in 159 filings | `holdings.split_periods` keeps only `ddate == period` |
| Restated copies | 7,881 holdings built from 2+ rows that agree; 1 that disagreed (rule 4) | `coalesce_holdings` merges them into one holding |
| Subtotals with no identifier | 13,597 rows with a type, industry or affiliation axis, in 169 filings | Rows with no identifier never become holdings |
| Holdings on a custom axis | 4,814 rows with a fair value, no identifier and no category axis, in 158 filings | The SOI drops the identifier; it cannot be recovered. Their summed fair value ($2.27 trillion) shows most are totals. Shortfalls are triaged in Part 3 |
| Values on custom tags | 5,178 holdings with no fair value in SOI, in 124 filings | Recovering them from NUM is a stretch goal |
| Unfunded commitments | 5,431 holdings with negative fair value (-$409.8m, 109 filings); 6,302 at exactly 0 | They are in the schedule, so they stay in the sum; filers that net differently are triaged in Part 3 |
| Affiliate and control | 0 holdings carry an affiliation; in this release the type,
