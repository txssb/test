import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from flask import Flask, jsonify, redirect, render_template, request, url_for

import analysis_store
import history_store
import text_store
from ai_service import AIConfigError, AIRequestError, analyze as run_ai_analyze

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 单文件最大 5MB
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-in-production")

ALLOWED_EXTENSIONS = {".txt"}


def _allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _display_filename(raw: str) -> str:
    """保留中文等真实文件名，仅去除路径与非法字符。"""
    if not raw:
        return "upload.txt"
    name = raw.replace("\\", "/").split("/")[-1].strip()
    if not name:
        return "upload.txt"
    for ch in '\\/:*?"<>|\0':
        name = name.replace(ch, "_")
    return name[:200] if len(name) > 200 else name


def _decode_text(raw: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gbk"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("无法识别文件编码，请使用 UTF-8 或 GBK 编码的 txt 文件")


@app.route("/")
def index():
    meta = text_store.get_meta()
    preview = None
    text = text_store.get_text()
    if text:
        preview = text[:300] + ("…" if len(text) > 300 else "")
    analysis = analysis_store.get_analysis()
    return render_template(
        "index.html",
        meta=meta,
        preview=preview,
        analysis=analysis,
        active="index",
    )


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        meta = text_store.get_meta()
        return render_template(
            "upload.html",
            meta=meta,
            error=None,
            active="upload",
        )

    file = request.files.get("file")
    if not file or not file.filename:
        return render_template(
            "upload.html",
            meta=text_store.get_meta(),
            error="请选择文件",
            active="upload",
        )

    if not _allowed_file(file.filename):
        return render_template(
            "upload.html",
            meta=text_store.get_meta(),
            error="仅支持 .txt 文件",
            active="upload",
        )

    try:
        content = _decode_text(file.read())
    except ValueError as exc:
        return render_template(
            "upload.html",
            meta=text_store.get_meta(),
            error=str(exc),
            active="upload",
        )

    if not content.strip():
        return render_template(
            "upload.html",
            meta=text_store.get_meta(),
            error="文件内容为空",
            active="upload",
        )

    filename = _display_filename(file.filename)
    text_store.save_text(content, filename)
    return redirect(url_for("upload", success=1))


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    meta = text_store.get_meta()
    text = text_store.get_text()
    has_text = text is not None

    if request.method == "GET":
        return render_template(
            "analyze.html",
            has_text=has_text,
            meta=meta,
            prompt=analysis_store.get_last_prompt(),
            analysis=analysis_store.get_analysis(),
            error=None,
            active="analyze",
        )

    if not has_text:
        return render_template(
            "analyze.html",
            has_text=False,
            meta=None,
            prompt=analysis_store.get_last_prompt(),
            analysis=None,
            error="请先上传文本",
            active="analyze",
        )

    prompt = request.form.get("prompt", "").strip()
    if not prompt:
        prompt = analysis_store.DEFAULT_PROMPT

    try:
        result = run_ai_analyze(text, prompt)
    except AIConfigError as exc:
        return render_template(
            "analyze.html",
            has_text=True,
            meta=meta,
            prompt=prompt,
            analysis=analysis_store.get_analysis(),
            error=str(exc),
            active="analyze",
        )
    except AIRequestError as exc:
        return render_template(
            "analyze.html",
            has_text=True,
            meta=meta,
            prompt=prompt,
            analysis=analysis_store.get_analysis(),
            error=str(exc),
            active="analyze",
        )

    analysis_store.save_analysis(result, prompt, meta["filename"])
    return redirect(url_for("analyze", success=1))


@app.route("/history")
def history():
    records = history_store.list_records()
    return render_template(
        "history.html",
        records=records,
        active="history",
    )


@app.route("/history/<record_id>")
def history_detail(record_id: str):
    record = history_store.get_record(record_id)
    if record is None:
        return redirect(url_for("history"))
    return render_template(
        "history_detail.html",
        record=record,
        active="history",
    )


@app.route("/history/<record_id>/load", methods=["POST"])
def history_load(record_id: str):
    record = history_store.get_record(record_id)
    if record is None:
        return redirect(url_for("history"))
    text_store.set_current(
        record["content"],
        record["filename"],
        history_id=record["id"],
    )
    return redirect(url_for("history", loaded=1))


@app.route("/api/history")
def api_history():
    return jsonify({"ok": True, "records": history_store.list_records()})


@app.route("/api/text")
def api_text():
    text = text_store.get_text()
    if text is None:
        return jsonify({"ok": False, "error": "尚未上传文本"}), 404
    meta = text_store.get_meta() or {}
    return jsonify({"ok": True, "text": text, "meta": meta})


@app.route("/api/analysis")
def api_analysis():
    analysis = analysis_store.get_analysis()
    if analysis is None:
        return jsonify({"ok": False, "error": "尚未进行 AI 分析"}), 404
    return jsonify({"ok": True, "analysis": analysis})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
