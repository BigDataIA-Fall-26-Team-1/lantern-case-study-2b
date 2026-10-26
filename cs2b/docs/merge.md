# Merging the 2026q1 release (P0)

Team 1's release is the quarter 2026q1. The SEC publishes 2026 releases monthly, so we merge three
monthly ZIPs into one folder, `data/raw/2026q1_bdc`, and set `release: "2026q1"` in `params.yaml`.
One folder means `paths.release_dir`, the notebooks, `check.py` and the grader work unchanged.

| Month | Filings in SUB | Forms | Periods | SOI rows | SOI columns |
|---|---:|---|---|---:|---:|
| 2026_01 | 2 | 1 10-K/A, 1 10-Q | 2025-09-30, 2025-11-30 | 2,918 | 47 |
| 2026_02 | 53 | 33 10-K, 20 10-Q | 2025-12-31 | 70,297 | 153 |
| 2026_03 | 123 | 121 10-K, 2 10-K/A | 2025-12-31 | 100,761 | 223 |
| **2026q1** | **178 (176 current)** | | | **173,976** | **258** |

Source URLs, sizes and SHA-256 hashes of the three ZIPs: `data/manifest.json`.

## Evidence (scripts/inspect_months.py)

| Finding | Effect on the merge |
|---|---|
| SOI has 47, 153 and 223 columns in the three months | Concatenate every table by column name, never by position |
| 0 accession numbers (adsh) appear in more than one month | Rule 2 changes nothing today; kept as a guard |
| 2 cik + period pairs have two filings: North Haven (0001193125-26-088367 → 10-K/A 0001193125-26-096532) and Rand (0001193125-26-092669 → 10-K/A 0001193125-26-133767); both originals are already prevrpt=1 in the SEC's SUB | Rule 3 changes nothing today; `load.load_sub` drops the originals |
| Each 10-K/A carries a full schedule: North Haven 2,353 SOI rows (same as its original), Rand 493 (same) | Dropping the originals loses no BDC |
| 3 rows in 2026_03 `num.tsv` have a quoted `segments` value containing a tab, e.g. 0001487918-26-000021 (data row 324799) and 0001628280-26-020991 (data row 366246) | Read and write quoted fields the way pandas does (Python `csv`, tab, `"`); every row's field count is checked |

## Merge rules (scripts/merge_release.py)

1. **Concatenate by column name.** Missing columns in a month are left empty.
2. **Dedupe by adsh.** An adsh in more than one month keeps only its latest month's rows (0 today).
3. **Latest filing per cik + period.** Among filings not already prevrpt=1, all but the latest
   `accepted` get prevrpt=1, so `load_sub` drops them (0 today).

Also: `tag.tsv` (no adsh) drops exact duplicate rows, the same tag listed in several months
(52,387 → 49,841). `readme.htm` and `bdc_metadata.json` are copied from 2026_03.
Required in every month: `soi.tsv`, `sub.tsv`, `tag.tsv`, `num.tsv`; optional files missing in a
month are skipped and listed in `reports/merge_log.json` (none skipped today).

## How the merged files differ from the SEC's

- **SUB:** identical values, plus one column, `source_release`. `prevrpt` would differ only where
  rule 3 sets it to 1: **0 rows today**.
- **SOI:** identical values, plus `source_release` and `source_soi_row` (the 0-based data row in that
  month's `soi.tsv`), so every merged row traces back to the SEC's monthly file.
- **TAG:** exact duplicate rows removed (2,546).
- **NUM, TXT, PRE, CAL, NON:** identical.

`scripts/verify_merge.py` reads each table the way the kit does (pandas, `load.READ`), concatenates
the three months by column name and compares value by value with the merged table: all 8 tables
**SAME**.

## Rebuild

python scripts/inspect_months.py     # evidence
python scripts/merge_release.py      # writes data/raw/2026q1_bdc and reports/merge_log.json
python scripts/verify_merge.py       # must print "merge verified"