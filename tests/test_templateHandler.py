import pytest
import json
import io
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from fastapi import HTTPException
from source.handlers.templateHandler import uploadTemplate

TEST_DIR = Path(__file__).parent
SAMPLE_TEMPLATE_JSON = TEST_DIR / "seller_1_myntra_template.json" 

@patch("source.handlers.templateHandler.SessionLocal")
@patch("source.handlers.templateHandler.open", new_callable=mock_open)
def test_uploadTemplate_duplicate_error(mock_file, mock_session):
    if not SAMPLE_TEMPLATE_JSON.exists():
        pytest.fail(f"Test file missing at {SAMPLE_TEMPLATE_JSON}")
    
    file_content = SAMPLE_TEMPLATE_JSON.read_text()
    json_data = json.loads(file_content)

    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

    mock_upload = MagicMock()
    mock_upload.file = io.BytesIO(file_content.encode('utf-8'))
    mock_upload.filename = "test_template.json"

    with pytest.raises(HTTPException) as exc:
        uploadTemplate(file=mock_upload)
    
    assert exc.value.status_code == 409
    assert "already exists" in exc.value.detail