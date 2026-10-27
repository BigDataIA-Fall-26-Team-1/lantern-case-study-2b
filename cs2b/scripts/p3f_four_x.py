"""P3: the exact-4x filers. Does each fair value appear four times?"""
import pandas as pd

B = pd.read_pickle("outputs/p3_work/baseline.pkl")
k = B["kept"]
for nm in ["STAR MOUNTAIN", "REMORA", "STEELE CREEK"]:
    h = k[k["name"].str.contains(nm) & k["fair_value"].gt(0)]
    mult = h.groupby("fair_value").size()
    print(f"\n=== {nm}: {len(h)} holdings, adsh {h['adsh'].iloc[0]} ===")
    print("times each fair value appears -> number of values:",
          mult.value_counts().sort_index().to_dict())
    v = mult[mult == mult.max()].index[0]
    print(h[h["fair_value"] == v][["identifier", "fair_value", "cost", "principal", "source_rows"]]
          .to_string(index=False, max_colwidth=100))
    