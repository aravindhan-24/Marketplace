import json
import csv
from typing import List, Dict
from constants import ENCODING

def load_json_file(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_csv_rows(file_path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []

    with open(file_path, newline="", encoding=ENCODING) as f:
        reader = csv.DictReader(f)

        for row in reader:
            # normalize immediately
            rows.append({
                k: "" if v is None else str(v).strip()
                for k, v in row.items()
            })

    return rows