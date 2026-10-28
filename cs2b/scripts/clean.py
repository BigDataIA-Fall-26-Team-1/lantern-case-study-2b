"""P5 stage 'clean': apply the team rules, in their fixed order, to the current holdings.

The same call as the kit's pipeline.run_baseline, but always with rules.TEAM_RULES (the kit
defaults to its 2 rules). Writes outputs/work/clean/{kept,log}.parquet and is the only writer
of reports/cleaning_log.csv. Run from cs2b/:  python scripts/clean.py
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lookthrough import clean, paths, rules  # noqa: E402
from workio import load_frame, save_frames  # noqa: E402

P = paths.load_params(ROOT)
t0 = time.perf_counter()

h = load_frame(ROOT / "outputs" / "work" / "parse", "holdings")
kept, log = clean.apply_rules(h[h["is_current"]], rules.TEAM_RULES)
print("rules, in order:", [r.__name__ for r in rules.TEAM_RULES])

save_frames({"kept": kept, "log": log}, ROOT / "outputs" / "work" / "clean")
log.to_csv(ROOT / P["outputs"]["reports"] / "cleaning_log.csv", index=False, lineterminator="\n")

print(log.to_string(index=False, max_colwidth=50))
print(f"current holdings {int(h['is_current'].sum()):,} -> kept {len(kept):,}")
print(f"clean done in {time.perf_counter() - t0:.1f} s")