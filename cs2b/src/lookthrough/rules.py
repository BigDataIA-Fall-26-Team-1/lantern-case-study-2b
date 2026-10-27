"""Team cleaning rules for release 2026q1 (Case Study 2B, Part 2).

Same contract as clean.rule_totals: each rule takes current-period coalesced holdings and
returns (drop_mask, one-line artifact description). Evidence for each rule: docs/cleaning_log.md
and reports/p2_artifact_survey.csv.
"""
import pandas as pd

from . import clean

# "Total ..." followed, in the same segment, by a legal-entity word = a borrower, not a total.
# "company" / "co" left out on purpose: "Total Unfunded Portfolio Company Commitments" is a total.
BORROWER = (r"^\s*total\b[^|]*?\b(?:llc|inc|l\.?p|ltd|limited|corp|corporation"
            r"|holdings|plc|gmbh|sarl|s\.a)\b")
MEMBER = r"\[Member\]\s*$"
# category words seen in 2026q1 member identifiers (Lord Abbett, BCP); borrower members
# such as "Accel International Holdings, Inc. (Revolver) [Member]" do not match
CATEGORY = r"^\s*(?:(?:first|second)\s+lien|equity\b|investment in joint venture|investment,|non[ -]?controlled)"


def rule_totals_v2(h: pd.DataFrame):
    """The kit's total pattern, minus borrowers named 'Total ...' and rows with loan terms."""
    total = clean._matches(h, clean.TOTAL)
    borrower = h["identifier"].str.contains(BORROWER, case=False, regex=True, na=False)
    has_terms = h["spread"].notna() | h["maturity"].notna()
    return (total & ~borrower & ~has_terms,
            "identifier names a total or subtotal (not a borrower named 'Total ...', not a row with loan terms)")


def rule_jv_subsidiary(h: pd.DataFrame):
    """Rows on the Nonconsolidated Subsidiary axis are a JV's own portfolio, not the BDC's holdings."""
    return (h["subsidiary"].notna(),
            "JV / nonconsolidated-subsidiary portfolio row (the BDC's stake in the JV is its own holding)")


def rule_range_axis(h: pd.DataFrame):
    """Rows on the Range axis are low/high/average bounds, not a holding's value."""
    return (h["range"].notna(),
            "range bound on Range Axis (Minimum/Maximum/Weighted Average), not a holding")


def rule_category_member(h: pd.DataFrame):
    """An identifier that is an XBRL category member ('First Lien Secured Debt [Member]') is a subtotal."""
    ident = h["identifier"]
    member = ident.str.contains(MEMBER, regex=True, na=False)
    category = ident.str.contains(CATEGORY, case=False, regex=True, na=False)
    return (member & category,
            "identifier is an XBRL category member ('First Lien Secured Debt [Member]'): a subtotal, not an investment")


# PennantPark lists its JV's (PennantPark Senior Loan Fund, PSSL) loans with no subsidiary axis.
# Its own holdings start "Investments in ..."; the JV schedule starts with the instrument type
# and then "Issuer Name" (e.g. "First Lien Secured Debt Issuer Name ...").
JV_SCHEDULE = (r"^\s*(?:first lien|second lien|equity securities|subordinated debt|preferred|common)\b"
               r"[^|]*?\bissuer name\b")


def rule_jv_schedule_style(h: pd.DataFrame):
    """JV portfolio rows that carry no subsidiary axis, recognised by the filer's JV-schedule identifier style."""
    return (h["identifier"].str.contains(JV_SCHEDULE, case=False, regex=True, na=False),
            "JV schedule row without a subsidiary axis (PennantPark PSSL style: '<instrument> Issuer Name ...')")

def rule_issuer_subtotals(h: pd.DataFrame):
    """Issuer-level subtotal rows that carry an identifier.

    Observed in Ares Capital (0001287750-26-000006) and Ares Strategic Income
    (0001918712-26-000018): a row named for the company sits above its tranches,
    and its fair value equals their sum. Dropped only when at least 2 holdings'
    identifiers extend its name and the values agree within 0.5%."""
    drop = pd.Series(False, index=h.index)
    ok = h["identifier"].notna() & h["fair_value"].notna()
    for _, g in h[ok].groupby(["adsh", "ddate"], sort=False):
        g = g.sort_values("identifier")
        names, fv, idx = g["identifier"].tolist(), g["fair_value"].tolist(), g.index.tolist()
        for i, name in enumerate(names):
            j, s, c = i + 1, 0.0, 0
            while j < len(names) and names[j].startswith(name) and len(names[j]) > len(name):
                s, c, j = s + fv[j], c + 1, j + 1
            if c >= 2 and fv[i] and abs(fv[i] - s) <= 0.005 * abs(fv[i]):
                drop[idx[i]] = True
    return drop, ("issuer-level subtotal row: its fair value equals the sum of the "
                  "holdings whose identifiers extend its name")

TEAM_RULES = [rule_jv_subsidiary, rule_jv_schedule_style, rule_range_axis, rule_category_member,
              rule_totals_v2,
              rule_issuer_subtotals, clean.rule_cash]
