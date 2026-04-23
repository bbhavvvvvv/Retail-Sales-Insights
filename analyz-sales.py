"""Analyze retail sales data and export summary files."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("outputs/.matplotlib").resolve()))
os.environ.setdefault("XDG_CACHE_HOME", str(Path("outputs/.cache").resolve()))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


REQUIRED_COLUMNS = {
    "order_date",
    "region",
    "category",
    "product",
    "sales_rep",
    "customer_type",
    "payment_method",
    "units_sold",
    "unit_price",
    "discount_pct",
    "revenue",
}


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_list}")

    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


def save_bar_chart(series: pd.Series, title: str, ylabel: str, output_path: Path) -> None:
    plt.figure(figsize=(10, 5))
    series.plot(kind="bar", color="#2E86AB")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_line_chart(series: pd.Series, title: str, ylabel: str, output_path: Path) -> None:
    plt.figure(figsize=(10, 5))
    series.plot(kind="line", marker="o", color="#F18F01")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def write_report(
    output_path: Path,
    df: pd.DataFrame,
    monthly_revenue: pd.Series,
    revenue_by_region: pd.Series,
    revenue_by_category: pd.Series,
    top_products: pd.DataFrame,
) -> None:
    total_revenue = df["revenue"].sum()
    total_orders = len(df)
    total_units = int(df["units_sold"].sum())
    avg_order_value = total_revenue / total_orders
    best_month = monthly_revenue.idxmax()
    best_region = revenue_by_region.idxmax()
    best_category = revenue_by_category.idxmax()

    report = f"""# Sales Analysis Report

## Overview

- Total revenue: ${total_revenue:,.2f}
- Total orders: {total_orders}
- Total units sold: {total_units}
- Average order value: ${avg_order_value:,.2f}

## Key findings

- Best month by revenue: {best_month} (${monthly_revenue.max():,.2f})
- Top region: {best_region} (${revenue_by_region.max():,.2f})
- Best-performing category: {best_category} (${revenue_by_category.max():,.2f})
- Top product by revenue: {top_products.iloc[0]["product"]} (${top_products.iloc[0]["revenue"]:,.2f})

## Notes

This report was generated automatically from the CSV input file. Use the CSV summaries
and charts in the output folder for deeper analysis or visualization work.
"""
    output_path.write_text(report)


def analyze(input_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_data(input_path)

    monthly_revenue = df.groupby("month")["revenue"].sum().round(2)
    revenue_by_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False).round(2)
    revenue_by_category = df.groupby("category")["revenue"].sum().sort_values(ascending=False).round(2)
    top_products = (
        df.groupby("product", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .head(10)
        .round(2)
    )

    monthly_revenue.to_csv(output_dir / "monthly_revenue.csv", header=["revenue"])
    revenue_by_region.to_csv(output_dir / "revenue_by_region.csv", header=["revenue"])
    revenue_by_category.to_csv(output_dir / "revenue_by_category.csv", header=["revenue"])
    top_products.to_csv(output_dir / "top_products.csv", index=False)

    save_line_chart(
        monthly_revenue,
        title="Monthly Revenue Trend",
        ylabel="Revenue",
        output_path=output_dir / "monthly_revenue.png",
    )
    save_bar_chart(
        revenue_by_region,
        title="Revenue by Region",
        ylabel="Revenue",
        output_path=output_dir / "revenue_by_region.png",
    )

    write_report(
        output_path=output_dir / "report.md",
        df=df,
        monthly_revenue=monthly_revenue,
        revenue_by_region=revenue_by_region,
        revenue_by_category=revenue_by_category,
        top_products=top_products,
    )

    print(f"Analysis complete. Files saved to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze retail sales data")
    parser.add_argument("--input", type=Path, required=True, help="Path to sales CSV")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory for analysis outputs",
    )
    args = parser.parse_args()

    analyze(input_path=args.input, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
