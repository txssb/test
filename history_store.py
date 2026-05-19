import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
HISTORY_DIR = DATA_DIR / "history"
INDEX_FILE = HISTORY_DIR / "index.json"
MAX_RECORDS = 100
PREVIEW_LEN = 120


def _ensure_history_dir() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text("[]", encoding="utf-8")


def _load_index() -> list[dict]:
    _ensure_history_dir()
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


def _save_index(records: list[dict]) -> None:
    INDEX_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def add_record(content: str, filename: str) -> str:
    _ensure_history_dir()
    record_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    text_path = HISTORY_DIR / f"{record_id}.txt"
    text_path.write_text(content, encoding="utf-8")

    preview = content[:PREVIEW_LEN]
    if len(content) > PREVIEW_LEN:
        preview += "…"

    record = {
        "id": record_id,
        "filename": filename,
        "char_count": len(content),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "preview": preview,
    }

    records = _load_index()
    records.insert(0, record)

    if len(records) > MAX_RECORDS:
        for old in records[MAX_RECORDS:]:
            old_path = HISTORY_DIR / f"{old['id']}.txt"
            if old_path.exists():
                old_path.unlink()
        records = records[:MAX_RECORDS]

    _save_index(records)
    return record_id


def list_records() -> list[dict]:
    return _load_index()


def get_record(record_id: str) -> dict | None:
    for record in _load_index():
        if record["id"] == record_id:
            text_path = HISTORY_DIR / f"{record_id}.txt"
            if not text_path.exists():
                return None
            return {
                **record,
                "content": text_path.read_text(encoding="utf-8"),
            }
    return None
