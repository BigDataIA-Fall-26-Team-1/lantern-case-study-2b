import streamlit as st

from data import coverage

st.title("Coverage: every attempted filing")
cov = coverage()
f = st.radio("Show", ["All", "Admitted", "Excluded"], horizontal=True)
if f != "All":
    cov = cov[cov["admitted"] == (f == "Admitted")]
cats = sorted(c for c in cov["triage_category"].unique() if c)
pick = st.multiselect("Triage category (excluded filings)", cats)
if pick:
    cov = cov[cov["triage_category"].isin(pick)]
q = st.text_input("Search BDC name")
if q:
    cov = cov[cov["name"].str.contains(q, case=False, na=False, regex=False)]
cols = ["name", "adsh", "form", "period", "n_holdings", "holdings_fv", "filed_fv", "gap_pct", "admitted",
        "triage_category", "missing_fv", "cik"]
st.dataframe(cov[[c for c in cols if c in cov]], width="stretch", hide_index=True)
st.caption(f"{len(cov)} filings shown. gap_pct = (holdings_fv - filed_fv) / filed_fv. Source: reports/coverage.csv")
