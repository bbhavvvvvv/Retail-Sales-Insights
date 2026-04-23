"""Generate a synthetic retail sales dataset for local analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PRODUCT_CATALOG = {
    "Electronics": [
        ("Laptop", 950),
        ("Headphones", 120),
        ("Smartphone", 780),
        ("Monitor", 260),
    ],
    "Furniture": [
        ("Desk", 320),
        ("Office Chair", 210),
        ("Bookshelf", 180),
        ("Lamp", 45),
    ],
    "Office Supplies": [
        ("Notebook Pack", 18),
        ("Printer Paper", 12),
        ("Pen Set", 9),
        ("Stapler", 14),
    ],
    "Clothing": [
        ("Jacket", 85),
        ("Jeans", 55),
        ("Sneakers", 95),
        ("T-Shirt", 25),
    ],
}

REGIONS = ["North", "South", "East", "West"]
SALES_REPS = ["Aisha", "Daniel", "Meera", "Rohan", "Sara", "Vikram"]
CUSTOMER_TYPES = ["Consumer", "Corporate", "Small Business"]
PAYMENT_METHODS = ["Card", "UPI", "Bank Transfer", "Cash"]


def generate_dataset(rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=365, freq="D")

    records: list[dict[str, object]] = []
    categories = list(PRODUCT_CATALOG.keys())

    for _ in range(rows):
        category = rng.choice(categories, p=[0.35, 0.2, 0.25, 0.2])
        product_name, base_price = PRODUCT_CATALOG[category][rng.integers(0, len(PRODUCT_CATALOG[category]))]

        units_sold = int(rng.integers(1, 8))
        seasonal_boost = 1.1 if category == "Electronics" else 1.0
        price_noise = rng.normal(1.0, 0.08)
        unit_price = round(base_price * seasonal_boost * max(price_noise, 0.75), 2)

        discount_pct = round(float(rng.choice([0, 0.05, 0.1, 0.15], p=[0.45, 0.3, 0.2, 0.05])), 2)
        revenue = round(units_sold * unit_price * (1 - discount_pct), 2)

        records.append(
            {
                "order_date": pd.Timestamp(rng.choice(dates)).date().isoformat(),
                "region": str(rng.choice(REGIONS)),
                "category": category,
                "product": product_name,
                "sales_rep": str(rng.choice(SALES_REPS)),
                "customer_type": str(rng.choice(CUSTOMER_TYPES, p=[0.55, 0.25, 0.2])),
                "payment_method": str(rng.choice(PAYMENT_METHODS, p=[0.45, 0.25, 0.2, 0.1])),
                "units_sold": units_sold,
                "unit_price": unit_price,
                "discount_pct": discount_pct,
                "revenue": revenue,
            }
        )

    df = pd.DataFrame(records)
    return df.sort_values("order_date").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic retail sales data")
    parser.add_argument("--rows", type=int, default=500, help="Number of rows to generate")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/sales_data.csv"),
        help="Where to save the dataset",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    df = generate_dataset(rows=args.rows, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Generated {len(df)} rows at {args.output}")


if __name__ == "__main__":
    main()
