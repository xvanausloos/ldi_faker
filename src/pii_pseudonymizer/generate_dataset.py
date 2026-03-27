import argparse
import csv
import os

from faker import Faker


def generate_dataset(
    rows: int,
    output_path: str,
    locale: str = "en_US",
    seed: int = 42,
) -> None:
    faker = Faker(locale)
    Faker.seed(seed)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["id", "firstname", "lastname", "address"],
        )
        writer.writeheader()

        for idx in range(1, rows + 1):
            writer.writerow(
                {
                    "id": idx,
                    "firstname": faker.first_name(),
                    "lastname": faker.last_name(),
                    "address": faker.address().replace("\n", ", "),
                }
            )

    print(f"Generated {rows} rows with PII into: {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate sample CSV dataset with PII",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=50,
        help="Number of records to generate",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/input_pii.csv",
        help="Output CSV path",
    )
    parser.add_argument("--locale", type=str, default="en_US", help="Faker locale")
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    generate_dataset(
        rows=args.rows,
        output_path=args.output,
        locale=args.locale,
        seed=args.seed,
    )
