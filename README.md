# Case Study 2B: Project LANTERN

DAMG 7245, Fall 2026. **Team 1:** Pranav, Preksha, Pradyumna.

A reconciled holdings panel for the SEC BDC data sets, release **2026q1** (the monthly files 2026_01,
2026_02 and 2026_03, mostly fiscal-2025 10-Ks), built on the LANTERN starter kit in `cs2b/`.

**Demo video :** 

## Results

| Measure | Value |
|---|---:|
| Filings attempted (current, with SOI rows) | 171 |
| Filings admitted (gap within 1%) | **82 (48.0%)** |
| Filed fair value admitted | **$204.9bn of $538.9bn (38.0%)** |
| SUB filings with no SOI rows (reported separately) | 5 |
| Excluded filings triaged, each with evidence | 89 of 89 |
| Self-check (`python -m lookthrough.check`) | 10/10 |
| Tests (`python tests/run_tests.py`) | 25/25 |
| Spot checks against the filings (Part 4) | 18 of 18 holdings match; 2 commitment rows; 0 disagreements |

## Reproduce (graders)

Python 3.11 or later. No AWS keys are needed: `dvc pull` reads the team's public S3 remote.
Run everything from `cs2b/`.

**Linux / macOS**

```bash
git clone https://github.com/BigDataIA-Fall-26-Team-1/lantern-case-study-2b.git
cd lantern-case-study-2b && git checkout cs2b-submission && cd cs2b
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
dvc pull                                    # raw release (about 1 GB) and pipeline outputs
dvc repro                                   # every stage reused: "didn't change, skipping"
PYTHONPATH=src python -m lookthrough.check  # 10/10
python tests/run_tests.py                   # 25/25
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/BigDataIA-Fall-26-Team-1/lantern-case-study-2b.git
cd lantern-case-study-2b; git checkout cs2b-submission; cd cs2b
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
dvc pull
dvc repro
$env:PYTHONPATH="src"; python -m lookthrough.check
python tests\run_tests.py
```

To rebuild every stage from the raw release instead of reusing the pulled outputs: `dvc repro -f`
(about 1 minute). We tested both on Windows (Python 3.14) and on Linux (Docker, `python:3.11-slim`):
the panel (`outputs/panel/holdings.parquet`, MD5 `5402d3dfc237dd3189226298a4590c02`) and every
report are byte-identical. After a forced rebuild on a different operating system or Python version,
only `outputs/p3_work/baseline.pkl` gets a new hash in `dvc.lock`, because a pickle stores Python and
numpy internals; its content, and every result built from it, is unchanged.

## The pipeline (`cs2b/dvc.yaml`)

| Stage | Script | Writes |
|---|---|---|
| acquire | `scripts/acquire.py` | `outputs/acquire/verified.json`. Verifies the 3 ZIPs against `data/manifest.json` (SHA-256) and the merged release against the monthly files; downloads nothing (`data/raw` comes from `dvc pull`) |
| parse | `scripts/parse.py` | `outputs/work/parse/`: SUB, NUM, canonical frame, coalesced holdings |
| clean | `scripts/clean.py` | `outputs/work/clean/`, `reports/cleaning_log.csv`. Applies `rules.TEAM_RULES` in its fixed order |
| reconcile | `scripts/p3a_reconcile.py` | `outputs/panel/holdings.parquet` (admitted filings only), `reports/coverage.json` (DVC metric), `outputs/p3_work/baseline.pkl` |
| report | `scripts/p3b`–`p3e` | `reports/p3_gap_evidence*.csv`, `coverage.csv`, `coverage.md`, `triage.md` |

Parameter: `reconcile.tolerance` (0.01) in `params.yaml`. Metric: `dvc metrics show`. Each output has
exactly one writing stage. `data/raw` and every `outputs/` file are tracked by DVC; `reports/` stays in Git.

## Where each Part is

| Part | Deliverables |
|---|---|
| 0 Setup, acquisition, provenance | `cs2b/params.yaml`, `data/manifest.json`, `data/raw.dvc`, `docs/merge.md` |
| 1 Raw parsing and schema | `cs2b/docs/schema.md`, `reports/agreement.md` |
| 2 Cleaning | `cs2b/src/lookthrough/rules.py`, `docs/cleaning_log.md`, `reports/cleaning_log.csv` |
| 3 Reconciliation, coverage, triage | `cs2b/outputs/panel/holdings.parquet` (DVC), `reports/coverage.csv`, `coverage.md`, `coverage.json`, `triage.md` |
| 4 Verify the dependency | `cs2b/reports/spot_check.csv`, `reports/dependency_check.md` |
| 5 Pipeline, tests, economics | `cs2b/dvc.yaml`, `dvc.lock`, `scripts/`, `reports/tests_that_fail.md`, `reports/economics.md` |

## Notes

- Do not run notebook 02 or `tools/run_notebooks.py`: with `release: "2026q1"`, notebook 02 tries to
  download a `2026q1_bdc.zip` that does not exist (the SEC publishes 2026 releases monthly).
- To rebuild the merged release from the 3 monthly ZIPs: `python scripts/merge_release.py`, then
  `python scripts/verify_merge.py` (must print "merge verified"). See `cs2b/docs/merge.md`.
- `python scripts/p5_tests_that_fail.py` breaks each rule and Part 1 fix, runs the tests and restores the
  code; it regenerates `reports/tests_that_fail.md`.
- Team pushes to DVC use the `store` remote with keys in `.dvc/config.local` only (never committed):
  `dvc push -r store`.
