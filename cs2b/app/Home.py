import streamlit as st

from data import coverage, coverage_json, csv

st.set_page_config(page_title="LANTERN 2B: BDC look-through", layout="wide")
st.title("Project LANTERN, Case Study 2B")
st.caption("A reconciled BDC holdings panel for release 2026q1 (SEC BDC data sets 2026_01 + 2026_02 + 2026_03). "
           "DAMG 7245, Team 1: Pranav, Preksha, Pradyumna.")

c = coverage_json()
excluded = int((~coverage()["admitted"]).sum())
a, b, d, e = st.columns(4)
a.metric(f"Filings admitted ({c['share_of_filings']:.1%})", f"{c['filings_admitted']} of {c['filings_attempted']}")
b.metric(f"Filed fair value admitted ({c['share_of_dollars']:.1%})", f"${c['filed_fv_admitted'] / 1e9:,.1f}bn")
d.metric("Filed fair value attempted", f"${c['filed_fv_attempted'] / 1e9:,.1f}bn")
e.metric("Filings with no SOI rows", c.get("filings_without_soi_rows", "n/a"))
st.write(f"**{excluded}** excluded filings, each triaged with evidence (see the Triage page). "
         "A filing is admitted when its holdings are within 1% of the filer's own reported total.")

log = csv("cleaning_log.csv")
st.subheader(f"Cleaning rules ({len(log)}, from reports/cleaning_log.csv)")
st.dataframe(log, width="stretch", hide_index=True)
st.info("Read-only view of the pipeline's outputs. Every number traces to a file in reports/ or outputs/panel/.")