from source.utility.validationHelper import validate_csv


def test_validate_csv_success():
    rows = [{"SKU": "A1", "Price": "100", "MRP": "120"}]

    mapping = {
        "sku": "SKU",
        "price": "Price",
        "mrp": "MRP",
    }

    template_fields = {
        "sku": {"type": "string", "required": True, "unique": True},
        "price": {"type": "number", "required": True},
        "mrp": {"type": "number", "required": True},
    }

    result = validate_csv(rows, mapping, template_fields)

    assert result[0]["valid"] is True
    assert result[0]["errors"] == {}


def test_validate_csv_price_gt_mrp():
    rows = [{"Price": "200", "MRP": "100"}]

    mapping = {"price": "Price", "mrp": "MRP"}

    template_fields = {
        "price": {"type": "number"},
        "mrp": {"type": "number"},
    }

    result = validate_csv(rows, mapping, template_fields)

    assert result[0]["valid"] is False
    assert "price" in result[0]["errors"]
