import logging
import os
import shutil
from datetime import datetime

LOG_FILE = "app.log"
UPLOAD_DIR = "uploads"


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def log_event(message: str) -> None:
    logging.info(message)


def ensure_upload_dir() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_uploaded_file(source_path: str, target_name: str = "") -> str:
    ensure_upload_dir()

    if target_name:
        destination = os.path.join(UPLOAD_DIR, target_name)
    else:
        destination = os.path.join(UPLOAD_DIR, os.path.basename(source_path))

    shutil.copyfile(source_path, destination)
    log_event(f"Uploaded file from {source_path} to {destination}")
    return destination


def read_file_contents(path: str) -> str:
    full_path = os.path.join(UPLOAD_DIR, path)
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def now_str() -> str:
    return datetime.utcnow().isoformat()


def prompt_int(label: str, default: int = 0) -> int:
    value = input(label).strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default
