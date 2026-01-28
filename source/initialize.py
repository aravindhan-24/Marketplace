from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from source.db.db import init_db
from source.logger.logger import init_logger
from source.constants.constants import TEMPLATE_DIR, UPLOAD_DIR, MAPPING_UPLOAD_DIR, LOG_FILE_PATH

def init_dirs():
    dirs = [TEMPLATE_DIR, UPLOAD_DIR, MAPPING_UPLOAD_DIR, Path(LOG_FILE_PATH).parent]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def initialize(app: FastAPI):
    init_dirs()
    init_logger(LOG_FILE_PATH)
    init_db()
    yield