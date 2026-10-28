# Tests that fail

A test is evidence only if it can fail. For each team cleaning rule and each Part 1 parsing fix, `scripts/p5_tests_that_fail.py` breaks the code on purpose, runs `python tests/run_tests.py`, records which tests fail, and restores the code. Before and after: 25/25 tests pass.

| Item | File | Break | Failing tests | Own test fails |
|---|---|---|---|---|
| rule_jv_subsidiary | `src/lookthrough/rules.py` | `return (h["subsidiary"].notna(),` → `return (h["subsidiary"].isna() & False,` | `test_rule_jv_subsidiary_drops_jv_portfolio_rows` (24/25 tests pass) | yes |
| rule_jv_schedule_style | `src/lookthrough/rules.py` | `return (h["identifier"].str.contains(JV_SCHEDULE,` → `return (~h["identifier"].str.contains(JV_SCHEDULE,` | `test_rule_jv_schedule_style_drops_pssl_rows_not_own_holdings` (24/25 tests pass) | yes |
| rule_range_axis | `src/lookthrough/rules.py` | `return (h["range"].notna(),` → `return (h["range"].isna() & False,` | `test_rule_range_axis_drops_range_bounds` (24/25 tests pass) | yes |
| rule_category_member | `src/lookthrough/rules.py` | `return (member & category,` → `return (member,` | `test_rule_category_member_drops_categories_not_borrowers` (24/25 tests pass) | yes |
| rule_totals_v2 | `src/lookthrough/rules.py` | `return (total & ~borrower & ~has_terms,` → `return (total,` | `test_rule_totals_v2_keeps_borrowers_named_total` (24/25 tests pass) | yes |
| rule_issuer_subtotals | `src/lookthrough/rules.py` | `if c >= 2 and fv[i]` → `if c >= 99 and fv[i]` | `test_rule_issuer_subtotals_drops_subtotal_only` (24/25 tests pass) | yes |
| rule_cash (kit rule, in TEAM_RULES) | `src/lookthrough/clean.py` | `CASH = r"cash and cash equivalents|money market"` → `CASH = r"(?!x)x"` | `test_baseline_reconciliation_counts_every_filing`<br>`test_checker_catches_a_silently_dropped_filing`<br>`test_checker_passes_baseline_and_catches_tampering` (22/25 tests pass) | n/a |
| Part 1: ALIASES (renamed fair value / cost columns) | `src/lookthrough/mapping.py` | `| {PRESET[field]} | ALIASES.get(field, set())` → `| {PRESET[field]}` | `test_renamed_soi_value_columns_map_by_alias` (24/25 tests pass) | yes |
| Part 1: extended holding KEY (subsidiary, range) | `src/lookthrough/holdings.py` | `KEY = ["adsh", "ddate", "identifier", "subsidiary", "range"]` → `KEY = ["adsh", "ddate", "identifier"]` | `test_holding_key_keeps_jv_and_range_rows_apart` (24/25 tests pass) | n/a |

Breaking a rule's function is what fails its test, because each team-rule test calls the function directly. Removing a rule from `rules.TEAM_RULES` instead fails no unit test, but it changes coverage: that effect is measured in `reports/p2_rule_ablation.csv` (`scripts/p2b_measure_rules.py`).
