import streamlit as st

from data import coverage, md, triage_sections

st.title("Triage: why each excluded filing was not admitted")
cov = coverage()
ex = cov[~cov["admitted"]].sort_values("filed_fv", ascending=False, na_position="last")
sec = triage_sections()
missing = [a for a in ex["adsh"] if a not in sec]
if missing:
    st.warning(f"{len(missing)} excluded filings have no section in reports/triage.md, e.g. {missing[:3]}")

cats = sorted(c for c in ex["triage_category"].unique() if c)
pick = st.multiselect("Triage category", cats)
if pick:
    ex = ex[ex["triage_category"].isin(pick)]
labels = {r.adsh: f"{r.name} ({r.adsh}) - {r.triage_category}" for r in ex.itertuples()}
choice = st.selectbox("Excluded filing (largest filed total first)", list(labels), format_func=labels.get)
if choice:
    st.markdown(md(sec.get(choice, "_No section found in reports/triage.md for this filing._")))
st.caption(f"{len(ex)} excluded filings shown; {len(sec)} sections in reports/triage.md.")