# Faker Relational PII Pseudonymization Demo

Small Python project to:
- generate a relational SQLite dataset with 3 related tables containing PII
- generate 100 rows in each source table
- pseudonymize PII with Faker into mirror tables
- keep primary/foreign keys unchanged so relationships are preserved

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run relational demo

```bash
python -m src.pii_pseudonymizer.relational_db --db-path data/pii_relational_demo.db --rows-per-table 100
```

## One-command demo

```bash
python -m src.pii_pseudonymizer.demo
```

The command creates six tables:
- source: `customers`, `accounts`, `orders`
- pseudonymized mirrors: `customers_pseudo`, `accounts_pseudo`, `orders_pseudo`

Relationships:
- `accounts.customer_id -> customers.customer_id`
- `orders.account_id -> accounts.account_id`
- pseudo tables keep the same relationships with `_pseudo` targets.

## Relationship-preserving pseudocode

```text
create faker instance for pseudonymization
create empty deterministic mapping dictionaries:
  first_name_map, last_name_map, address_map

for each source table row:
  keep id columns unchanged (customer_id/account_id/order_id and foreign keys)

  pseudo firstname/lastname/address using deterministic maps
  insert into *_pseudo tables with same PK/FK values

verify row counts and join counts are the same for source and pseudo chains
```

This proves Faker-based pseudonymization can hide PII while preserving
relational integrity for joins.
