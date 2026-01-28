import pytest
from pathlib import Path
from fastapi import UploadFile
from unittest.mock import MagicMock
import io

from source.handlers.csvhandler import uploadfile
from source.db.model import Files, SellerCsvUpload


def make_upload_file_from_disk(path: Path) -> UploadFile:
    """
    Reads CSV from disk and wraps it as FastAPI UploadFile
    """
    content = path.read_bytes()
    return UploadFile(
        filename=path.name,
        file=io.BytesIO(content)
    )


def test_upload_csv_with_sample_file(tmp_path, monkeypatch):
    """
    Uses real sample.csv as input
    """

    test_dir = Path(__file__).parent
    sample_csv = test_dir / "sample.csv"

    assert sample_csv.exists(), "sample.csv must exist next to test file"

    upload_file = make_upload_file_from_disk(sample_csv)

    monkeypatch.setattr(
        "source.handlers.csvhandler.UPLOAD_DIR",
        tmp_path
    )

    monkeypatch.setattr(
        "source.handlers.csvhandler.SAMPLE_ROW_COUNT",
        3
    )

    mock_db = MagicMock()
    monkeypatch.setattr(
        "source.handlers.csvhandler.SessionLocal",
        lambda: mock_db
    )

    def refresh_side_effect(obj):
        if isinstance(obj, Files):
            obj.id = 1
        elif isinstance(obj, SellerCsvUpload):
            obj.id = 10

    mock_db.refresh.side_effect = refresh_side_effect

    response = uploadfile(
        seller_id="seller_1",
        file=upload_file
    )

    assert response["fileId"] == 1
    assert response["csvUploadId"] == 10

    assert response["rowCount"] == 10

    assert response["headers"] == [
        "Name",
        "BrandName",
        "Gender",
        "Category",
        "Color",
        "Size",
        "MRP",
        "Price",
        "SKU",
        "Image1",
        "Description",
        "Material",
    ]

    assert len(response["sampleRows"]) == 3

    first_row = response["sampleRows"][0]
    assert first_row["Name"] == "TShirt"
    assert first_row["BrandName"] == "Otto"
    assert first_row["Price"] == "1290"

    assert mock_db.add.call_count == 2
    assert mock_db.commit.call_count == 2
    mock_db.close.assert_called_once()
