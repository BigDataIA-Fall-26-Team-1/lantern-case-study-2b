# Unit economics (Part 5)

Release 2026q1 (2026_01 + 2026_02 + 2026_03, mostly fiscal-2025 10-Ks). All runtimes were measured with
`dvc repro` (all 5 stages forced) on one laptop: Windows, Python 3.14, Intel Core 7 150U, 16 GB RAM. Every
assumption is stated in the table below it; change it there and the arithmetic follows.

## The five lines

| Line | Value |
|---|---|
| **Cost per completed task** | **$0.0000083 of compute per filing** ($0.0014 for the whole release; 51 s at $0.10/hour, 171 filings). No model is used, so there is no model cost. Storage: about 1.1 GB on S3 (raw release 1.0 GB + pipeline outputs 0.1 GB), about $0.03 per month. |
| **Latency** | **51 s for the release, 0.30 s per filing** (171 attempted). By stage: acquire 26 s (re-verifies the manifest and every value of the merge), parse 8 s, clean 1 s, reconcile and report about 16 s. On a clone with `dvc pull`, `dvc repro` reuses every stage (`dvc.lock`), so the rebuild check takes seconds. |
| **Human time replaced** | For the 82 admitted filings, which no longer need reconciling by hand: **×0.5: 82 h ($9,840) · ×1: 164 h ($19,680) · ×2: 328 h ($39,360)**. The 89 excluded filings are not counted as replaced: each still needs an analyst, but starts from its triage evidence in `reports/triage.md`. |
| **Quality** | Coverage: **82 of 171 filings (48.0%), $204.9bn of $538.9bn filed fair value (38.0%)**; 5 filings in SUB have no SOI rows and are reported separately. Agreement with the filings (Part 4): 18 of 18 checked holdings match on fair value and principal; 2 further sampled rows were commitment disclosures, not holdings; 0 value disagreements (`reports/dependency_check.md`). Self-check 10/10; 25 tests. Breaking each of the 7 rules in `TEAM_RULES` (the 6 team rules and the kit's `rule_cash`) and each Part 1 fix (ALIASES, extended KEY) fails at least one test (`reports/tests_that_fail.md`). |
| **Scale** | Every quarter since Q4 2022: **16 quarters, at most about 2,700 filings: about 14 minutes and $0.02 of compute, at most about 18 GB on S3 (about $0.40 per month)**. Both are upper bounds: early quarters likely had fewer BDCs, and a quarterly release stores no monthly copies (2026q1 stores both). Human time replaced at ×1, if coverage held: 16 × 164 h = about 2,600 h. The real cost of scale is engineering, not compute: about 4–8 hours per new release to review new artifacts and triage (64–128 h for 16 quarters). |

## Assumptions

| Assumption | Value | Basis |
|---|---|---|
| Compute price | $0.10 per hour | A laptop or a small cloud VM (the starter kit's notebook 08 example) |
| Analyst time to reconcile one BDC filing by hand | 2 h (×0.5 = 1 h, ×2 = 4 h) | Our admitted filings average about 383 holdings each (31,387 panel rows ÷ 82 filings): copy the schedule, sum it, and explain the gap to the filed total. Small BDCs take less; the largest (Blackstone Private Credit, 0001803498-26-000014, 2,005 holdings) take far more |
| Analyst cost | $120 per hour, fully loaded | The starter kit's example rate |
| S3 storage | $0.023 per GB-month | S3 Standard list price |
| Filings per quarter | at most about 171 | Our release. BDCs file every quarter (three 10-Qs and one 10-K a year); early quarters (2022–23) likely had fewer BDCs, so 171 is an upper bound |
| Engineering per new release | 4–8 h | Our estimate: new artifacts, new triage cases, rerun and check. Not measured |
| Release format | Quarterly releases through 2025q4, monthly files from 2026 | Case Study §4 lists 2025q4 and 2025q3 as releases; Tool Tutorial slide 8: the 2025 files are consolidated into quarters. Each 2026 quarter is merged from its 3 monthly files with `scripts/merge_release.py`, as for 2026q1 |

**Caveat on scale.** The rules were built on 2026q1. Other quarters are mostly 10-Qs, with comparative
schedules and possibly new artifacts, so their coverage is unknown until the pipeline runs on them
(Case Study stretch goal: a second release). The compute and storage figures scale linearly; the coverage
and the human time replaced may not.

## Build versus buy

The starter kit saved us the base of the pipeline: chunked loading of the SEC files, mapping SOI columns by
XBRL tag, splitting current from comparative schedules, coalescing rows into holdings, reconciling to the
filed total, the report writers, the self-check that grades like the grader, and a synthetic fixture with
tests. We did not use EdgarTools: the brief makes it optional with a pinned version, and none was announced
(Part 4); it also reconciles one filing at a time, not the bulk data set. What we still had to build was
specific to our release and to trusting it: merging three monthly files into one quarter with proof that no
value changed (Part 0); aliases for the renamed fair-value and cost columns and a holding key that keeps
joint-venture and range rows apart (Part 1); six cleaning rules, each with an artifact, an example and a
test that fails without it (Parts 2 and 3); evidence-based triage of all 89 excluded filings (Part 3); hand
checks against the filings (Part 4); and a pipeline that rebuilds byte-identical results on Windows and on
Linux (Docker `python:3.11-slim`, `dvc repro -f`) (Part 5). A vendor look-through feed could replace the
build, but not the verification: Tom will act only on a number he can trace to the filing, and Lina wants
proof before relying on any source. That verification, not the compute, is where the cost is.