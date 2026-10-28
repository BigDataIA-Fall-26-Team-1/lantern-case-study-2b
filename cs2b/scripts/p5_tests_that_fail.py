"""P5: tests that fail. Break each team rule and each Part 1 fix on purpose, run the tests,
record which tests fail, and restore the code (even if a run crashes).

Writes reports/tests_that_fail.md. Exits 1 if any break fails no test (a missing test).
Not a pipeline stage. Run from cs2b/:  python scripts/p5_tests_that_fail.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (item, file, old text, broken text, its own test or None)
CASES = [
    ("rule_jv_subsidiary", "src/lookthrough/rules.py",
     'return (h["subsidiary"].notna(),', 'return (h["subsidiary"].isna() & False,',
     "test_rule_jv_subsidiary_drops_jv_portfolio_rows"),
    ("rule_jv_schedule_style", "src/lookthrough/rules.py",
     'return (h["identifier"].str.contains(JV_SCHEDULE,', 'return (~h["identifier"].str.contains(JV_SCHEDULE,',
     "test_rule_jv_schedule_style_drops_pssl_rows_not_own_holdings"),
    ("rule_range_axis", "src/lookthrough/rules.py",
     'return (h["range"].notna(),', 'return (h["range"].isna() & False,',
     "test_rule_range_axis_drops_range_bounds"),
    ("rule_category_member", "src/lookthrough/rules.py",
     "return (member & category,", "return (member,",
     "test_rule_category_member_drops_categories_not_borrowers"),
    ("rule_totals_v2", "src/lookthrough/rules.py",
     "return (total & ~borrower & ~has_terms,", "return (total,",
     "test_rule_totals_v2_keeps_borrowers_named_total"),
    ("rule_issuer_subtotals", "src/lookthrough/rules.py",
     "if c >= 2 and fv[i]", "if c >= 99 and fv[i]",
     "test_rule_issuer_subtotals_drops_subtotal_only"),
    ("rule_cash (kit rule, in TEAM_RULES)", "src/lookthrough/clean.py",
     'CASH = r"cash and cash equivalents|money market"', 'CASH = r"(?!x)x"',
     None),
    ("Part 1: ALIASES (renamed fair value / cost columns)", "src/lookthrough/mapping.py",
     "| {PRESET[field]} | ALIASES.get(field, set())", "| {PRESET[field]}",
     "test_renamed_soi_value_columns_map_by_alias"),
    ("Part 1: extended holding KEY (subsidiary, range)", "src/lookthrough/holdings.py",
     'KEY = ["adsh", "ddate", "identifier", "subsidiary", "range"]', 'KEY = ["adsh", "ddate", "identifier"]',
     None),
]


def run_tests():
    r = subprocess.run([sys.executable, "tests/run_tests.py"], cwd=ROOT,
                       capture_output=True, text=True, timeout=900)
    failed = re.findall(r"^\s*FAIL\s+(\S+)", r.stdout, flags=re.M)
    summary = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
    return failed, summary


failed, summary = run_tests()
if failed:
    sys.exit(f"tests must pass before breaking anything: {failed}")
print(f"baseline: {summary}", flush=True)

rows = []
for item, rel, old, new, own in CASES:
    path = ROOT / rel
    original = path.read_bytes()
    text = original.decode("utf-8")
    if text.count(old) != 1:
        sys.exit(f"{item}: expected the text exactly once in {rel}, found {text.count(old)}: {old!r}")
    try:
        path.write_bytes(text.replace(old, new).encode("utf-8"))
        failed, summary = run_tests()
    finally:
        path.write_bytes(original)                     # always restore the exact bytes
    own_ok = "n/a" if own is None else ("yes" if own in failed else "NO")
    rows.append((item, rel, old, new, failed, summary, own_ok))
    print(f"{item}: {len(failed)} failing -> {failed}", flush=True)

failed, summary = run_tests()
if failed:
    sys.exit(f"tests fail after restoring the code: {failed}")
print(f"restored: {summary}", flush=True)

md = ["# Tests that fail", "",
      "A test is evidence only if it can fail. For each team cleaning rule and each Part 1 parsing fix, "
      "`scripts/p5_tests_that_fail.py` breaks the code on purpose, runs `python tests/run_tests.py`, "
      "records which tests fail, and restores the code. "
      f"Before and after: {summary}.", "",
      "| Item | File | Break | Failing tests | Own test fails |", "|---|---|---|---|---|"]
for item, rel, old, new, failed_t, summ, own_ok in rows:
    tests = "<br>".join(f"`{t}`" for t in failed_t) or "**none**"
    md.append(f"| {item} | `{rel}` | `{old}` → `{new}` | {tests} ({summ}) | {own_ok} |")
md += ["", "Breaking a rule's function is what fails its test, because each team-rule test calls the "
       "function directly. Removing a rule from `rules.TEAM_RULES` instead fails no unit test, but it "
       "changes coverage: that effect is measured in `reports/p2_rule_ablation.csv` "
       "(`scripts/p2b_measure_rules.py`)."]
(ROOT / "reports" / "tests_that_fail.md").write_text("\n".join(md) + "\n", newline="\n")
print("wrote reports/tests_that_fail.md")

missing = [r[0] for r in rows if not r[4]]
if missing:
    sys.exit(f"no test fails for: {missing} -> add a test")