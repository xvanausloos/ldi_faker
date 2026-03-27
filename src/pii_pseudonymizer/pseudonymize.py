import argparse
import csv
import os
from typing import Dict

from faker import Faker


def pseudonymize_dataset(
    input_path: str,
    output_path: str,
    locale: str = "en_US",
    seed: int = 1234,
) -> None:
    faker = Faker(locale)
    Faker.seed(seed)

    first_name_map: Dict[str, str] = {}
    last_name_map: Dict[str, str] = {}
    address_map: Dict[str, str] = {}

    with open(input_path, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=["id", "firstname", "lastname", "address"],
        )
        writer.writeheader()

        for row in rows:
            record_id = row["id"].strip()
            real_first = row["firstname"].strip()
            real_last = row["lastname"].strip()
            real_address = row["address"].strip()

            if real_first not in first_name_map:
                first_name_map[real_first] = faker.first_name()

            if real_last not in last_name_map:
                last_name_map[real_last] = faker.last_name()

            if real_address not in address_map:
                address_map[real_address] = faker.address().replace("\n", ", ")

            writer.writerow(
                {
                    "id": record_id,
                    "firstname": first_name_map[real_first],
                    "lastname": last_name_map[real_last],
                    "address": address_map[real_address],
                }
            )

    print(f"Pseudonymized {len(rows)} rows into: {output_path}")
    print("Mappings created:")
    print(f"  firstnames: {len(first_name_map)}")
    print(f"  lastnames: {len(last_name_map)}")
    print(f"  addresses: {len(address_map)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pseudonymize CSV dataset with Faker",
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/input_pii.csv",
        help="Input CSV path",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/output_pseudo.csv",
        help="Output CSV path",
    )
    parser.add_argument("--locale", type=str, default="en_US", help="Faker locale")
    parser.add_argument(
        "--seed",
        type=int,
        default=1234,
        help="Random seed for reproducibility",
    )
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    pseudonymize_dataset(
        input_path=args.input,
        output_path=args.output,
        locale=args.locale,
        seed=args.seed,
    )
