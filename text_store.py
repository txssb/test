import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
TEXT_FILE = DATA_DIR / "current.txt"
META_FILE = DATA_DIR / "meta.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)


def _clear_analysis_on_new_upload() -> None:
    try:
        import analysis_store

        analysis_store.clear_analysis()
    except ImportError:
        pass


def set_current(content: str, filename: str, history_id: str | None = None) -> None:
    """设为当前文本（不写入历史，用于从历史恢复）。"""
    _ensure_data_dir()
    _clear_analysis_on_new_upload()
    TEXT_FILE.write_text(content, encoding="utf-8")
    meta = {
        "filename": filename,
        "char_count": len(content),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if history_id:
        meta["history_id"] = history_id
    META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def save_text(content: str, filename: str) -> str:
    """保存为当前文本，并追加一条历史记录。返回 history_id。"""
    import history_store

    history_id = history_store.add_record(content, filename)
    set_current(content, filename, history_id=history_id)
    return history_id


def get_text() -> str | None:
    if not TEXT_FILE.exists():
        return None
    return TEXT_FILE.read_text(encoding="utf-8")


def get_meta() -> dict | None:
    if not META_FILE.exists():
        return None
    return json.loads(META_FILE.read_text(encoding="utf-8"))
