"""End-to-end pipeline entry point for the customer sales analysis project."""

from __future__ import annotations

from pathlib import Path

from generate_data import DB_PATH, generate_database
from pandas_analysis import run_analysis
from sql_queries import run_all_queries
from visualize import create_visualizations


def main() -> None:
    """Run the complete customer sales analysis pipeline."""
    database_path = generate_database()
    print(f"Database generated at: {database_path}")

    sql_results = run_all_queries(DB_PATH)
    print("\nSQL summary results:")
    for query_name, rows in sql_results.items():
        print(f"- {query_name}: {len(rows)} rows")

    analysis = run_analysis(DB_PATH)
    print("\nPandas summary:")
    print(analysis["summary"])

    chart_paths = create_visualizations()
    print("\nChart files created:")
    for label, path in chart_paths.items():
        print(f"- {label}: {path}")

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()
