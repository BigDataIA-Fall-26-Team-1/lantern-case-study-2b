"""Shared loaders for the LANTERN 2B app. Read-only: the app never runs the pipeline.

Reads only files in Git (reports/, docs/) and the panel restored by `dvc pull`.
Paths resolve from cs2b/, so the app runs from any working directory.
"""
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]          # cs2b/
REPORTS = ROOT / "reports"
PANEL = ROOT / "outputs" / "panel" / "holdings.parquet"

# scripts/p3e_triage.py writes one heading per excluded filing:  ### {name} ({adsh}, {form})
TRIAGE_HEADING = re.compile(r"^### (.+) \((\d{10}-\d{2}-\d{6}), ([^)]+)\)\s*$")


def read_text(rel: str) -> str:
    """UTF-8 on every OS (Windows would otherwise use cp1252 and fail on characters such as an em dash)."""
    return (ROOT / rel).read_text(encoding="utf-8")


def md(s: str) -> str:
    """Escape $ so Streamlit shows dollar amounts as text, not as a math formula between two $ signs."""
    return s.replace("$", "\\$")


@st.cache_data
def coverage_json() -> dict:
    return json.loads(read_text("reports/coverage.json"))


@st.cache_data
def coverage() -> pd.DataFrame:
    cov = pd.read_csv(REPORTS / "coverage.csv", dtype={"adsh": str, "cik": str})
    cov["admitted"] = cov["admitted"].astype(str).str.lower().isin(["true", "1"])   # as check.py reads it
    cov["triage_category"] = cov["triage_category"].fillna("")                     # "" for admitted filings
    return cov


@st.cache_data
def panel() -> pd.DataFrame:
    return pd.read_parquet(PANEL)


def panel_or_stop() -> pd.DataFrame:
    if not PANEL.exists():
        st.error("outputs/panel/holdings.parquet is missing. From cs2b/, run: dvc pull outputs/panel/holdings.parquet")
        st.stop()
    return panel()


@st.cache_data
def csv(name: str) -> pd.DataFrame:
    return pd.read_csv(REPORTS / name, dtype=str)


@st.cache_data
def text(rel: str) -> str:
    return read_text(rel)


@st.cache_data
def triage_sections() -> dict:
    """{adsh: markdown section} from reports/triage.md, one section per '### NAME (adsh, form)' heading."""
    out, cur, buf = {}, None, []
    for line in read_text("reports/triage.md").splitlines():
        m = TRIAGE_HEADING.match(line)
        if m or line.startswith("## "):          # a new filing, or a new top-level section
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = (m.group(2), [line]) if m else (None, [])
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return out


def filing_index_url(cik, adsh: str) -> str:
    """EDGAR folder of a filing, built from CIK and accession number (no raw data needed)."""
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/"