import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

# 单次送入模型的文本上限（字符），避免超出 API 限制
MAX_TEXT_CHARS = 30_000


class AIConfigError(Exception):
    pass


class AIRequestError(Exception):
    pass


def _get_config() -> tuple[str, str, str]:
    api_key = os.environ.get("AI_API_KEY", "").strip()
    if not api_key:
        raise AIConfigError(
            "未配置 AI API 密钥。请复制 .env.example 为 .env，并填写 AI_API_KEY。"
        )
    base_url = os.environ.get("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("AI_MODEL", "gpt-4o-mini").strip()
    return api_key, base_url, model


def _build_user_message(prompt: str, text: str) -> str:
    if len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS] + "\n\n[文本过长，已截断至前 30000 字]"
    return f"{prompt.strip()}\n\n---\n\n以下是需要处理的文本：\n\n{text}"


def analyze(text: str, prompt: str) -> str:
    api_key, base_url, model = _get_config()
    url = f"{base_url}/chat/completions"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": _build_user_message(prompt, text)}],
        "temperature": 0.7,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AIRequestError(f"AI 接口返回错误 ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise AIRequestError(f"无法连接 AI 服务: {exc.reason}") from exc

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise AIRequestError(f"AI 返回格式异常: {data}") from exc
