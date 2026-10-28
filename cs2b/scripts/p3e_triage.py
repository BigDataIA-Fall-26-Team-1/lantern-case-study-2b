"""P3 step 5: a triage category for every excluded filing; coverage and triage reports."""
import sys

import pandas as pd

sys.path.insert(0, "src")
from lookthrough import paths, reconcile

root = paths.repo_root()
P = paths.load_params(root)
TOL = float(P["reconcile"]["tolerance"])   # P5: the admission tolerance from params.yaml
PCT = f"{TOL:.0%}"                         # P5: "1%" in the report text
rep = root / P["outputs"]["reports"]
B = pd.read_pickle(root / "outputs" / "p3_work" / "baseline.pkl")
rec, diag, kept, sub = B["rec"], B["diag"], B["kept"], B["sub"]
e1 = pd.read_csv(rep / "p3_gap_evidence.csv", dtype={"adsh": str})
e3 = pd.read_csv(rep / "p3_gap_evidence3.csv", dtype={"adsh": str})
ev = (rec.merge(diag.drop(columns=["name", "gap_pct", "n_holdings"]), on="adsh", how="left")
      .merge(e1.drop(columns=["name", "form", "gap_pct", "missing_fv"]), on="adsh", how="left")
      .merge(e3.drop(columns=["name", "gap_pct", "gap_m"]), on="adsh", how="left"))
for c in ["unfunded_closes", "cash_closes", "big_closes", "subtotal_closes"]:
    ev[c] = ev[c].astype("boolean").fillna(False).astype(bool)


def m(x):
    return "n/a" if pd.isna(x) else f"${x / 1e6:,.1f}m"


def holding(k, which="largest"):
    if which == "missing" and k["fair_value"].isna().any():
        h = k[k["fair_value"].isna()].iloc[0]
    else:
        h = k.loc[k["fair_value"].idxmax()]
    return f"`{h.identifier[:90]}`, fair value {m(h.fair_value)}, SOI rows {h.source_rows}"


def subtotal_example(k):
    k = k[k["fair_value"].notna()]
    items = sorted(zip(k["identifier"], k["fair_value"], k["source_rows"]))
    for i, (name, fv, rows) in enumerate(items):
        j, s, c = i + 1, 0.0, 0
        while j < len(items) and items[j][0].startswith(name) and len(items[j][0]) > len(name):
            s, c, j = s + items[j][1], c + 1, j + 1
        if c >= 2 and fv and abs(fv - s) <= 0.005 * abs(fv):
            return f"`{name[:90]}`, {m(fv)}, SOI rows {rows}, equal to its {c} tranches below it"
    return None


NOFIX = "None: no evidenced rule exists, and a rule only to force a match is not allowed."


def classify(r):
    k = kept[kept["adsh"] == r.adsh]
    gap = r.holdings_fv - r.filed_fv if pd.notna(r.filed_fv) and pd.notna(r.holdings_fv) else float("nan")
    if pd.isna(r.filed_fv):
        return ("no_filed_total", "NUM has no undimensioned InvestmentOwnedAtFairValue fact at the period end.",
                f"{r.n_holdings} holdings parsed, nothing to reconcile against.",
                "None possible: the filer reports no total under the standard tag.")
    if r.n_holdings == 0:
        return ("no_identified_holdings",
                f"{int(r.rows_without_identifier)} current SOI rows, none with an identifier.",
                "Rows only on a custom axis (dropped from the SOI) or subtotals.",
                "None in Part 3: identifiers on a custom axis are not in the SOI.")
    hidden = (r.num_missing_m + r.num_for_nan_m) * 1e6
    if hidden > TOL * r.filed_fv:
        return ("custom_tags",
                f"NUM has {m(hidden)} of identifier-level fair value the SOI lacks: "
                f"{m(r.num_missing_m * 1e6)} on identifiers absent from the SOI, and "
                f"{m(r.num_for_nan_m * 1e6)} for {r.missing_fv} SOI holdings with no fair value.",
                holding(k, "missing"),
                "Not fixed: recovering these values from NUM is the stretch goal.")
    if r.ratio > 10:
        return ("other",
                f"Our holdings are {r.ratio:,.1f}x the filed fact ({m(r.filed_fv)}), and match the filer's own "
                "identifier-level NUM facts: the undimensioned fact is not the portfolio total.",
                holding(k), "None possible from the data set: the filing's total is not tagged as expected.")
    if r.subtotal_closes:
        return ("totals_counted",
                f"{int(r.n_subtotals)} holdings ({m(r.subtotal_m * 1e6)}) equal the sum of the holdings whose "
                f"identifiers extend their names; the gap is {m(gap)}. Issuer-level subtotals carry an identifier.",
                subtotal_example(k) or holding(k), "Partly fixed: rule_issuer_subtotals drops exact issuer subtotals; the rows left here fail its 0.5% guard.")
    if r.unfunded_closes:
        return ("unfunded_commitments", f"Negative fair values ({m(r.neg_m * 1e6)}) close the gap of {m(gap)}.",
                holding(k), "None: the filer nets unfunded commitments differently; most filers keep them.")
    if r.cash_closes:
        return ("cash_lines", f"Cash rows dropped by rule_cash ({m(r.cash_m * 1e6)}) close the gap of {m(gap)}.",
                holding(k), "None: this filer's total includes cash; rule_cash is right for most filers.")
    if r.big_closes:
        return ("totals_counted", f"A single holding ({m(r.big_m * 1e6)}) equals the gap of {m(gap)}.",
                holding(k), "None yet: one filing, verify before writing a rule.")
    if gap < 0 and (r.missing_fv > 0 or r.custom_fv_facts_in_num > 0):
        return ("custom_tags",
                f"We are short by {m(-gap)}; {r.missing_fv} holdings have no SOI fair value and NUM has "
                f"{int(r.custom_fv_facts_in_num)} custom-tag fair value facts.",
                holding(k, "missing"), "Not fixed: recovering custom-tag values from NUM is the stretch goal.")
    if gap > 0 and r.subtotal_m * 1e6 >= 0.5 * gap:
        return ("totals_counted",
                f"Issuer-level subtotals ({m(r.subtotal_m * 1e6)}, {int(r.n_subtotals)} rows) explain at least half "
                f"of the {m(gap)} gap.", subtotal_example(k) or holding(k),
                "Partly fixed: rule_issuer_subtotals drops exact issuer subtotals; the rows left here fail its 0.5% guard.")
    if r.ratio >= 2 and abs(r.ratio - round(r.ratio)) < 0.005:
        return ("totals_counted",
                f"Our holdings are exactly {r.ratio:.3f}x the filed total ({m(r.filed_fv)}). Holdings and "
                "subtotal rows at several levels (industry, investment type, affiliation category) all carry "
                "identifiers, and each level sums to the full portfolio, so "
                f"{round(r.ratio)} levels give {round(r.ratio)}x. For Star Mountain (0001140361-26-012276) the "
                "schedule's total ($375.0m) was confirmed by hand, and UJP Acquisition's warrants (SOI rows "
                "162550;162551, 29,787) reappear as the Food Products subtotal (row 110409) and the "
                "warrants-category subtotal (row 165467).",
                holding(k),
                "Not fixed: these subtotal identifiers share no common word such as 'Total'; separating them "
                "needs the schedule's hierarchy, which the SOI does not carry.")
    exact = r.ratio >= 2 and abs(r.ratio - round(r.ratio)) < 0.001
    note = f" Our total is exactly {round(r.ratio)}x the filed fact." if exact else ""
    return ("other",
            f"Our holdings match the filer's own identifier-level NUM facts (difference {r.num_sum_vs_holdings:+.1%}), "
            f"but exceed its reported total by {m(gap)} ({r.gap_pct:+.1%}): the filer tags holdings its total does "
            f"not include, for example a second schedule or joint venture we could not attribute.{note}",
            holding(k), NOFIX)


ex = ev[~ev["admitted"]].copy()
out = ex.apply(lambda r: pd.Series(classify(r), index=["cat", "evidence", "example", "fix"]), axis=1)
ex = ex.join(out)
assert set(ex["cat"]) <= set(reconcile.TRIAGE), set(ex["cat"]) - set(reconcile.TRIAGE)

# coverage.csv with real categories
cov = rec.copy()
cov["triage_category"] = cov["adsh"].map(ex.set_index("adsh")["cat"]).fillna("")
cov.to_csv(rep / "coverage.csv", index=False, lineterminator="\n")   # P5: LF on every OS

# triage.md
summ = ex.groupby("cat").agg(filings=("adsh", "size"), filed=("filed_fv", "sum")).sort_values("filings", ascending=False)
total_f, total_d = len(rec), rec["filed_fv"].sum()
n_match = int(e3["num_sum_vs_holdings"].abs().le(TOL).sum())   # P5: key finding computed from p3d's evidence
lines = ["# Triage of non-admitted filings", "",
         f"{len(ex)} of {total_f} attempted filings were not admitted "
         f"({m(ex['filed_fv'].sum())} of {m(total_d)} filed fair value).", "",
         "Evidence: `reports/p3_gap_evidence.csv` (simple causes), `reports/p3_gap_evidence2.csv` (extra axes, "
         "alternative totals), `reports/p3_gap_evidence3.csv` (NUM comparison, issuer subtotals). "
         "Scripts: `scripts/p3b_gap_evidence.py`, `scripts/p3c_deep_evidence.py`, `scripts/p3d_num_and_subtotals.py`, "
         "`scripts/p3e_triage.py`.", "",
         "## Key finding", "",
         f"For {n_match} of the {len(e3)} excluded filings with a filed total and holdings, the filer's own identifier-level "
         f"fair value facts in NUM sum to our parsed holdings within {PCT}, and every matched holding's SOI value "
         "equals its NUM value. The parse is faithful; most gaps come from what the filers tag, not from parsing.", "",
         "## Category rules (applied in this order)", "",
         "1. No filed total in NUM: `no_filed_total`.",
         "2. No identified holdings: `no_identified_holdings`.",
         f"3. NUM has identifier-level fair value the SOI lacks (identifiers absent from SOI holdings before any rule, plus NUM values for SOI holdings with no fair value) above {PCT} of the filed total: `custom_tags`.",   # P5 rule 3: wording matches the code
         "4. Our holdings more than 10x the filed fact: `other` (the fact is not the portfolio total).",
         "5. Issuer-level subtotals close the gap: `totals_counted`.",
         "6. Removing negative fair values closes the gap: `unfunded_commitments`.",
         "7. Adding back cash dropped by rule_cash closes the gap: `cash_lines`.",
         "8. A single holding equals the gap: `totals_counted`.",
         "9. Short of the total with missing fair values: `custom_tags`.",
         "10. Over the total with subtotals explaining at least half the gap: `totals_counted`.",
         "10b. Our total an exact multiple (2x or more) of the filed total: `totals_counted` "
         "(subtotal levels carrying identifiers).",
         "11. Otherwise: `other`, with the NUM evidence stated.", "",
         "## Summary", "", "| Category | Filings | Filed fair value |", "|---|---:|---:|"]
lines += [f"| {c} | {r.filings} | {m(r.filed)} |" for c, r in summ.iterrows()]
lines += ["", "## Filings", ""]
for r in ex.sort_values("filed_fv", ascending=False, na_position="last").itertuples():
    gap = "n/a" if pd.isna(r.gap_pct) else f"{r.gap_pct:+.2%}"
    lines += [f"### {r.name} ({r.adsh}, {r.form})", "",
              f"- Gap: {gap}; holdings {m(r.holdings_fv)} ({r.n_holdings}); filed {m(r.filed_fv)}",
              f"- **Category:** `{r.cat}`", f"- **Evidence:** {r.evidence}",
              f"- **Example:** {r.example}", f"- **Fix or reason:** {r.fix}", ""]
(rep / "triage.md").write_text("\n".join(lines), newline="\n")   # P5: LF on every OS

# coverage.md: summary first, then the per-filing table
no_soi = sub[~sub["adsh"].isin(rec["adsh"])]
a = rec[rec["admitted"]]
head = ["# Coverage report", "",
        f"**Filings:** {len(a)} of {total_f} attempted admitted ({len(a) / total_f:.1%}).",
        f"**Dollars:** {m(a['filed_fv'].sum())} of {m(total_d)} filed fair value admitted "
        f"({a['filed_fv'].sum() / total_d:.1%}).", "",
        f"Filings in SUB with no SOI rows ({len(no_soi)}), reported separately and not attempted:", ""]
head += [f"- {r.name} ({r.adsh}, {r.form}, period {r.period})" for r in no_soi.itertuples()]
head += ["", "Excluded filings by triage category (see `reports/triage.md`):", "",
         "| Category | Filings | Filed fair value |", "|---|---:|---:|"]
head += [f"| {c} | {r.filings} | {m(r.filed)} |" for c, r in summ.iterrows()]
# P5: the per-filing table is built here, in the kit's exact format (report.write_outputs),
# instead of being copied out of the kit's coverage.md
money = lambda x: "n/a" if pd.isna(x) else f"{x:,.0f}"
pct = lambda x: "n/a" if pd.isna(x) else f"{x:+.2%}"
table = ["| BDC | Holdings | Holdings FV | Filed FV | Gap | Admitted |", "|---|---:|---:|---:|---:|---|"]
table += [f"| {r.name} | {r.n_holdings} | {money(r.holdings_fv)} | {money(r.filed_fv)} | {pct(r.gap_pct)} | {r.admitted} |"
          for r in cov.itertuples()]
(rep / "coverage.md").write_text("\n".join(head + ["", "## Per filing", ""] + table + [""]), newline="\n")

print(summ.assign(filed_bn=summ["filed"] / 1e9).drop(columns="filed").round(2).to_string())
print(f"\nWrote {rep / 'coverage.csv'}, {rep / 'triage.md'}, {rep / 'coverage.md'}")