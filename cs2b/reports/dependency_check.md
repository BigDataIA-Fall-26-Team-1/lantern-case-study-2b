# Dependency check (Part 4)

Release 2026q1. We checked holdings in our panel (`outputs/panel/holdings.parquet`, 82 admitted
filings, 31,387 rows) against the human-readable schedule of investments in each filing.
Results, row by row: `reports/spot_check.csv`. Checked by hand on 27 October 2026.

## Method

- **Sample** (`scripts/p4a_spot_check_sample.py`): notebook 07's method, unchanged. The 5 largest
  filings by fair value plus 5 more at random (`random_state=7`); from each, the largest holding and
  one more at random. **20 holdings across 10 filings**, the brief's minimum.
- **Comparison:** for each holding we opened the filing (plain document URL, not the Inline XBRL
  viewer), found the line in the current-period schedule (December 31, 2025), and compared fair
  value and principal, in the filing's own units. Results are recorded by
  `scripts/p4b_fill_spot_check.py`.
- **EdgarTools:** not used. The brief makes it optional and asks us to pin the version the
  instructor announces; no version was announced, so we did not install it.

## Result

| Outcome | Holdings | Checks |
|---|---:|---|
| Fair value and principal match the filing | 18 | S01, S03 to S19 |
| Not a holding (commitment disclosure in the panel) | 2 | S02, S20 |
| Disagreement in value | 0 | |

The 18 matches span three unit conventions: thousands (most filers), thousands to one decimal
(Ares Strategic Income, 0001918712-26-000018) and millions to one decimal (Ares Capital,
0001287750-26-000006). They include equity with no principal (S01, S04), a below-par loan (S07),
an undrawn revolver marked at a small negative value (S16: fair value (2), par "-"), and a warrant
the filing reports with no cost or value (S14: "—", matching the panel's empty values).

**We found no case where the SOI data set reports a different fair value or principal from the
filing.** The two findings below are about what our parse treats as a holding, and about how the
SOI writes identifiers.

## Finding 1: commitment disclosures become panel rows

Two sampled rows are not holdings. In both, the company's real lines are separate panel rows that
match the filing.

- **S02, Ares Capital 0001287750-26-000006, soi_row 58925**, "Repairify, Inc. and Repairify
  Holdings, LLC". The row has no fair value, cost or principal. In the SOI it carries only
  `Investment Company, Financial Support to Investee Contractually Required, Amount` (7,300,000)
  and `..., Not Provided, Amount` (2,200,000). The filing's three Repairify lines (revolver 5.1,
  first lien 5.0, Class A units 2.7; company subtotal 12.8, in millions) match panel rows 58923,
  58921 and 58920.
- **S20, North Haven Private Income Fund A 0001193125-26-088351, soi_row 120878**, "Granicus, Inc.
  Commitment Type Delayed Draw Term Loan Commitment Expiration Date 07/31/2026". The filing lists
  this in its unfunded-commitments table (unfunded commitment 398, fair value "—"), not among the
  holdings. In the SOI the row carries fair value 0 and `..., Not Provided, Amount` 398,000.
  Granicus's three schedule lines are panel rows 133425 to 133427.

**Cause.** Coalescing turns every row with an identifier into a holding. Rows that carry only
commitment facts therefore become holdings with no value or a zero value.

**Effect.** No total changes (an empty or zero value adds nothing), so reconciliation is
unaffected. Holding counts are inflated. 2,085 of the panel's 31,387 rows (6.6%), in 49 of 82
filings, have no fair value, cost or principal. We traced one of them (S02). The count does not
include commitment rows that carry a fair value of 0, such as S20, so it is neither a full count of
commitment rows nor a count only of them.

**Possible fix (not applied).** Drop rows whose only facts are
`Investment Company, Financial Support to Investee ...`, or whose identifier contains
"Commitment Type". This would need a rule, a test and a cleaning-log entry (Part 2's contract).

## Finding 2: how the SOI writes identifiers

These are not errors, but anyone matching SOI rows to a filing needs to know them.

- **Trailing numbers count repeated lines.** "Qualus Power Services Corp. 4" (S08) is the fourth of
  four Qualus lines in Blackstone Secured Lending's schedule; "Signia Aerospace, LLC, Senior
  secured 1" (S10), "Anaplan, Inc. | One stop 1" (S11) and "Celerion Buyer, Inc. | One stop 3"
  (S12, the third of four lines, counting an unfunded one) follow the same pattern. The number does
  not appear in the filing.
- **Header text is joined onto the company name.** Apollo Debt Solutions' identifiers start with
  the industry and group header lines ("Aerospace & Defense MRO Holdings MRO Holdings, Inc. ...",
  S03).
- **Units differ by filer** (above), so a check must read each schedule's unit note.

## Other evidence from the filings

- **PennantPark Floating Rate (0001193125-26-042778)**, checked in Part 2: the SOI identifier for
  PennantPark Senior Secured Loan Fund II's first lien gives "Maturity 11/18/2025", while the
  filing's schedule shows acquisition 11/18/2025 and maturity 08/08/2032. The amounts match
  (39,375). This is a difference between the identifier text and the filing; we cannot tell from
  the data set whether it comes from the filer's tagging.
- **Data-set issue already documented:** the SOI headers for fair value and cost do not appear in
  the release's TAG table (`reports/issue_draft.md`).

## Conclusion

For the 18 holdings we checked, the panel's fair value and principal agree with the filings. We
rely on the panel's values for reconciliation and coverage. We do not rely on its holding counts
without first removing commitment rows (Finding 1).

## Reproduce

From `cs2b/`:

    python scripts/p4a_spot_check_sample.py    # draws the same 20 holdings, writes reports/spot_check.csv
    python scripts/p4b_fill_spot_check.py      # writes the recorded filing values into it
