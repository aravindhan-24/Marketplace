import logging
import json
import csv
from typing import List, Dict

from source.constants.constants import ENCODING

logger = logging.getLogger(__name__)


def load_json_file(file_path: str) -> dict:
    logger.debug(f"Loading JSON file | path={file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"JSON file loaded successfully | path={file_path}")
        return data
    except Exception:
        logger.exception(f"Failed to load JSON file | path={file_path}")
        raise


def read_csv_rows(file_path: str) -> List[Dict[str, str]]:
    logger.debug(f"Reading CSV file | path={file_path}")
    rows: List[Dict[str, str]] = []

    try:
        with open(file_path, newline="", encoding=ENCODING) as f:
            reader = csv.DictReader(f)

            for row in reader:
                rows.append({
                    k: "" if v is None else str(v).strip()
                    for k, v in row.items()
                })

        logger.debug(
            f"CSV file read successfully | path={file_path} | rows={len(rows)}"
        )
        return rows

    except Exception:
        logger.exception(f"Failed to read CSV file | path={file_path}")
        raise
