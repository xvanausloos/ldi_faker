import argparse
import os
import sqlite3
from dataclasses import dataclass
from typing import Dict

from faker import Faker


@dataclass
class PiiMaps:
    first_name: Dict[str, str]
    last_name: Dict[str, str]
    address: Dict[str, str]


def _connect(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS orders_pseudo;
        DROP TABLE IF EXISTS accounts_pseudo;
        DROP TABLE IF EXISTS customers_pseudo;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS accounts;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            address TEXT NOT NULL
        );

        CREATE TABLE accounts (
            account_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            contact_firstname TEXT NOT NULL,
            contact_lastname TEXT NOT NULL,
            billing_address TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            account_id INTEGER NOT NULL,
            recipient_firstname TEXT NOT NULL,
            recipient_lastname TEXT NOT NULL,
            shipping_address TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        );

        CREATE TABLE customers_pseudo (
            customer_id INTEGER PRIMARY KEY,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            address TEXT NOT NULL
        );

        CREATE TABLE accounts_pseudo (
            account_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            contact_firstname TEXT NOT NULL,
            contact_lastname TEXT NOT NULL,
            billing_address TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers_pseudo(customer_id)
        );

        CREATE TABLE orders_pseudo (
            order_id INTEGER PRIMARY KEY,
            account_id INTEGER NOT NULL,
            recipient_firstname TEXT NOT NULL,
            recipient_lastname TEXT NOT NULL,
            shipping_address TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts_pseudo(account_id)
        );
        """
    )
    conn.commit()


def seed_source_data(
    conn: sqlite3.Connection,
    rows_per_table: int = 100,
    locale: str = "en_US",
    seed: int = 42,
) -> None:
    faker = Faker(locale)
    Faker.seed(seed)

    for idx in range(1, rows_per_table + 1):
        first = faker.first_name()
        last = faker.last_name()
        home = faker.address().replace("\n", ", ")

        conn.execute(
            """
            INSERT INTO customers(customer_id, firstname, lastname, address)
            VALUES(?, ?, ?, ?)
            """,
            (idx, first, last, home),
        )

        conn.execute(
            """
            INSERT INTO accounts(
                account_id,
                customer_id,
                contact_firstname,
                contact_lastname,
                billing_address
            )
            VALUES(?, ?, ?, ?, ?)
            """,
            (idx, idx, first, last, home),
        )

        ship_first = faker.first_name()
        ship_last = faker.last_name()
        ship_addr = faker.address().replace("\n", ", ")

        conn.execute(
            """
            INSERT INTO orders(
                order_id,
                account_id,
                recipient_firstname,
                recipient_lastname,
                shipping_address
            )
            VALUES(?, ?, ?, ?, ?)
            """,
            (idx, idx, ship_first, ship_last, ship_addr),
        )

    conn.commit()


def _pseudo_firstname(maps: PiiMaps, faker: Faker, value: str) -> str:
    if value not in maps.first_name:
        maps.first_name[value] = faker.first_name()
    return maps.first_name[value]


def _pseudo_lastname(maps: PiiMaps, faker: Faker, value: str) -> str:
    if value not in maps.last_name:
        maps.last_name[value] = faker.last_name()
    return maps.last_name[value]


def _pseudo_address(maps: PiiMaps, faker: Faker, value: str) -> str:
    if value not in maps.address:
        maps.address[value] = faker.address().replace("\n", ", ")
    return maps.address[value]


def pseudonymize_data(
    conn: sqlite3.Connection,
    locale: str = "en_US",
    seed: int = 1234,
) -> None:
    faker = Faker(locale)
    Faker.seed(seed)
    maps = PiiMaps(first_name={}, last_name={}, address={})

    customers = conn.execute(
        """
        SELECT customer_id, firstname, lastname, address
        FROM customers
        ORDER BY customer_id
        """
    ).fetchall()

    for customer_id, firstname, lastname, address in customers:
        conn.execute(
            """
            INSERT INTO customers_pseudo(
                customer_id,
                firstname,
                lastname,
                address
            )
            VALUES(?, ?, ?, ?)
            """,
            (
                customer_id,
                _pseudo_firstname(maps, faker, firstname),
                _pseudo_lastname(maps, faker, lastname),
                _pseudo_address(maps, faker, address),
            ),
        )

    accounts = conn.execute(
        """
        SELECT
            account_id,
            customer_id,
            contact_firstname,
            contact_lastname,
            billing_address
        FROM accounts
        ORDER BY account_id
        """
    ).fetchall()

    for (
        account_id,
        customer_id,
        contact_first,
        contact_last,
        billing_addr,
    ) in accounts:
        conn.execute(
            """
            INSERT INTO accounts_pseudo(
                account_id,
                customer_id,
                contact_firstname,
                contact_lastname,
                billing_address
            )
            VALUES(?, ?, ?, ?, ?)
            """,
            (
                account_id,
                customer_id,
                _pseudo_firstname(maps, faker, contact_first),
                _pseudo_lastname(maps, faker, contact_last),
                _pseudo_address(maps, faker, billing_addr),
            ),
        )

    orders = conn.execute(
        """
        SELECT
            order_id,
            account_id,
            recipient_firstname,
            recipient_lastname,
            shipping_address
        FROM orders
        ORDER BY order_id
        """
    ).fetchall()

    for (
        order_id,
        account_id,
        recipient_first,
        recipient_last,
        shipping_addr,
    ) in orders:
        conn.execute(
            """
            INSERT INTO orders_pseudo(
                order_id,
                account_id,
                recipient_firstname,
                recipient_lastname,
                shipping_address
            )
            VALUES(?, ?, ?, ?, ?)
            """,
            (
                order_id,
                account_id,
                _pseudo_firstname(maps, faker, recipient_first),
                _pseudo_lastname(maps, faker, recipient_last),
                _pseudo_address(maps, faker, shipping_addr),
            ),
        )

    conn.commit()


def verify_relationships(conn: sqlite3.Connection, rows_per_table: int) -> None:
    checks = [
        ("customers count", "SELECT COUNT(*) FROM customers", rows_per_table),
        ("accounts count", "SELECT COUNT(*) FROM accounts", rows_per_table),
        ("orders count", "SELECT COUNT(*) FROM orders", rows_per_table),
        (
            "customers_pseudo count",
            "SELECT COUNT(*) FROM customers_pseudo",
            rows_per_table,
        ),
        (
            "accounts_pseudo count",
            "SELECT COUNT(*) FROM accounts_pseudo",
            rows_per_table,
        ),
        (
            "orders_pseudo count",
            "SELECT COUNT(*) FROM orders_pseudo",
            rows_per_table,
        ),
        (
            "source chain join count",
            """
            SELECT COUNT(*)
            FROM orders o
            JOIN accounts a ON o.account_id = a.account_id
            JOIN customers c ON a.customer_id = c.customer_id
            """,
            rows_per_table,
        ),
        (
            "pseudo chain join count",
            """
            SELECT COUNT(*)
            FROM orders_pseudo o
            JOIN accounts_pseudo a ON o.account_id = a.account_id
            JOIN customers_pseudo c ON a.customer_id = c.customer_id
            """,
            rows_per_table,
        ),
    ]

    for check_name, query, expected in checks:
        actual = conn.execute(query).fetchone()[0]
        if actual != expected:
            raise ValueError(
                f"Verification failed for {check_name}: "
                f"expected {expected}, got {actual}"
            )


def run_relational_demo(
    db_path: str = "data/pii_relational_demo.db",
    rows_per_table: int = 100,
    locale: str = "en_US",
) -> None:
    conn = _connect(db_path)
    try:
        create_schema(conn)
        seed_source_data(
            conn,
            rows_per_table=rows_per_table,
            locale=locale,
            seed=42,
        )
        pseudonymize_data(conn, locale=locale, seed=1234)
        verify_relationships(conn, rows_per_table=rows_per_table)
    finally:
        conn.close()

    print(f"Created SQLite demo DB: {db_path}")
    print(
        f"Generated {rows_per_table} rows in each source table and pseudo table.",
    )
    print(
        "Relationships preserved after pseudonymization "
        "(verification passed).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build relational SQLite demo with Faker pseudonymization",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="data/pii_relational_demo.db",
        help="SQLite database path",
    )
    parser.add_argument(
        "--rows-per-table",
        type=int,
        default=100,
        help="Rows to generate in each table",
    )
    parser.add_argument(
        "--locale",
        type=str,
        default="en_US",
        help="Faker locale",
    )
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    run_relational_demo(
        db_path=args.db_path,
        rows_per_table=args.rows_per_table,
        locale=args.locale,
    )
