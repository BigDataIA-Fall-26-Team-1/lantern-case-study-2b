"""Shared loader for P1 scripts: latest filings, current period, kit mapping."""
import sys

sys.path.insert(0, "src")
from lookthrough.holdings import TEXT, coalesce_holdings, split_periods
from lookthrough.load import load_soi, load_sub, load_tag, norm_date, soi_header
from lookthrough.mapping import AXES, CANONICAL, map_soi_columns, soi_usecols, to_canonical
from lookthrough.paths import load_params, release_dir

SUBAX = "Investment Company, Nonconsolidated Subsidiary Axis"


def load_current():
    """Return current-period rows, coalesced holdings, extra axes, compared fields."""
    rdir = release_dir(load_params())
    sub, tag, header = load_sub(rdir), load_tag(rdir), soi_header(rdir)
    colmap = map_soi_columns(header, tag)
    extra = [c for c in header if c.endswith("Axis") and c not in AXES.values()]
    prov = [c for c in ("source_release", "source_soi_row") if c in header]
    soi = load_soi(rdir, usecols=soi_usecols(header, colmap) + prov + extra)
    if "soi_row" not in soi:
        soi["soi_row"] = soi.index
    canon = to_canonical(soi, colmap)
    for c in prov + extra:
        canon[c] = soi[c]
    canon["ddate"], canon["period"] = norm_date(canon["ddate"]), norm_date(canon["period"])
    canon = canon[canon["adsh"].isin(sub["adsh"])]
    h = split_periods(canon, sub)
    cur = h[h["is_current"]].copy()
    fields = [f for f in list(CANONICAL) + TEXT if f in cur]
    return cur, coalesce_holdings(cur), extra, fields