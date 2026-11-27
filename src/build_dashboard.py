"""Build the interactive web dashboard (docs/index.html) from the cleaned data.

Run from the repository root after the notebook:
    python src/build_dashboard.py
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "processed" / "customer_shopping_clean.csv"
TEMPLATE = ROOT / "src" / "dashboard_template.html"
OUT = ROOT / "docs" / "index.html"

COLS = {  # dashboard key -> column in the clean table
    "gender": "gender", "category": "category", "item": "item_purchased",
    "season": "season", "sub": "subscription_status", "ship": "shipping_type",
    "disc": "discount_applied", "age": "age_group", "seg": "customer_segment",
    "pay": "payment_method",
}
ORDER = {
    "age": ["Young Adult", "Adult", "Middle-aged", "Senior"],
    "season": ["Spring", "Summer", "Fall", "Winter"],
    "seg": ["New", "Returning", "Loyal"],
}


def main():
    df = pd.read_csv(CLEAN)
    payload = {"dims": {}, "rows": []}
    codes = {}
    for key, col in COLS.items():
        values = ORDER.get(key) or sorted(df[col].astype(str).unique())
        payload["dims"][key] = values
        codes[key] = df[col].astype(str).map({v: i for i, v in enumerate(values)})
    keys = list(COLS)
    payload["keys"] = keys + ["amt", "rating"]
    for i in range(len(df)):
        payload["rows"].append([int(codes[k].iat[i]) for k in keys]
                               + [int(df["purchase_amount"].iat[i]), round(float(df["review_rating"].iat[i]), 1)])
    html = TEMPLATE.read_text(encoding="utf-8").replace(
        "/*__DATA__*/null", json.dumps(payload, separators=(",", ":")))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(df):,} rows, {OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
