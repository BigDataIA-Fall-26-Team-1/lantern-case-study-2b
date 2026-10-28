"""Save and load the pipeline's work tables (Parquet), exactly as pandas held them in memory.

pandas 3 reads Parquet text columns back as the new str dtype, and Parquet has one "missing"
(null) where pandas may have used None or NaN. For each object column we record which missing
marker it used, and restore both the object dtype and that marker on load. save_frames reads
every table back and stops if it differs in any value, dtype or index.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _marker(s: pd.Series) -> str:
    vals = s.to_numpy(dtype=object)
    has_none = any(v is None for v in vals)
    has_nan = any(isinstance(v, float) and np.isnan(v) for v in vals)
    if has_none and has_nan:
        raise ValueError(f"column {s.name!r} mixes None and NaN; cannot restore it exactly")
    return "none" if has_none else "nan"


def load_frame(folder, name) -> pd.DataFrame:
    folder = Path(folder)
    df = pd.read_parquet(folder / f"{name}.parquet")
    for c, marker in json.loads((folder / f"{name}.objects.json").read_text()).items():
        vals = df[c].to_numpy(dtype=object, copy=True)
        if marker == "none":
            vals[pd.isna(vals)] = None
        df[c] = pd.Series(vals, index=df.index, dtype=object)
    return df


def save_frames(frames: dict, folder) -> None:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name, df in frames.items():
        p = folder / f"{name}.parquet"
        df.to_parquet(p)
        objects = {c: _marker(df[c]) for c in df.columns if df[c].dtype == object}
        (folder / f"{name}.objects.json").write_text(json.dumps(objects, indent=2) + "\n", newline="\n")
        pd.testing.assert_frame_equal(df, load_frame(folder, name))   # exact round trip, or stop
        print(f"  {name:9s} {len(df):>9,} rows  {p.stat().st_size / 1e6:6.1f} MB", flush=True)