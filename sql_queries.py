"""SQL queries for the customer sales analysis pipeline."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "sales_data.db"


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Create a SQLite connection to the project database."""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def run_query(query: str, db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    """Execute a SQL query and return rows as dictionaries."""
    with get_connection(db_path) as connection:
        rows = connection.execute(query).fetchall()
    return [dict(row) for row in rows]


def top_10_customers_by_revenue(db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    """Return the top 10 customers by total revenue."""
    query = """
        SELECT
            c.customer_id,
            c.first_name,
            c.last_name,
            ROUND(SUM(o.total_amount), 2) AS total_revenue,
            COUNT(o.order_id) AS total_orders
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        WHERE o.order_status != 'Returned'
        GROUP BY c.customer_id, c.first_name, c.last_name
        ORDER BY total_revenue DESC
        LIMIT 10
    """
    return run_query(query, db_path)


def month_over_month_revenue_growth(db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    """Return monthly revenue with month-over-month growth percentages."""
    query = """
        WITH monthly_revenue AS (
            SELECT
                strftime('%Y-%m', order_date) AS month,
                ROUND(SUM(total_amount), 2) AS revenue
            FROM orders
            WHERE order_status != 'Returned'
            GROUP BY strftime('%Y-%m', order_date)
        )
        SELECT
            month,
            revenue,
            LAG(revenue) OVER (ORDER BY month) AS previous_month_revenue,
            ROUND(
                ((revenue - LAG(revenue) OVER (ORDER BY month)) /
                NULLIF(LAG(revenue) OVER (ORDER BY month), 0)) * 100,
                2
            ) AS growth_pct
        FROM monthly_revenue
        ORDER BY month
    """
    return run_query(query, db_path)


def customer_churn_90_days(db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    """Return customers who have not placed an order in the last 90 days."""
    query = """
        SELECT
            c.customer_id,
            c.first_name,
            c.last_name,
            c.segment,
            MAX(o.order_date) AS last_order_date,
            ROUND((julianday('now') - julianday(MAX(o.order_date))), 0) AS days_since_last_order
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name, c.segment
        HAVING MAX(o.order_date) IS NULL
            OR (julianday('now') - julianday(MAX(o.order_date))) >= 90
        ORDER BY days_since_last_order DESC
    """
    return run_query(query, db_path)


def average_order_value_by_segment(db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    """Return average order value by customer segment."""
    query = """
        SELECT
            c.segment,
            ROUND(AVG(o.total_amount), 2) AS avg_order_value,
            COUNT(o.order_id) AS order_count
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        WHERE o.order_status != 'Returned'
        GROUP BY c.segment
        ORDER BY avg_order_value DESC
    """
    return run_query(query, db_path)


def run_all_queries(db_path: Path = DB_PATH) -> dict[str, list[dict[str, Any]]]:
    """Run all business query functions and return them in a dictionary."""
    return {
        "top_customers": top_10_customers_by_revenue(db_path),
        "monthly_revenue": month_over_month_revenue_growth(db_path),
        "churned_customers": customer_churn_90_days(db_path),
        "segment_aov": average_order_value_by_segment(db_path),
    }


def main() -> None:
    """Print each SQL output for quick inspection in the terminal."""
    results = run_all_queries()
    for name, rows in results.items():
        print(f"\n{name.upper()}\n{'=' * 40}")
        for row in rows[:5]:
            print(row)


if __name__ == "__main__":
    main()
