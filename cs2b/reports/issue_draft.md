# Draft issue: SOI value columns appear under headers that are not in the release's TAG table

**To:** SEC Division of Economic and Risk Analysis (DERA), BDC data sets
**Status:** draft. Not to be sent until Case Study 2B grades are returned.
**Data sets:** BDC data sets `2026_01_bdc.zip`, `2026_02_bdc.zip`, `2026_03_bdc.zip`
(SHA-256 in `data/manifest.json`).

## Summary

In all three releases, every fair value and every cost in `soi.tsv` sits under a column headed
`Initial fair value of Investment` or `Adjusted cost basis`. Neither header appears as a label in
the release's own `tag.tsv`. The columns headed with the labels that `tag.tsv` does give for these
tags, `Investment Owned, Fair Value` and `Investment Owned, Cost`, exist but are empty in every row.
A user who maps SOI column headers to tags through TAG, as the readme describes, finds no fair
value or cost for any holding.

## What the readme says

`readme.htm` (included in each release) describes the SOI report as having "the tag labels pivoted
as column headings with their values reported", and defines TAG's `tlabel`, for a standard tag, as
"the label text provided by the taxonomy". So a user expects each SOI value column's header to be
the `tlabel` of its tag in `tag.tsv`.

## Evidence

Counts from each release's `soi.tsv` and `tag.tsv` (reproduced by `scripts/bonus_issue_evidence.py`;
output in `reports/issue_evidence.csv`):

| Release | SOI rows | Filled under `Investment Owned, Fair Value` | Filled under `Initial fair value of Investment` | Filled under `Investment Owned, Cost` | Filled under `Adjusted cost basis` |
|---|---:|---:|---:|---:|---:|
| 2026_01 | 2,918 | 0 | 2,242 | 0 | 2,158 |
| 2026_02 | 70,297 | 0 | 58,894 | 0 | 52,475 |
| 2026_03 | 100,761 | 0 | 79,845 | 0 | 70,240 |

In each release, `tag.tsv` lists these tags only with these labels:

| Release | `tag.tsv` entries |
|---|---|
| 2026_01, 2026_02 | `InvestmentOwnedAtFairValue` us-gaap/2025 = "Investment Owned, Fair Value"; `InvestmentOwnedAtCost` us-gaap/2025 = "Investment Owned, Cost" |
| 2026_03 | the same, for us-gaap/2024 and us-gaap/2025 |

Neither `Initial fair value of Investment` nor `Adjusted cost basis` appears as any `tlabel` in
any of the three `tag.tsv` files.

**One row to check by hand.** `2026_03_bdc/soi.tsv`, data row 18822 (0-based; line 18,824 of the
file including the header): Bain Capital Private Credit, adsh `0001193125-26-104390`, identifier
"Aerospace & Defense ATS First Lien Senior Secured Loan SOFR Spread 5.75% Interest Rate 9.65%
Maturity Date 7/12/2029". The value 4,949,000 is under `Initial fair value of Investment`;
`Investment Owned, Fair Value` is empty. In `num.tsv` the same fact is tag
`InvestmentOwnedAtFairValue`, version us-gaap/2025, ddate 20251231, value 4949000.0000. The
filer used the 2025 taxonomy, whose label is "Investment Owned, Fair Value", yet the value is
reported under a different header.

**The values themselves are correct.** Matched against NUM across 171 filings, the values under
`Initial fair value of Investment` agree with `InvestmentOwnedAtFairValue` in 99.67% of rows
(108,631 of 108,992), and those under `Adjusted cost basis` agree with `InvestmentOwnedAtCost` in
99.69% (101,545 of 101,857) (`reports/p1_value_column_check.csv`). Only the headers are affected.

## Impact

Any tool that maps SOI columns through TAG reads every holding's fair value and cost as missing.
In our pipeline, before we added the two headers as aliases (`src/lookthrough/mapping.py`,
`ALIASES`), no filing could be reconciled to its reported total.

## How to reproduce

1. Download and unzip `2026_03_bdc.zip`.
2. In `soi.tsv`, count non-empty values under `Investment Owned, Fair Value` (0) and under
   `Initial fair value of Investment` (79,845).
3. In `datasets/tag.tsv`, search `tlabel` for `Initial fair value of Investment` (no match), and
   look up `InvestmentOwnedAtFairValue` (label "Investment Owned, Fair Value").

## Possible cause (not confirmed)

The headers may come from a newer taxonomy's labels than the ones in the release's `tag.tsv`. We
have not confirmed this.

## Suggested fix

Either head the SOI value columns with the `tlabel` from the release's own `tag.tsv` (so they
match the version each filer used), or include the labels actually used as SOI headers in
`tag.tsv`, so the readme's mapping works.
