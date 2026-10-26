"""P0: write data/manifest.json once: one row per monthly ZIP (path, url, bytes, sha256, recorded).
Refuses to overwrite an existing manifest unless run with --force (only if the ZIPs changed)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lookthrough import acquire, paths  # noqa: E402

MONTHS = ["2026_01", "2026_02", "2026_03"]
P = paths.load_params(ROOT)
out = ROOT / "data" / "manifest.json"
if out.exists() and "--force" not in sys.argv:
    sys.exit(f"{out.relative_to(ROOT)} already exists; it is written once. Use --force only if the ZIPs changed.")

zips = [ROOT / "data" / "raw" / f"{m}_bdc.zip" for m in MONTHS]
rows = acquire.write_manifest(zips, out, root=ROOT)
for r, m in zip(rows, MONTHS):
    r["url"] = acquire.release_url(m, P["sec"]["base_url"])
out.write_text(json.dumps(rows, indent=2))
for r in rows:
    print(f"{r['path']}  {r['bytes']:,} bytes  sha256 {r['sha256'][:16]}...  {r['url']}")
print("verify_manifest:", acquire.verify_manifest(out, root=ROOT))