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
    logger.info(
        f"CSV validation started | rows={len(rows)} | mapped_fields={len(mapping)}"
    )

    validators, unique_fields = build_validators(template_fields)
    unique_seen = {f: set() for f in unique_fields}

    results = []

    for idx, row in enumerate(rows, start=1):
        errors = {}

        for field, validator in validators.items():
            csv_col = mapping.get(field)

            if not csv_col:
                errors[field] = "Field not mapped"
                continue

            value = row.get(csv_col)

            if not validator(value):
                errors[field] = "Validation failed"
                continue

            if field in unique_fields:
                v = str(value).strip()
                if v == "":
                    continue
                if v in unique_seen[field]:
                    errors[field] = "Duplicate value"
                else:
                    unique_seen[field].add(v)

        if "price" in mapping and "mrp" in mapping:
            try:
                price = float(row.get(mapping["price"], 0))
                mrp = float(row.get(mapping["mrp"], 0))

                if price > mrp:
                    errors["price"] = "Price cannot exceed MRP"

            except Exception:
                errors["price"] = "Invalid price/mrp"

        results.append({
            "row": idx,
            "valid": not errors,
            "errors": errors
        })

    valid_count = sum(r["valid"] for r in results)

    logger.info(
        f"CSV validation completed | total={len(results)} | valid={valid_count} | invalid={len(results) - valid_count}"
    )

    return results
