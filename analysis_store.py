import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
ANALYSIS_FILE = DATA_DIR / "analysis.json"
PROMPT_FILE = DATA_DIR / "last_prompt.txt"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)


def save_analysis(result: str, prompt: str, source_filename: str) -> None:
    _ensure_data_dir()
    data = {
        "result": result,
        "prompt": prompt,
        "source_filename": source_filename,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ANALYSIS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    PROMPT_FILE.write_text(prompt, encoding="utf-8")


def get_analysis() -> dict | None:
    if not ANALYSIS_FILE.exists():
        return None
    return json.loads(ANALYSIS_FILE.read_text(encoding="utf-8"))


def get_last_prompt() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8").strip()
    return DEFAULT_PROMPT


def clear_analysis() -> None:
    if ANALYSIS_FILE.exists():
        ANALYSIS_FILE.unlink()


DEFAULT_PROMPT = (
    "请阅读以下文本，并给出：\n"
    "1. 内容摘要\n"
    "2. 关键要点（条目列出）\n"
    "3. 你的阅读见解或建议"
)
