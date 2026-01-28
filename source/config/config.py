import json
from pathlib import Path

_CONFIG = None

def load_config() -> dict:
    global _CONFIG
    if _CONFIG is None:
        config_path = Path(__file__).resolve().parents[2] / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            _CONFIG = json.load(f)
    return _CONFIG

def get_config(path: str, default=None):
    config = load_config()
    keys = path.split(".")

    value = config
    for k in keys:
        if k not in value:
            if default is not None:
                return default
            raise KeyError(f"Missing config key: {path}")
        value = value[k]

    return value