import tempfile
from source.utility.fileHelper import load_json_file, read_csv_rows


def test_load_json_file():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        f.write('{"a": 1}')
        f.flush()

        data = load_json_file(f.name)
        assert data == {"a": 1}


def test_read_csv_rows_normalization():
    csv_data = "name,price\nApple,10\nOrange,\n"

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as f:
        f.write(csv_data)
        f.flush()

        rows = read_csv_rows(f.name)

        assert rows == [
            {"name": "Apple", "price": "10"},
            {"name": "Orange", "price": ""}
        ]
