import streamlit as st

from data import filing_index_url, panel_or_stop

st.title("Panel: holdings of admitted filings")
p = panel_or_stop()
st.caption(f"{len(p):,} holdings across {p['adsh'].nunique()} admitted filings. Source: outputs/panel/holdings.parquet")

filings = (p.groupby(["adsh", "name"], as_index=False)["fair_value"].sum()
           .sort_values("fair_value", ascending=False))
labels = {r.adsh: f"{r.name} ({r.adsh})" for r in filings.itertuples()}
adsh = st.selectbox("BDC filing (largest first)", list(labels), format_func=labels.get)
g = p[p["adsh"] == adsh]
r = g.iloc[0]
st.markdown(f"**{r['name']}** · adsh `{adsh}` · period {r['period']} · "
            f"[filing on EDGAR]({filing_index_url(r['cik'], adsh)})")

q = st.text_input("Search identifier")
if q:
    g = g[g["identifier"].str.contains(q, case=False, na=False, regex=False)]
st.metric("Holdings / fair value", f"{len(g):,} / ${g['fair_value'].sum() / 1e6:,.1f}m")
cols = [c for c in ["identifier", "investment_type", "industry", "affiliation", "fair_value", "principal", "cost",
                    "interest_rate", "spread", "pik_rate", "maturity", "pct_net_assets", "source_rows", "n_rows",
                    "n_conflicts"] if c in g]
empty = [c for c in cols if g[c].isna().all()]          # fields this filer does not report
st.dataframe(g[[c for c in cols if c not in empty]], width="stretch", hide_index=True)
if empty:
    st.caption("Empty for this filing, so hidden: " + ", ".join(empty))
st.download_button("Download these rows (CSV)", g.to_csv(index=False).encode("utf-8"),
                   file_name=f"holdings_{adsh}.csv", mime="text/csv")
st.caption("source_rows = 0-based row numbers in data/raw/2026q1_bdc/soi.tsv (the kit's soi_row).")