"""Create visual outputs for the customer sales analysis pipeline."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from generate_data import DB_PATH as DATA_DB_PATH
from pandas_analysis import compute_cohort_retention, compute_rfm, load_order_data
from sql_queries import month_over_month_revenue_growth

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


def ensure_output_dir(output_dir: Path = OUTPUT_DIR) -> Path:
    """Create the output directory if it does not exist."""
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def plot_revenue_trend(output_dir: Path = OUTPUT_DIR, db_path: Path = DATA_DB_PATH) -> Path:
    """Save a revenue trend line chart by month."""
    monthly = pd.DataFrame(month_over_month_revenue_growth(db_path))
    if monthly.empty:
        raise ValueError("No monthly revenue data available.")

    monthly["month"] = pd.to_datetime(monthly["month"].astype(str) + "-01")
    monthly["revenue"] = pd.to_numeric(monthly["revenue"], errors="coerce")
    monthly["growth_pct"] = pd.to_numeric(monthly["growth_pct"], errors="coerce")

    plt.figure(figsize=(10, 5))
    sns.lineplot(data=monthly, x="month", y="revenue", marker="o")
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    file_path = ensure_output_dir(output_dir) / "revenue_trend.png"
    plt.savefig(file_path, dpi=200)
    plt.close()
    return file_path


def plot_customer_segments(output_dir: Path = OUTPUT_DIR, db_path: Path = DATA_DB_PATH) -> Path:
    """Save a customer segment distribution bar chart."""
    rfm = compute_rfm(db_path)
    segment_counts = rfm["rfm_segment"].value_counts().reset_index()
    segment_counts.columns = ["segment", "count"]

    plt.figure(figsize=(8, 6))
    sns.barplot(data=segment_counts, x="segment", y="count", hue="segment", palette="viridis", dodge=False, legend=False)
    plt.title("Customer Segment Distribution")
    plt.xlabel("Segment")
    plt.ylabel("Customers")
    plt.tight_layout()

    file_path = ensure_output_dir(output_dir) / "customer_segments.png"
    plt.savefig(file_path, dpi=200)
    plt.close()
    return file_path


def plot_retention_curve(output_dir: Path = OUTPUT_DIR, db_path: Path = DATA_DB_PATH) -> Path:
    """Save a retention curve chart by cohort month."""
    retention = compute_cohort_retention(db_path)
    if retention.empty:
        raise ValueError("No retention data available.")

    retention["retention_rate"] = pd.to_numeric(retention["retention_rate"], errors="coerce")
    retention = retention.sort_values(["cohort_month", "months_since_start"])

    plt.figure(figsize=(10, 6))
    for cohort, group in retention.groupby("cohort_month"):
        plt.plot(group["months_since_start"], group["retention_rate"], marker="o", label=cohort)

    plt.title("Cohort Retention Curve")
    plt.xlabel("Months Since First Purchase")
    plt.ylabel("Retention Rate")
    plt.legend(title="Cohort", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()

    file_path = ensure_output_dir(output_dir) / "retention_curve.png"
    plt.savefig(file_path, dpi=200)
    plt.close()
    return file_path


def create_visualizations(output_dir: Path = OUTPUT_DIR, db_path: Path = DATA_DB_PATH) -> dict[str, Path]:
    """Generate all chart outputs for the project."""
    return {
        "revenue_trend": plot_revenue_trend(output_dir, db_path),
        "customer_segments": plot_customer_segments(output_dir, db_path),
        "retention_curve": plot_retention_curve(output_dir, db_path),
    }


def main() -> None:
    """Generate and save the output charts."""
    outputs = create_visualizations()
    print("Saved charts:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
