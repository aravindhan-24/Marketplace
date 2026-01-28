import pytest
import csv
from pathlib import Path
from unittest.mock import MagicMock, patch
from source.handlers.mappingHandler import validate_file

TEST_DIR = Path(__file__).parent
SAMPLE_CSV_PATH = TEST_DIR / "seller_1_mapping.json" 

@patch("source.handlers.mappingHandler.SessionLocal")
@patch("source.handlers.mappingHandler.load_json_file")
@patch("source.handlers.mappingHandler.read_csv_rows")
@patch("source.handlers.mappingHandler.validate_csv")
def test_validate_file_success(mock_val_csv, mock_read_csv, mock_load_json, mock_session):
    with open(SAMPLE_CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_data = [row for row in reader]

    mock_db = MagicMock()
    mock_session.return_value = mock_db

    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
        template_id=1, 
        mapping_file_id=10
    )
    
    mock_db.query.return_value.get.side_effect = [
        MagicMock(file_path="map.json"),  
        MagicMock(file_id=20),            
        MagicMock(file_path="temp.json"), 
        MagicMock(csv_file_id=30),        
        MagicMock(file_path="data.csv")  
    ]

    mock_load_json.side_effect = [
        {"mapping": {"source_col": "target_col"}},
        {"fields": [{"name": "target_col", "required": True}]} 
    ]
    
    mock_read_csv.return_value = csv_data
    
    mock_val_csv.return_value = [{"valid": True} for _ in csv_data]

    result = validate_file(seller_id="seller_1", mapping_file_id=10)

    assert result["total"] == len(csv_data)
    assert result["valid"] == len(csv_data)
    mock_val_csv.assert_called_once()
    mock_session.return_value.close.assert_called() 