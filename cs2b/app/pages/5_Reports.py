import streamlit as st

from data import ROOT, md, text

st.title("Reports and documentation")
docs = ["reports/coverage.md", "reports/triage.md", "reports/economics.md", "reports/tests_that_fail.md",
        "docs/cleaning_log.md", "docs/schema.md", "reports/agreement.md", "reports/dependency_check.md",
        "docs/merge.md", "reports/issue_draft.md"]
have = [d for d in docs if (ROOT / d).exists()]
pick = st.selectbox("Document", have)
st.markdown(md(text(pick)))