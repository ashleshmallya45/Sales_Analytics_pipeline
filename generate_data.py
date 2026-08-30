"""Generate realistic e-commerce sales data and populate a SQLite database.

This script creates a small but realistic retail dataset with customers, products,
orders, and order items suitable for SQL and pandas analysis.
"""

from __future__ import annotations

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

from faker import Faker


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "sales_data.db"


def create_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Create a SQLite connection and ensure the parent directory exists."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Create the SQLite tables used in the e-commerce dataset."""
    conn.execute("DROP TABLE IF EXISTS order_items")
    conn.execute("DROP TABLE IF EXISTS orders")
    conn.execute("DROP TABLE IF EXISTS products")
    conn.execute("DROP TABLE IF EXISTS customers")

    conn.execute(
        """
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            segment TEXT NOT NULL,
            signup_date TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            brand TEXT NOT NULL,
            unit_cost REAL NOT NULL,
            unit_price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            order_status TEXT NOT NULL,
            subtotal REAL NOT NULL,
            tax_amount REAL NOT NULL,
            shipping_cost REAL NOT NULL,
            total_amount REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            line_total REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
        """
    )

    conn.commit()


def generate_customers(fake: Faker, count: int = 500) -> list[tuple]:
    """Create customer records with realistic profile metadata."""
    segments = ["New", "Returning", "Loyal", "VIP"]
    customers: list[tuple] = []

    for customer_id in range(1, count + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        segment = random.choices(segments, weights=[0.25, 0.35, 0.25, 0.15], k=1)[0]
        signup_date = fake.date_between(start_date="-1200d", end_date="today").isoformat()
        city = fake.city()
        state = fake.state_abbr()
        is_active = 1 if random.random() < 0.9 else 0
        customers.append(
            (
                customer_id,
                first_name,
                last_name,
                email,
                segment,
                signup_date,
                city,
                state,
                is_active,
            )
        )

    return customers


def generate_products(fake: Faker) -> list[tuple]:
    """Create 30 realistic products across common retail categories."""
    product_templates: list[dict] = [
        {"name": "Wireless Noise Cancelling Headphones", "category": "Electronics", "brand": "Auralis", "unit_cost": 120.0},
        {"name": "4K Smart TV", "category": "Electronics", "brand": "Vanta", "unit_cost": 550.0},
        {"name": "Mechanical Keyboard", "category": "Electronics", "brand": "KeyForge", "unit_cost": 95.0},
        {"name": "Gaming Mouse", "category": "Electronics", "brand": "PulseX", "unit_cost": 45.0},
        {"name": "USB-C Charging Cable", "category": "Electronics", "brand": "VoltEdge", "unit_cost": 12.0},
        {"name": "Fitness Tracker", "category": "Electronics", "brand": "MoveFit", "unit_cost": 75.0},
        {"name": "Bluetooth Speaker", "category": "Electronics", "brand": "EchoWave", "unit_cost": 80.0},
        {"name": "Laptop Stand", "category": "Office", "brand": "FlexDock", "unit_cost": 32.0},
        {"name": "Ergonomic Office Chair", "category": "Office", "brand": "ComfortPro", "unit_cost": 210.0},
        {"name": "Standing Desk Converter", "category": "Office", "brand": "DeskRise", "unit_cost": 170.0},
        {"name": "Premium Notebook Set", "category": "Office", "brand": "PageCraft", "unit_cost": 22.0},
        {"name": "Leather Wallet", "category": "Accessories", "brand": "Northline", "unit_cost": 35.0},
        {"name": "Travel Backpack", "category": "Accessories", "brand": "SummitOut", "unit_cost": 72.0},
        {"name": "Sunglasses", "category": "Accessories", "brand": "Lensora", "unit_cost": 48.0},
        {"name": "Wristwatch", "category": "Accessories", "brand": "Timexia", "unit_cost": 160.0},
        {"name": "Cotton T-Shirt", "category": "Apparel", "brand": "Harbor", "unit_cost": 18.0},
        {"name": "Classic Denim Jeans", "category": "Apparel", "brand": "Ridges", "unit_cost": 42.0},
        {"name": "Running Sneakers", "category": "Apparel", "brand": "StrideOne", "unit_cost": 68.0},
        {"name": "Winter Jacket", "category": "Apparel", "brand": "NorthPeak", "unit_cost": 120.0},
        {"name": "Leather Belt", "category": "Apparel", "brand": "Harbor", "unit_cost": 30.0},
        {"name": "Ceramic Coffee Mug", "category": "Home", "brand": "GroveLine", "unit_cost": 16.0},
        {"name": "Smart Home Lightbulb", "category": "Home", "brand": "LumaNest", "unit_cost": 25.0},
        {"name": "Air Purifier", "category": "Home", "brand": "PureAura", "unit_cost": 140.0},
        {"name": "Kitchen Blender", "category": "Home", "brand": "FreshBlend", "unit_cost": 60.0},
        {"name": "Throw Blanket", "category": "Home", "brand": "CozyNest", "unit_cost": 28.0},
        {"name": "Portable Blender Bottle", "category": "Fitness", "brand": "ShapeMove", "unit_cost": 19.0},
        {"name": "Yoga Mat", "category": "Fitness", "brand": "FlowLand", "unit_cost": 34.0},
        {"name": "Resistance Bands Set", "category": "Fitness", "brand": "CoreLift", "unit_cost": 24.0},
        {"name": "Running Water Bottle", "category": "Fitness", "brand": "HydraPeak", "unit_cost": 17.0},
        {"name": "Smart Pressure Cooker", "category": "Home", "brand": "QuickHeat", "unit_cost": 90.0},
    ]

    products: list[tuple] = []
    for product_id, template in enumerate(product_templates, start=1):
        unit_cost = template["unit_cost"]
        unit_price = round(unit_cost * random.uniform(1.45, 2.1), 2)
        stock_quantity = random.randint(15, 350)
        products.append(
            (
                product_id,
                template["name"],
                template["category"],
                template["brand"],
                round(unit_cost, 2),
                round(unit_price, 2),
                stock_quantity,
                1,
            )
        )

    return products


def generate_orders(
    customers: Iterable[tuple],
    products: Iterable[tuple],
    fake: Faker,
    order_count: int = 2200,
) -> tuple[list[tuple], list[tuple]]:
    """Generate orders and order items using a realistic purchase pattern."""
    customer_ids = [customer[0] for customer in customers]
    product_rows = list(products)

    orders: list[tuple] = []
    order_items: list[tuple] = []

    for order_id in range(1, order_count + 1):
        customer_id = random.choice(customer_ids)
        order_date = fake.date_between(start_date="-600d", end_date="today").isoformat()
        status = random.choices(
            ["Completed", "Shipped", "Processing", "Returned"],
            weights=[0.72, 0.15, 0.08, 0.05],
            k=1,
        )[0]
        item_count = random.randint(1, 5)
        chosen_products = random.sample(product_rows, k=item_count)

        subtotal = 0.0
        item_lines: list[tuple] = []

        for product in chosen_products:
            product_id = product[0]
            unit_price = float(product[5])
            quantity = random.randint(1, 3)
            line_total = round(unit_price * quantity, 2)
            subtotal += line_total
            item_lines.append(
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                    line_total,
                )
            )

        tax_amount = round(subtotal * 0.08, 2)
        shipping_cost = round(7.99 if subtotal < 75 else 0.0, 2)
        total_amount = round(subtotal + tax_amount + shipping_cost, 2)

        orders.append(
            (
                order_id,
                customer_id,
                order_date,
                status,
                round(subtotal, 2),
                tax_amount,
                shipping_cost,
                total_amount,
            )
        )

        for idx, line in enumerate(item_lines, start=1):
            order_items.append(
                (
                    (order_id * 1000) + idx,
                    order_id,
                    line[1],
                    line[2],
                    line[3],
                    line[4],
                )
            )

    return orders, order_items


def insert_data(conn: sqlite3.Connection, customers: list[tuple], products: list[tuple], orders: list[tuple], order_items: list[tuple]) -> None:
    """Insert all generated records into the SQLite database."""
    conn.executemany(
        """
        INSERT INTO customers (
            customer_id, first_name, last_name, email, segment, signup_date,
            city, state, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        customers,
    )

    conn.executemany(
        """
        INSERT INTO products (
            product_id, product_name, category, brand, unit_cost, unit_price,
            stock_quantity, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        products,
    )

    conn.executemany(
        """
        INSERT INTO orders (
            order_id, customer_id, order_date, order_status, subtotal,
            tax_amount, shipping_cost, total_amount
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        orders,
    )

    conn.executemany(
        """
        INSERT INTO order_items (
            order_item_id, order_id, product_id, quantity, unit_price, line_total
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        order_items,
    )

    conn.commit()


def generate_database(db_path: Path = DB_PATH, customer_count: int = 500, order_count: int = 2200) -> Path:
    """Create and populate the sales database for the project."""
    fake = Faker()
    random.seed(42)

    conn = create_connection(db_path)
    create_schema(conn)

    customers = generate_customers(fake, count=customer_count)
    products = generate_products(fake)
    orders, order_items = generate_orders(customers, products, fake, order_count=order_count)
    insert_data(conn, customers, products, orders, order_items)

    conn.close()
    return db_path


def main() -> None:
    """Run the database generation workflow."""
    customer_count = 500
    order_count = 2200
    output_path = generate_database(customer_count=customer_count, order_count=order_count)
    print(f"Database created successfully at: {output_path}")
    print(f"Customers: {customer_count}")
    print(f"Products: {len(generate_products(Faker()))}")
    print(f"Orders: {order_count}")


if __name__ == "__main__":
    main()
