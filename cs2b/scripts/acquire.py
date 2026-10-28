"""P5 stage 'acquire': verify the release; never download.

data/raw is restored by `dvc pull` (data/raw.dvc). This stage checks that the 3 monthly ZIPs
match data/manifest.json (SHA-256) and that data/raw/2026q1_bdc equals the monthly files
(scripts/verify_merge.py). Writes outputs/acquire/verified.json.
Run from cs2b/:  python scripts/acquire.py
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lookthrough import acquire, paths  # noqa: E402

P = paths.load_params(ROOT)
manifest = ROOT / "data" / "manifest.json"
entries = json.loads(manifest.read_text())

# 1. The ZIPs are the ones we recorded in Part 0
bad = acquire.verify_manifest(manifest, root=ROOT)
if bad:
    sys.exit(f"manifest mismatch (missing or changed): {bad}. Run `dvc pull` first.")
print(f"manifest verified: {len(entries)} files", flush=True)

# 2. The merged release equals the 3 monthly files
r = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_merge.py")])
if r.returncode != 0:
    sys.exit("merge check failed: data/raw/2026q1_bdc differs from the monthly files")

# 3. A small output so the parse stage runs after this one
out = ROOT / "outputs" / "acquire" / "verified.json"
out.parent.mkdir(parents=True, exist_ok=True)
info = {"release": P["release"],
        "manifest": [{"path": e["path"], "sha256": e["sha256"]} for e in entries],
        "manifest_mismatches": bad,
        "merge_verified": True}
with open(out, "w", newline="\n") as fh:       # LF on every OS
    fh.write(json.dumps(info, indent=2) + "\n")
print(f"wrote {out.relative_to(ROOT).as_posix()}")