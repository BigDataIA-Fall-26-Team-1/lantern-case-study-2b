"""P0: list every row whose field count differs from its header, in every table of every month."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MONTHS = ["2026_01", "2026_02", "2026_03"]
TABLES = ["soi.tsv"] + [f"datasets/{t}.tsv" for t in ("sub", "tag", "num", "txt", "pre", "cal", "non")]

for m in MONTHS:
    for t in TABLES:
        p = RAW / f"{m}_bdc" / t
        if not p.exists():
            continue
        with open(p, encoding="utf-8", newline="") as fh:
            h = fh.readline().rstrip("\r\n").split("\t")
            bad, i = [], 0
            for line in fh:
                line = line.rstrip("\r\n")
                if not line:
                    continue
                f = line.split("\t")
                if len(f) != len(h):
                    bad.append((i, f))
                i += 1
        print(f"{m} {t}: {len(bad)} bad rows of {i:,}")
        for i, f in bad[:2]:
            print(f"   row {i}: {len(f)} fields")
            for name, val in zip(h + ["(extra)"] * (len(f) - len(h)), f):
                print(f"      {name}: {val[:120]!r}")