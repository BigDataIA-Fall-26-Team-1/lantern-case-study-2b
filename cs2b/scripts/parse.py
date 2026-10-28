"""P5 stage 'parse': the release -> canonical frame and coalesced holdings (notebooks 03-04).

The same calls, in the same order, as the first half of the kit's pipeline.run_baseline.
Writes outputs/work/parse/{sub,num,canon,holdings,soi_adsh}.parquet (+ .objects.json), and
checks that each table reads back exactly. Run from cs2b/:  python scripts/parse.py
"""
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lookthrough import holdings, load, mapping, paths, reconcile  # noqa: E402
from workio import save_frames  # noqa: E402

P = paths.load_params(ROOT)
rdir = paths.release_dir(P, ROOT)
t0 = time.perf_counter()

sub, tag = load.load_sub(rdir), load.load_tag(rdir)
header = load.soi_header(rdir)
colmap = mapping.map_soi_columns(header, tag)
soi = load.load_soi(rdir, mapping.soi_usecols(header, colmap))
soi = soi[soi["adsh"].isin(sub["adsh"])]
num = load.load_num(rdir, tags=[reconcile.FV_TAG], custom_fv=True)
canon = holdings.split_periods(mapping.to_canonical(soi, colmap), sub)
h = holdings.coalesce_holdings(canon)

frames = {"sub": sub, "num": num, "canon": canon, "holdings": h,
          "soi_adsh": pd.DataFrame({"adsh": sorted(set(soi["adsh"]))})}
save_frames(frames, ROOT / "outputs" / "work" / "parse")

print(f"SUB current filings: {len(sub)}; filings with SOI rows: {len(frames['soi_adsh'])}; "
      f"current holdings: {int(h['is_current'].sum()):,}")
print(f"parse done in {time.perf_counter() - t0:.1f} s")