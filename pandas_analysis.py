"""Pandas analysis for the customer sales data pipeline."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from generate_data import DB_PATH as DATA_DB_PATH
from sql_queries import get_connection

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


def load_order_data(db_path: Path = DATA_DB_PATH) -> pd.DataFrame:
    """Load an order-level dataset for customer analytics."""
    query = """
        SELECT
            o.order_id,
            o.customer_id,
            c.segment,
            c.signup_date,
            o.order_date,
            o.total_amount,
            CASE
                WHEN o.order_status = 'Returned' THEN 0
                ELSE 1
            END AS valid_order_flag
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
    """
    with get_connection(db_path) as connection:
        return pd.read_sql_query(query, connection)


def compute_cohort_retention(db_path: Path = DATA_DB_PATH) -> pd.DataFrame:
    """Calculate customer retention by acquisition cohort."""
    orders = load_order_data(db_path)
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders["signup_date"] = pd.to_datetime(orders["signup_date"])

    customer_cohorts = (
        orders.groupby("customer_id", as_index=False)
        .agg(first_order_date=("order_date", "min"), signup_date=("signup_date", "first"))
    )
    customer_cohorts["cohort_month"] = customer_cohorts["first_order_date"].dt.to_period("M").astype(str)

    customer_activity = orders[["customer_id", "order_date"]].drop_duplicates()
    customer_activity["order_month"] = customer_activity["order_date"].dt.to_period("M").astype(str)

    cohort_df = customer_cohorts[["customer_id", "cohort_month"]].merge(
        customer_activity, on="customer_id", how="left"
    )
    cohort_df["months_since_start"] = (
        cohort_df["order_month"].astype(str).str.slice(0, 7).astype("string")
    )

    orders_for_analysis = cohort_df.merge(
        cohort_df.groupby("cohort_month")["customer_id"].nunique().rename("cohort_size").reset_index(),
        on="cohort_month",
        how="left",
    )
    orders_for_analysis["months_since_start"] = (
        (pd.to_datetime(orders_for_analysis["order_month"]) - pd.to_datetime(orders_for_analysis["cohort_month"]))
        .dt.days
        // 30
    )

    retention_by_month = (
        orders_for_analysis.groupby(["cohort_month", "months_since_start"], as_index=False)["customer_id"]
        .nunique()
        .rename(columns={"customer_id": "active_customers"})
    )
    cohort_sizes = (
        orders_for_analysis.groupby("cohort_month", as_index=False)["customer_id"].nunique().rename(columns={"customer_id": "cohort_size"})
    )
    retention_df = retention_by_month.merge(cohort_sizes, on="cohort_month", how="left")
    retention_df["retention_rate"] = retention_df["active_customers"] / retention_df["cohort_size"]
    retention_df = retention_df.sort_values(["cohort_month", "months_since_start"]).reset_index(drop=True)
    return retention_df


def compute_rfm(db_path: Path = DATA_DB_PATH) -> pd.DataFrame:
    """Calculate the RFM score for each customer."""
    query = """
        SELECT
            c.customer_id,
            c.segment,
            MAX(o.order_date) AS last_order_date,
            COUNT(o.order_id) AS frequency,
            ROUND(SUM(o.total_amount), 2) AS monetary
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.segment
    """
    with get_connection(db_path) as connection:
        rfm = pd.read_sql_query(query, connection)

    rfm["last_order_date"] = pd.to_datetime(rfm["last_order_date"])
    snapshot_date = rfm["last_order_date"].max() + pd.Timedelta(days=1)
    rfm["recency_days"] = (snapshot_date - rfm["last_order_date"]).dt.days
    rfm["frequency"] = rfm["frequency"].fillna(0).astype(int)
    rfm["monetary"] = rfm["monetary"].fillna(0.0)
    rfm["R_score"] = pd.qcut(rfm["recency_days"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1], duplicates="drop")
    rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5], duplicates="drop")

    def segment_customer(row: pd.Series) -> str:
        if row["R_score"] >= 4 and row["F_score"] >= 4 and row["M_score"] >= 4:
            return "VIP"
        if row["R_score"] >= 3 and row["F_score"] >= 3 and row["M_score"] >= 3:
            return "Loyal"
        if row["R_score"] >= 2 and row["F_score"] >= 2:
            return "At Risk"
        return "Churned"

    rfm["rfm_segment"] = rfm.apply(segment_customer, axis=1)
    return rfm


def summary_statistics(db_path: Path = DATA_DB_PATH) -> dict[str, Any]:
    """Return a concise summary of the dataset metrics."""
    orders = load_order_data(db_path)
    rfm = compute_rfm(db_path)

    summary = {
        "total_customers": int(orders["customer_id"].nunique()),
        "total_orders": int(len(orders)),
        "avg_order_value": float(orders.loc[orders["valid_order_flag"] == 1, "total_amount"].mean()),
        "total_revenue": float(orders.loc[orders["valid_order_flag"] == 1, "total_amount"].sum()),
        "avg_frequency": float(rfm["frequency"].mean()),
        "avg_recency_days": float(rfm["recency_days"].mean()),
        "segment_distribution": rfm["rfm_segment"].value_counts().to_dict(),
    }
    return summary


def run_analysis(db_path: Path = DATA_DB_PATH) -> dict[str, pd.DataFrame | dict[str, Any]]:
    """Run the complete pandas analysis workflow and return major outputs."""
    retention = compute_cohort_retention(db_path)
    rfm = compute_rfm(db_path)
    stats = summary_statistics(db_path)
    return {
        "retention": retention,
        "rfm": rfm,
        "summary": stats,
    }


def main() -> None:
    """Print the retention and RFM analysis outputs."""
    analysis = run_analysis()
    print("SUMMARY STATISTICS")
    print(analysis["summary"])
    print("\nRFM SEGMENTS")
    print(analysis["rfm"]["rfm_segment"].value_counts().to_string())
    print("\nRETENTION SAMPLE")
    print(analysis["retention"].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
