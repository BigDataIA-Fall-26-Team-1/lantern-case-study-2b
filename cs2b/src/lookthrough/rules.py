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


TEAM_RULES = [rule_jv_subsidiary, rule_range_axis, rule_category_member, rule_totals_v2, clean.rule_cash]
