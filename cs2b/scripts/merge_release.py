"""P0: merge the 3 monthly BDC releases (2026_01, 2026_02, 2026_03) into data/raw/2026q1_bdc.

Evidence for each rule: output of scripts/inspect_months.py (25 Oct 2026).
1. Concat every table by column NAME, not position: SOI has 47, 153 and 223 columns in the 3 months.
2. Dedupe by adsh: an adsh found in more than one month keeps only its latest month's rows
   (0 found; kept as a guard).
3. Latest filing per cik + period: among filings not already prevrpt=1, all but the latest
   'accepted' get prevrpt=1, so load.load_sub drops them (0 extra found; the 2 amendments
   in 2026_03, North Haven and Rand, are already prevrpt=1 from the SEC).
4. Provenance: sub and soi get source_release; soi also gets source_soi_row
   (0-based data row in that month's soi.tsv).
   Rows are copied field by field, never converted. Quoted fields are read and written the way
   pandas reads them: a quoted value may contain a tab (3 rows in 2026_03 num.tsv, e.g.
   0001487918-26-000021, data row 324799). Every row's field count is still checked.
Required in every month: soi.tsv, datasets/sub.tsv, tag.tsv, num.tsv (the kit reads all four).
Optional (skipped and logged if missing): datasets/txt, pre, cal, non; readme.htm; bdc_metadata.json.
Run from cs2b/:  python scripts/merge_release.py
"""
import csv
import json
import shutil
from pathlib import Path

csv.field_size_limit(2**31 - 1)                     # long text facts (txt.tsv) exceed the default limit

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MONTHS = ["2026_01", "2026_02", "2026_03"]          # date order: later months win
OUT = RAW / "2026q1_bdc"
REQUIRED = {"soi.tsv", "datasets/sub.tsv", "datasets/tag.tsv", "datasets/num.tsv"}
OTHER = ["soi.tsv"] + [f"datasets/{t}.tsv" for t in ("tag", "num", "txt", "pre", "cal", "non")]
EXTRAS = ["readme.htm", "bdc_metadata.json"]


def header_of(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return next(csv.reader(fh, delimiter="\t", quotechar='"'))


def rows_of(path):
    """Yield (data_row_number, fields). Quoted fields are read like pandas does; stop with an
    error if a row still has the wrong field count."""
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t", quotechar='"')
        n = len(next(reader))
        i = 0
        for f in reader:
            if not f:                                   # blank line
                continue
            if len(f) != n:
                raise ValueError(f"{path}: data row {i} has {len(f)} fields, header has {n}")
            yield i, f
            i += 1


def union(headers):
    cols = []
    for h in headers:
        cols += [c for c in h if c not in cols]
    return cols


def write(path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writerow(cols)
        for r in rows:
            w.writerow(r)
            n += 1
    return n
def present_months(t, log):
    """(month, path) for months that have file t; log the months that do not."""
    have = [(m, RAW / f"{m}_bdc" / t) for m in MONTHS]
    missing = [m for m, p in have if not p.exists()]
    if missing and t in REQUIRED:
        raise FileNotFoundError(f"required file {t} missing in {missing}")
    if missing:
        log["skipped_missing"].append({"file": t, "months": missing})
    return [(m, p) for m, p in have if p.exists()]


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    log = {"months": MONTHS, "tables": {}, "skipped_missing": []}

    # SUB first: it decides which month each filing comes from (rules 2 and 3)
    have = present_months("datasets/sub.tsv", log)
    heads = [header_of(p) for _, p in have]
    cols = union(heads)
    rows = [(m, dict(zip(h, f))) for (m, p), h in zip(have, heads) for _, f in rows_of(p)]
    src = {r["adsh"]: m for m, r in rows}                       # last (latest) month wins
    dup_adsh = sorted({r["adsh"] for m, r in rows if src[r["adsh"]] != m})
    keep = [(m, r) for m, r in rows if src[r["adsh"]] == m]
    groups = {}
    for m, r in keep:
        if r["prevrpt"] != "1":
            groups.setdefault((r["cik"], r["period"]), []).append(r)
    marked = []
    for g in groups.values():
        for r in sorted(g, key=lambda r: r["accepted"])[:-1]:
            r["prevrpt"] = "1"
            marked.append(r["adsh"])
    n = write(OUT / "datasets" / "sub.tsv", cols + ["source_release"],
              ([r.get(c, "") for c in cols] + [m] for m, r in keep))
    log["tables"]["datasets/sub.tsv"] = {"rows_in": len(rows), "rows_out": n, "columns": len(cols) + 1,
                                         "columns_per_month": [len(h) for h in heads]}
    log["adsh_in_more_than_one_month"] = dup_adsh
    log["marked_prevrpt_by_merge"] = marked
    log["filings"] = len(keep)
    log["filings_current"] = sum(r["prevrpt"] != "1" for _, r in keep)

    # every other table: concat by column name; drop rows of an adsh kept from another month
    for t in OTHER:
        have = present_months(t, log)
        if not have:
            continue
        heads = [header_of(p) for _, p in have]
        cols = union(heads)
        extra = ["source_release", "source_soi_row"] if t == "soi.tsv" else []
        stats = {"rows_in": 0, "dropped_other_month": 0, "dropped_exact_duplicate": 0,
                 "months": [m for m, _ in have]}
        seen = set()

        def gen():
            for (m, p), h in zip(have, heads):
                pos = {c: j for j, c in enumerate(h)}
                a = pos.get("adsh")
                for i, f in rows_of(p):
                    stats["rows_in"] += 1
                    if a is not None and src.get(f[a], m) != m:
                        stats["dropped_other_month"] += 1
                        continue
                    out = [f[pos[c]] if c in pos else "" for c in cols]
                    if a is None:                       # e.g. tag.tsv: same tag in several months
                        key = tuple(out)
                        if key in seen:
                            stats["dropped_exact_duplicate"] += 1
                            continue
                        seen.add(key)
                    yield out + ([m, str(i)] if extra else [])

        stats["rows_out"] = write(OUT / t, cols + extra, gen())
        stats["columns"] = len(cols) + len(extra)
        stats["columns_per_month"] = [len(h) for h in heads]
        log["tables"][t] = stats

    # readme / metadata: copy from the latest month that has each file
    for f in EXTRAS:
        have = present_months(f, log)
        if have:
            shutil.copy2(have[-1][1], OUT / f)
            log.setdefault("extras_copied_from", {})[f] = have[-1][0]

    (ROOT / "reports" / "merge_log.json").write_text(json.dumps(log, indent=2))
    for t, s in log["tables"].items():
        print(f"  {t:20s} rows in {s['rows_in']:>9,} -> out {s['rows_out']:>9,} | columns {s['columns']}")
    print(f"filings {log['filings']} (current {log['filings_current']}); adsh in >1 month: {len(dup_adsh)}; "
          f"marked prevrpt by merge: {len(marked)}")
    print("skipped (missing):", log["skipped_missing"] or "none")
    print("wrote", OUT.relative_to(ROOT), "and reports/merge_log.json")


if __name__ == "__main__":
    main()