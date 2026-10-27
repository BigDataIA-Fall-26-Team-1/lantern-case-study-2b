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
**Artifact.** PennantPark lists the loans of its JV, its joint ventures (PennantPark Senior Secured Loan Fund, PSSL, for PFLT; PennantPark Senior Loan Fund, PSLF, for PNNT), with no
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
**Verified against the filings (26 Oct 2026).** In both 10-Qs the dropped rows sit in the JV listing
in the notes, not in the BDC's own schedule, and the BDC's stake appears in its own schedule:
- PennantPark Floating Rate 0001193125-26-042778 (JV: PennantPark Senior Secured Loan Fund, PSSL):
  Beacon Behavioral Support Services (FV 24,965), GGG MIDCO (24,511) and NORA Acquisition (20,375)
  are in "listing of PSSL's individual investments as of December 31, 2025"; PFLT's own schedule
  holds PSSL Fund I first lien 237,650 and common equity 72,690, and Fund II first lien 39,375 and
  common equity 16,857. The schedule's Total Investments, $2,605,347k, equals the filed total in NUM.
- PennantPark Investment 0001193125-26-042780 (JV: PennantPark Senior Loan Fund, PSLF): Sigma
  Defense Systems (26,563), Blackhawk Industrial Distribution (24,675) and Beacon Behavioral Support
  Services (24,545) are in "listing of PSLF's individual investments as of December 31, 2025". The
  note's PSLF summary gives total investments of $1,357,342k, equal to the $1,357.3m this rule drops
  from the filing. PNNT's own schedule holds PSLF subordinated debt 140,287 and common equity 59,767.
- The same borrowers also appear in each BDC's own schedule at different, smaller amounts (for
  example PNNT's own Sigma Defense Systems line: par 11,599, FV 11,483), so these are distinct lines.
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


### rule_issuer_subtotals (added in Part 3)

**Artifact:** some filers tag a company-level subtotal row with an identifier, so it looks like a
holding and the company is counted twice. Found in Part 3 triage: in Ares Capital
(0001287750-26-000006), 21 such rows ($4,479m) closed the $4,614m gap to within 1%; Ares Strategic
Income (0001918712-26-000018) showed the same pattern. `rule_totals_v2` misses them because they never
say "Total". **Rule:** drop a holding when at least 2 other holdings' identifiers extend its name and
its fair value equals their sum within 0.5%; the sum guard keeps real borrowers whose names happen to
prefix others. **Rows affected:** 184 holdings across the release. **Example:** 0001287750-26-000006 / soi_row 14469
(Ares Capital). **Effect:** Ares Capital and Ares Strategic Income admitted; dollar coverage 27.0% to
38.0% (filings 79 to 82). **Test:** `test_rule_issuer_subtotals_drops_subtotal_only`.