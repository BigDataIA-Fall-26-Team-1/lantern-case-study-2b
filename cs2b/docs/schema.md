# Canonical holdings schema (Part 1)

Release: `2026q1` (the merged `2026_01`, `2026_02` and `2026_03` releases, see `docs/merge.md`),
read from `data/raw/2026q1_bdc`.

## 1. Loading

- All four tables are read with the kit's `READ` settings: tab-separated, every column as a
  string, empty strings as missing (`dtype=str`, `keep_default_na=False`). Numbers are converted
  deliberately with `pd.to_numeric(errors="coerce")` in `to_canonical`; nothing is type-guessed.
- **Latest version of each filing**: `load_sub` keeps rows with `prevrpt != "1"`. Our release has
  2 amendments (North Haven, Rand); each 10-K/A re-files the full schedule, so no BDC is lost.
  SOI rows are kept only for adsh in the filtered SUB.
- NUM is read in 500,000-row chunks and filtered by tag inside the loop (`load_num`).

## 2. Canonical fields

Every SOI column is mapped through its XBRL tag, never by position. Counts are non-empty rows
across all 173,976 SOI rows (`reports/p1_soi_columns.csv`).

| Field | Source tag or axis | SOI column(s) in our release | Type | Notes |
|---|---|---|---|---|
| fair_value | InvestmentOwnedAtFairValue | `Initial fair value of Investment` (alias); `Investment Owned, Fair Value` (empty) | float, USD | See section 3. 140,981 rows, 172 filings |
| cost | InvestmentOwnedAtCost | `Adjusted cost basis` (alias); `Investment Owned, Cost` (empty) | float, USD | See section 3. 124,873 rows, 170 filings |
| principal | InvestmentOwnedBalancePrincipalAmount | `Investment Owned, Balance, Principal Amount` | float | Maps by TAG label. Empty for equity and warrants |
| interest_rate | InvestmentInterestRate | `Investment Interest Rate` | float, decimal | Maps by TAG label |
| spread | InvestmentBasisSpreadVariableRate | `Investment, Basis Spread, Variable Rate` | float, decimal | Maps by TAG label |
| maturity | InvestmentMaturityDate | `Investment Maturity Date` | date | 42,865 rows, all `yyyy-mm-dd` |
| pik_rate | InvestmentInterestRatePaidInKind | `Investment, Interest Rate, Paid in Kind` | float, decimal | Maps by TAG label |
| pct_net_assets | InvestmentOwnedPercentOfNetAssets | `Investment Owned, Net Assets, Percentage` | float, decimal | Maps by TAG label |
| identifier | Investment, Identifier Axis | `Investment, Identifier Axis` | text | Typed member: free text naming the holding |
| investment_type | Investment Type Axis | `Investment Type Axis` | text | |
| industry | Industry Sector Axis | `Industry Sector Axis` | text | |
| affiliation | Investment, Issuer Affiliation Axis | `Investment, Issuer Affiliation Axis` | text | |
| subsidiary | Investment Company, Nonconsolidated Subsidiary Axis | same | text | **Added in P1.** Part of the holding key, see section 5 |
| range | Range Axis | same | text | **Added in P1.** Part of the holding key, see section 5 |

## 3. Fair value and cost: renamed columns (an SEC data-set issue)

In all three 2026 monthly releases, the preset SOI columns `Investment Owned, Fair Value` and
`Investment Owned, Cost` exist but are **empty in every row**. The values sit in two columns,
`Initial fair value of Investment` and `Adjusted cost basis`, whose headers match no `tlabel`
in TAG, although the SEC readme says every SOI header is a tag label. Mapping by TAG alone
therefore gives zero fair values for every filing.

We verified the columns against NUM before mapping them (`scripts/p1d_verify_all_filings.py`,
`reports/p1_value_column_check.csv`), joining SOI rows to NUM facts on adsh, identifier and date:

| SOI column | Matches tag | Rows equal | Rate |
|---|---|---:|---:|
| Initial fair value of Investment | InvestmentOwnedAtFairValue | 108,631 of 108,992 | 99.67% |
| Adjusted cost basis | InvestmentOwnedAtCost | 101,545 of 101,857 | 99.69% |
| Investment shares | InvestmentOwnedBalanceShares | 12,968 of 12,970 | 99.98% |

The problem is present in the raw monthly files before our merge (`scripts/p1c_verify_value_columns.py`).
The two columns are added as verified aliases in `ALIASES` in `src/lookthrough/mapping.py`;
`test_renamed_soi_value_columns_map_by_alias` fails if they are removed. `Investment shares` is
verified but not mapped: adding it to `CANONICAL` breaks the kit's fixture test, and no Part 1
requirement needs it. It is available for equity and warrants if Part 2 needs it.

## 4. Dates and periods

| Column | Format in our release | Lost by `norm_date` |
|---|---|---:|
| SOI ddate, filed, period | `yyyy-mm-dd` (the readme says `mm/dd/yyyy`) | 0 |
| SOI Investment Maturity Date | `yyyy-mm-dd` | 0 |
| SUB period, filed | `yyyymmdd` | 0 |
| NUM ddate | `yyyymmdd` | 0 |

All dates are normalized to `yyyy-mm-dd` before comparison. `split_periods` marks a row current
when its `ddate` equals the filing's `period` from SUB. Latest filings give 94,508 current rows
and 76,622 comparative rows; every filing with SOI rows has current rows. Comparative rows are
kept, not used, for later case studies.

## 5. Coalescing and conflicts

`coalesce_holdings` merges a holding's rows into one, keeping the first non-empty value per
field, `source_rows` (semicolon-separated `soi_row` numbers), `n_rows` and `n_conflicts` (fields
whose values disagree across the rows).

**With the kit's key** `(adsh, ddate, identifier)`: 63,862 holdings, **458 with conflicts**
(pik_rate 261, principal 171, fair_value 169, cost 169, interest_rate 15, maturity 5,
pct_net_assets 5, industry 1). The fair value conflicts spanned $1,087.1m (max minus min).

**Cause**: 167 of the 169 fair value conflicts merge rows that belong to different joint ventures
on the Nonconsolidated Subsidiary axis; the other 2 differ on the Range Axis. For example,
Oaktree (`0001414932-26-000005`) lists "ADB Companies, LLC, First Lien Term Loan 1" once for
OCSI Glick JV LLC (fair value $417,000, source_soi_row 10655) and once for SLF JV I ($834,000,
source_soi_row 10881). These are different holdings, not conflicting copies. Once these rows are
set aside, every other conflict disappears.

**Resolution**: we add `subsidiary` and `range` to the holding key in
`src/lookthrough/holdings.py`, so these rows stay separate instead of being merged. Result:
**64,568 holdings, 1 conflict**. Whether these rows belong in the BDC's own total is a Part 2
decision; the agreement report (`reports/agreement.md`) shows they should not.

**The remaining conflict** is in Lord Abbett Private Credit Fund S (`0000930413-26-000842`,
source_soi_row 3479, 3776, ...): the identifier is a category member,
"First Lien - Secured Debt [Member]", with no values at all, so it is not a holding and has no
dollar impact. Left for the Part 2 rules.

## 6. Columns not mapped, and why

| Columns | Decision |
|---|---|
| `qtrs`, `filed` | Metadata. `qtrs` was added by the SEC in 2026 |
| Interest rate floor, cash interest rate, acquisition date, variable-rate type | Optional; not needed for reconciliation |
| `InvestmentCompanyFinancialCommitmentToInvesteeFutureAmount` (unfunded commitments, 30 filings) | Not mapped. Relevant to Part 2 and 3 netting |
| Fair Value Hierarchy, Financial Instrument, Legal Entity, Geographical, Valuation Approach and other axes | Not mapped. Possible sources of split or breakdown rows for Part 2 |
| `... [Extensible Enumeration]` columns for type, industry, issuer name and affiliation (5 to 14 filings) | Not mapped. Some filers report these here instead of on the axes; a possible fallback for Part 2 |
| `Investment shares` | Verified, not mapped (section 3) |

Full list with row and filing counts: `reports/p1_soi_columns.csv`.

## 7. Filing counts for Part 3

- Current filings in SUB: 176. With SOI rows: 171, so **5 have no SOI rows** (report separately).
- With identified holdings: 169, so **2 have SOI rows but no identified holdings**.
- 22,039 current rows (23%) have no identifier: subtotals, or holdings on a custom axis.