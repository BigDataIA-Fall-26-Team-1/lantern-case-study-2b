"""P0 sanity check: run notebooks 01, 03 and 04 on the release in params.yaml and show their output.
Notebook 02 is skipped: it downloads params.release ("2026q1"), which has no single SEC ZIP."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ["01_primer_exercise", "03_raw_parse", "04_periods_and_dimensions"]

fails = 0
for name in NOTEBOOKS:
    nb = json.loads((ROOT / "notebooks" / f"{name}.ipynb").read_text(encoding="utf-8"))
    cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    src = "\n\n".join("".join(c["source"]) if isinstance(c["source"], list) else c["source"] for c in cells)
    print(f"===== {name} =====", flush=True)
    r = subprocess.run([sys.executable, "-c", src], cwd=ROOT / "notebooks",
                       env=dict(os.environ, MPLBACKEND="Agg"))
    fails += r.returncode != 0
    print(f"----- {name}: {'PASS' if r.returncode == 0 else 'FAIL'}\n", flush=True)
sys.exit(1 if fails else 0)