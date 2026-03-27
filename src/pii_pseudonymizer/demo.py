from src.pii_pseudonymizer.relational_db import run_relational_demo


def run_demo() -> None:
    run_relational_demo(
        db_path="data/pii_relational_demo.db",
        rows_per_table=100,
        locale="en_US",
    )
    print("\nRelational demo complete.")


if __name__ == "__main__":
    run_demo()
