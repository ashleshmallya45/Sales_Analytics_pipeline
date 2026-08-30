# Customer Sales Analysis Pipeline

## Executive Summary

This project models a real e-commerce revenue and retention problem: how do we identify the customers driving profit, where is revenue growth slowing, and which customers are at risk of churn before they stop buying?

I built a complete Python analytics pipeline using SQLite, SQL, pandas, and visualization libraries to answer those questions on a realistic synthetic dataset of 500 customers, 30 products, and 2,200 orders. The project combines SQL-based business reporting with advanced customer analytics to highlight actionable retention opportunities.

The analysis surfaced several business-critical signals:

- 248 customers were inactive for 90+ days, representing a meaningful portion of the customer base that may need reactivation or retention outreach.
- The top 10 customers generated a large share of revenue, showing concentration risk and the value of customer-level segmentation.
- Monthly revenue varied meaningfully over time, which suggests a need to understand seasonality and order timing rather than treating customer behavior as static.

This project demonstrates the kind of analytics work a data analyst would use to support growth, retention, and customer value decisions in an e-commerce or subscription business.

## Business Problem

A retail company wants to understand:

- which customers generate the most revenue,
- how monthly sales change over time,
- when customers become inactive,
- how customer segments differ in shopping behavior,
- and which retention patterns are worth acting on.

The project simulates a realistic e-commerce dataset and answers those questions with SQL, Python, and data visualization.

## Key Insights

- The top 10 customers contributed a disproportionate share of total revenue, indicating heavy concentration among a small set of high-value accounts.
- 248 customers had no purchases in the previous 90 days, suggesting a meaningful risk of churn or reduced engagement that could be addressed through lifecycle campaigns.
- Average order value varied by segment, which means customer behavior is not uniform and different cohorts may need different offers or retention strategies.
- Revenue and retention patterns show that customer value is driven not just by one-time purchases, but by repeat behavior and consistent engagement over time.

## Project Structure

```text
Customer_Sales_Analysis_Pipeline/
├── data/
│   └── sales_data.db
├── output/
│   └── charts and summary exports
├── src/
│   └── package utilities (if expanded later)
├── generate_data.py
├── sql_queries.py
├── pandas_analysis.py
├── visualize.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore (optional)
```

## Data Model

The SQLite database contains four core tables:

- customers: customer profile information and segment tags
- products: product catalog with brand, category, and pricing
- orders: order headers including date, status, and totals
- order_items: line-level product purchases inside each order

The synthetic dataset includes 500 customers, 30 products, and 2,200 orders with realistic e-commerce behavior.

## Workflow

1. Generate the database using Faker.
2. Run SQL queries to capture business KPIs.
3. Pull results into pandas for deeper segmentation and cohort analysis.
4. Visualize key trends and retention metrics.
5. Execute the full pipeline from a central entry point.

## Key Business Questions Answered

- Top 10 customers by total revenue
- Month-over-month revenue growth
- Customer churn for customers inactive for 90+ days
- Average order value by customer segment
- Cohort retention analysis
- RFM segmentation (Recency, Frequency, Monetary)

## Tools Used

- SQLite for transactional data storage
- Python for orchestration and data processing
- pandas for tabular analysis
- matplotlib and seaborn for visual output
- Faker for realistic synthetic data generation

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python generate_data.py
python main.py
```

## Example Insights

This project is designed to surface insights such as:

- high-value customer retention patterns,
- slow-selling or low-engagement customer cohorts,
- revenue seasonality and growth trends,
- customer segment differences in order size and frequency.

## Portfolio Value

This pipeline is useful for demonstrating:

- SQL reporting skills,
- data modeling and database design,
- Python automation for ETL and analysis,
- customer analytics and retention analysis,
- and the ability to communicate business value through dashboards and visual summaries.
