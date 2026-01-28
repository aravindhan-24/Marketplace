from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = "Streamoid.ai"
ALGORITHM = "HS256"

SAMPLE_ROW_COUNT = 10
ENCODING = "utf-8"

ENDPOINT = "/v1"

TEMPLATE_DIR = BASE_DIR / "templates"
UPLOAD_DIR = BASE_DIR / "uploads"
MAPPING_UPLOAD_DIR = BASE_DIR / "mapping"
LOG_FILE_PATH = BASE_DIR / "logs" / "app.log"
