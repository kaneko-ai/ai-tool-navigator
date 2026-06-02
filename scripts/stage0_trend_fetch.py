#!/usr/bin/env python3
"""
Stage 0: X Premium OAuth + Grok 4.3 + x_search でリアルタイムトレンドを取得し、
drafts/<DATE>/00_trends.json と 00_trends_summary.md に保存する。

使い方:
    python3 scripts/stage0_trend_fetch.py                # 今日
    python3 scripts/stage0_trend_fetch.py 2026-05-27     # 日付指定
    python3 scripts/stage0_trend_fetch.py --force        # 既存ファイル上書き

環境変数:
    STAGE0_MODEL     (default: grok-4.3)
    STAGE0_PROVIDER  (default: xai-oauth)
    STAGE0_TIMEOUT   (default: 300 秒)
    STAGE0_HERMES_BIN (default: hermes)
"""

from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 設定
REPO_ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = REPO_ROOT / "drafts"
JST = timezone(timedelta(hours=9))

MODEL = os.environ.get("STAGE0_MODEL", "grok-4.3")
PROVIDER = os.environ.get("STAGE0_PROVIDER", "xai-oauth")
TIMEOUT = int(os.environ.get("STAGE0_TIMEOUT", "300"))
HERMES_BIN = os.environ.get("STAGE0_HERMES_BIN", "hermes")

REQUIRED_KEYS = {
    "topic", "summary", "category", "intent",
    "freshness_hours", "example_post", "keywords_jp", "article_angle",
}
VALID_CATEGORIES = {"ai", "freelance", "english"}

PROMPT = """日本のAI、フリーランス、英語学習に関連する直近24時間のXトレンドを、x_searchツールを使って取得してください。各カテゴリ（ai/freelance/english）から必ず2件ずつ、計6件返してください。

出力は以下のJSON配列形式のみ。前置き・解説・コードフェンス・末尾の補足は一切不要です。

[
  {
    "topic": "トピック名（簡潔、20字以内）",
    "summary": "1-2文の要約（日本語、なぜ今話題かを含む）",
    "category": "ai|freelance|english",
    "intent": "informational|transactional|comparison|how_to",
    "freshness_hours": 推定経過時間,
    "example_post": "代表的なポストの抜粋（100字以内、原文ママ)",
    "keywords_jp": ["記事タイトルに使える日本語キーワード3-5語"],
    "article_angle": "この話題を1500字の解説記事にする場合の切り口（30字以内）"
  }
]"""


def parse_args():
    p = argparse.ArgumentParser(description="Stage 0: X trend fetch via Grok 4.3 + x_search")
    p.add_argument("date", nargs="?", default=None, help="YYYY-MM-DD (default: today JST)")
    p.add_argument("--force", action="store_true", help="既存ファイルを上書き")
    p.add_argument("--dry-run", action="store_true", help="hermes は実行するが保存しない")
    return p.parse_args()


def resolve_date(date_str: str | None) -> str:
    if date_str:
        # validate
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    return datetime.now(JST).strftime("%Y-%m-%d")


def extract_json_array(raw: str) -> str | None:
    """raw stdout の中から最初の `[` と最後の `]` を取り出す。"""
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return None
    return raw[start : end + 1]


def validate_trend(item: dict) -> tuple[bool, str]:
    missing = REQUIRED_KEYS - set(item.keys())
    if missing:
        return False, f"missing keys: {sorted(missing)}"
    if item["category"] not in VALID_CATEGORIES:
        return False, f"invalid category: {item['category']}"
    if not isinstance(item["keywords_jp"], list) or len(item["keywords_jp"]) == 0:
        return False, "keywords_jp must be a non-empty list"
    try:
        float(item["freshness_hours"])
    except (TypeError, ValueError):
        return False, f"freshness_hours not numeric: {item['freshness_hours']}"
    return True, ""


def run_hermes() -> str:
    """hermes を起動し stdout を返す。失敗時は RuntimeError。"""
    cmd = [
        HERMES_BIN, "-z", PROMPT,
        "--provider", PROVIDER,
        "-m", MODEL,
        "-t", "x_search",
    ]
    print(f"[stage0] running: {HERMES_BIN} -z <PROMPT> --provider {PROVIDER} -m {MODEL} -t x_search", file=sys.stderr)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"hermes timeout after {TIMEOUT}s")
    if proc.returncode != 0:
        raise RuntimeError(f"hermes exit {proc.returncode}: stderr={proc.stderr[:400]}")
    return proc.stdout


def render_markdown_summary(date: str, payload: dict) -> str:
    lines = [f"# {date} のXトレンド（Stage 0 取得）", ""]
    lines.append(f"- 取得日時: {payload['fetched_at']}")
    lines.append(f"- モデル: {payload['model']}")
    lines.append(f"- ソース: {payload['source']}")
    lines.append(f"- 件数: {len(payload['trends'])}")
    lines.append("")

    by_cat: dict[str, list[dict]] = {"ai": [], "freelance": [], "english": []}
    for t in payload["trends"]:
        by_cat.setdefault(t["category"], []).append(t)

    cat_labels = {"ai": "## AI", "freelance": "## フリーランス", "english": "## 英語学習"}
    for cat, label in cat_labels.items():
        items = by_cat.get(cat, [])
        if not items:
            continue
        lines.append(label)
        lines.append("")
        for t in items:
            lines.append(f"### {t['topic']} ({t['freshness_hours']}h前 / {t['intent']})")
            lines.append(f"- 要約: {t['summary']}")
            lines.append(f"- 切り口: {t['article_angle']}")
            lines.append(f"- キーワード: {', '.join(t['keywords_jp'])}")
            lines.append(f"- 例: {t['example_post']}")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    date = resolve_date(args.date)
    out_dir = DRAFTS_DIR / date
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "00_trends.json"
    md_path = out_dir / "00_trends_summary.md"
    raw_path = out_dir / "00_trends_raw.txt"

    if json_path.exists() and not args.force:
        print(f"[stage0] {json_path} already exists. Skip. (use --force to overwrite)", file=sys.stderr)
        return 0

    try:
        raw = run_hermes()
    except RuntimeError as e:
        print(f"[stage0] FAILED: {e}", file=sys.stderr)
        return 1

    if not args.dry_run:
        raw_path.write_text(raw, encoding="utf-8")

    json_str = extract_json_array(raw)
    if not json_str:
        print(f"[stage0] FAILED: no JSON array found in hermes output (saved to {raw_path})", file=sys.stderr)
        return 1

    try:
        trends_raw = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"[stage0] FAILED: JSON parse error: {e} (saved raw to {raw_path})", file=sys.stderr)
        return 1

    if not isinstance(trends_raw, list):
        print(f"[stage0] FAILED: top-level is not a list", file=sys.stderr)
        return 1

    valid_trends: list[dict] = []
    for i, item in enumerate(trends_raw):
        if not isinstance(item, dict):
            print(f"[stage0] WARN: item {i} not a dict, skip", file=sys.stderr)
            continue
        ok, msg = validate_trend(item)
        if not ok:
            print(f"[stage0] WARN: item {i} invalid ({msg}), skip", file=sys.stderr)
            continue
        valid_trends.append(item)

    if len(valid_trends) < 3:
        print(f"[stage0] FAILED: only {len(valid_trends)} valid trends (need >=3)", file=sys.stderr)
        return 1

    payload = {
        "fetched_at": datetime.now(JST).isoformat(),
        "date": date,
        "model": MODEL,
        "provider": PROVIDER,
        "source": "x_search via hermes",
        "prompt_version": "v1",
        "trends": valid_trends,
    }

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"[stage0] dry-run, no files saved", file=sys.stderr)
        return 0

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_summary(date, payload), encoding="utf-8")

    print(f"[stage0] OK: {len(valid_trends)} trends saved to {json_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
