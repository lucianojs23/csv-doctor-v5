import os
from datetime import datetime
from . import config
import json

def ensure_dirs():
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

def _log_path():
    ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d")
    return config.LOGS_DIR / f"csvdoctor_{ts}.log"

def log(msg, level="INFO"):
    ensure_dirs()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    with open(_log_path(), "a", encoding="utf-8") as f:
        f.write(line + "\n")

def pretty_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)
