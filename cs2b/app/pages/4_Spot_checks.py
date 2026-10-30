import streamlit as st

from data import csv, md, text

st.title("Part 4: holdings checked against the filings")
s = csv("spot_check.csv")
if "matches" in s:
    counts = s["matches"].value_counts()
    st.write(f"**{len(s)}** holdings across **{s['adsh'].nunique()}** filings: "
             + ", ".join(f"{v} {k}" for k, v in counts.items()))
cols = ["check", "name", "adsh", "identifier", "fair_value", "principal", "filing_fair_value", "filing_principal",
        "filing_units", "matches", "where_in_filing", "note", "filing_url"]
st.dataframe(s[[c for c in cols if c in s]], width="stretch", hide_index=True)
with st.expander("reports/dependency_check.md"):
    st.markdown(md(text("reports/dependency_check.md")))