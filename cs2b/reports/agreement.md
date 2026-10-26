# Part 1 agreement report: parsed holdings vs the filings

## Method

EdgarTools was not used. Following the case study's alternative, we compared our parsed
holdings with the human-readable schedule of investments for three filings.

- **Parsed holdings**: the starter kit's pipeline with our Part 1 changes (verified column
  aliases for fair value and cost; holding key extended with the Nonconsolidated Subsidiary
  and Range axes), current period only, before any Part 2 cleaning rule.
- **Filed total**: the undimensioned `InvestmentOwnedAtFairValue` fact in NUM at the period end.
- **Schedule**: the filing's own schedule of investments, opened on EDGAR. Amounts in the
  filings are in thousands.
- SOI row numbers are the kit's `soi_row`: the 0-based data row in `data/raw/2026q1_bdc/soi.tsv`
  (row 0 is the first line after the header). Each merged row also carries `source_release` and
  `source_soi_row`, which point back to the row in the SEC's original monthly `soi.tsv`.

The three filings were chosen to cover three different situations: a clean filer, a filer
whose joint-venture holdings are tagged on the Nonconsolidated Subsidiary axis, and a filer
whose joint-venture holdings are not.

## Totals per filing

| Filing | adsh | Holdings parsed | Parsed fair value | Schedule total | Filed total (NUM) | Gap | Status |
|---|---|---:|---:|---:|---:|---:|---|
| Andalusian Credit Company, LLC | 0001104659-26-027134 | 52 | $316,015k | $316,015k | $316,015k | +0.00% | Agrees |
| Oaktree Specialty Lending Corp | 0001414932-26-000005 | 382 own (608 total) | $2,978,084k | $2,949,092k | $2,949,092k | +0.98% | Agrees once JV rows are separated |
| PennantPark Investment Corp | 0001193125-26-021227 | 482 own (599 total) | $1,287,273k | $1,287,273k | $1,287,273k | +0.00% | Agrees once JV rows are separated |

## Differences explained

**Andalusian.** The schedule's final line is "Total investments and cash and cash equivalents".
Subtracting the cash line gives $316,015k, equal to our total and to the filed total. This filer's
filed total excludes cash.

**Oaktree.** 226 of the 608 parsed holdings are joint-venture or valuation-range rows: the
portfolios of OCSI Glick JV LLC and SLF JV I ($510,672k on the Nonconsolidated Subsidiary axis),
which the 10-K lists in separate schedules. Oaktree's own stake in the JV appears as its own
holding (Senior Loan Fund JV I, LLC, Subordinated Debt, $112,656k, SOI row 60507), so counting
the JV's loans as well would double count. Including them would put the gap near +18%. The
remaining +0.98% ($28,992k) is within the 1% tolerance and is left for Part 2 and Part 3 to
explain.

**PennantPark.** The SOI carries 117 holdings ($1,265.9m) that belong to its joint venture,
PennantPark Senior Loan Fund (PSSL), whose schedule appears in the 10-K's notes. Unlike Oaktree,
these rows carry no Nonconsolidated Subsidiary member, so the extended key cannot separate them.
They are identifiable only by identifier style: PennantPark's own holdings begin with
"Investments in ...", the PSSL rows do not. Including them doubles the total (+98.34%).
PennantPark's stake in PSSL appears as its own holding (Subordinated Debt, PennantPark Senior
Loan Fund, $140,287k, SOI rows 528;529). 50 of the 117 PSSL borrowers also appear in
PennantPark's own schedule. Separating these rows is a Part 2 cleaning decision.

## Field-level checks

| Filing | Holding | SOI rows | Field | Parsed | Filing | Match |
|---|---|---|---|---:|---:|---|
| Andalusian | Vivos Holdings, LLC, First Lien Term Loan | 165226;165227 | Fair value | 31,309 | 31,309 | Yes |
| Andalusian | Vivos Holdings, LLC, First Lien Term Loan | 165226;165227 | Principal | 31,867 | 31,867 | Yes |
| Oaktree | Aurelia Netherlands B.V., First Lien Term Loan | 17138 | Fair value | 56,000 | 56,000 | Yes |
| Oaktree | Aurelia Netherlands B.V., First Lien Term Loan | 17138 | Principal | 47,682 | 47,682 | Yes [CONFIRM: is the principal in a foreign currency?] |
| Oaktree | Senior Loan Fund JV I, LLC, Subordinated Debt | 60507 | Fair value | 112,656 | 112,656 | Yes |
| PennantPark | PennantPark Senior Loan Fund, Subordinated Debt | 528;529 | Fair value | 140,287 | 140,287 | Yes |
| PennantPark | Blackhawk Industrial Distribution, Inc., First Lien | 218;219 | Fair value | 24,802 | 24,802 | Yes [CONFIRM: found in the PSSL schedule in the notes?] |

(Amounts in thousands.)

## Findings carried into Parts 2 and 3

1. **Joint-venture portfolios** appear in the SOI for at least 23 filings on the Nonconsolidated
   Subsidiary axis (1,293 current rows), and for PennantPark without it. They should not count
   toward the BDC's own total.
2. **Cash lines**: Andalusian's filed total excludes cash; other filers may differ.
3. **Identifier quirk**: 14 PennantPark identifiers begin "nvestments in" (missing the "I"), as
   filed in the SOI.