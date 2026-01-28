import logging
from source.utility.validators import TYPE_DISPATCHER

logger = logging.getLogger(__name__)


def build_validators(template_fields: dict):
    logger.debug("Building validators from template fields")

    validators = {}
    unique_fields = set()

    for field, rule in template_fields.items():
        validators[field] = TYPE_DISPATCHER[rule["type"]](rule)
        if rule.get("unique"):
            unique_fields.add(field)

    logger.debug(
        f"Validators built | total={len(validators)} | unique_fields={len(unique_fields)}"
    )

    return validators, unique_fields


def validate_price(price, mrp):
    return price <= mrp

def validate_csv(rows, mapping, template_fields):
    logger.info(f"CSV validation started | rows={len(rows)}")

    if not rows:
        return []

    mapping = {
        k: v.strip()
        for k, v in mapping.items()
        if v
    }

    required_fields = {
        name for name, meta in template_fields.items()
        if meta.get("required") is True
    }

    validators, unique_fields = build_validators(template_fields)
    unique_seen = {f: set() for f in unique_fields}

    csv_headers = {
        h.strip().lower(): h for h in rows[0].keys()
    }

    missing = []
    for field in required_fields:
        csv_col = mapping.get(field)

        if not csv_col:
            missing.append({
                "field": field,
                "error": "Required field not mapped"
            })
        elif csv_col.strip().lower() not in csv_headers:
            missing.append({
                "field": field,
                "expected_csv_column": csv_col
        })

    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    results = []

    for idx, row in enumerate(rows, start=1):
        errors = {}

        mapped_row = {
            field: row.get(csv_col, "")
            for field, csv_col in mapping.items()
        }

        for field, validator in validators.items():
            value = mapped_row.get(field, "")

            if not value and field in required_fields:
                errors[field] = "Required field missing"
                continue

            if value and not validator(value):
                errors[field] = "Validation failed"
                continue

            if field in unique_fields:
                v = str(value).strip()
                if v:
                    if v in unique_seen[field]:
                        errors[field] = "Duplicate value"
                    else:
                        unique_seen[field].add(v)

        try:
            price = float(mapped_row.get("price", 0))
            mrp = float(mapped_row.get("mrp", 0))
            if price > mrp:
                errors["price"] = "Price cannot exceed MRP"
        except Exception:
            errors["price"] = "Invalid price/mrp"

        results.append({
            "row": idx,
            "valid": not errors,
            "errors": errors
        })

    return results



