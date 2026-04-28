#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
daily_article_generator.py
ai-tool-navigator 日次記事自動生成スクリプト

3段フォールバック:
  1. FreeLLMAPI (localhost:3001)
  2. Google Gemini API direct
  3. NVIDIA NIM direct

依存: 標準ライブラリのみ (Python 3.9+)
"""

import os
import re
import json
import time
import datetime
import subprocess
import urllib.request
import urllib.error
from datetime import timezone


# ============================================================
# 設定
# ============================================================
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(REPO_DIR, "src/articles")
ENV_FILE = os.path.expanduser("~/ai-blog-config/.env")

AFFILIATE_CTA = """
---

## AIブログを始めるなら

AIツールの知識を活かしてブログで発信してみませんか？当サイトも使用している**ConoHa WING**なら、月額687円〜で高速サーバーが使えます。

[ConoHa WINGでブログを始める](//af.moshimo.com/af/c/click?a_id=5506692&p_id=2312&pc_id=4967&pl_id=38395)

*※上記リンクはアフィリエイトリンクです。*
"""

TOPICS = [
    {
        "title": "無料で使えるAI API比較 2026年最新版",
        "keywords": "AI API 無料 比較 2026 OpenRouter NVIDIA NIM Google AI",
        "search_query": "free AI API 2026 OpenRouter NVIDIA NIM Google AI Studio",
        "guidance": "OpenRouter、NVIDIA NIM、Google AI Studio、Hugging Faceなど主要な無料AI APIを比較。無料枠の制限、対応モデル、手順を具体的に書き、比較表を含める。"
    },
    {
        "title": "FreeLLMAPI 統合ハブの構築実録｜14プロバイダ40モデルを1キーで使う方法",
        "keywords": "FreeLLMAPI 統合 LLM プロバイダ ルーティング 2026",
        "search_query": "free LLM API gateway router multiple providers 2026",
        "guidance": "FreeLLMAPIで複数のLLMプロバイダ（OpenRouter, NVIDIA NIM, Google等）を1つのエンドポイントに統合する方法。導入手順、認証、フォールバック設計、実際の運用ログを含める。"
    },
    {
        "title": "AI副業で月5万円を稼ぐロードマップ",
        "keywords": "AI 副業 月5万 稼ぐ 初心者 2026",
        "search_query": "AI side hustle earn money beginner 2026 roadmap",
        "guidance": "3ヶ月で月5万円を達成するためのステップ。案件例、必要なツール、手順を解説。"
    },
    {
        "title": "マルチモーダルAI徹底比較｜GPT-5 vs Gemini vs Claude",
        "keywords": "マルチモーダルAI 比較 GPT-5 Gemini Claude 2026",
        "search_query": "multimodal AI comparison GPT-5 Gemini Claude 2026",
        "guidance": "2026年時点の主要AIの機能を比較。テキスト・画像・音声への対応状況を比較表付きで解説。"
    },
    {
        "title": "AIエージェント フレームワーク比較｜LangChain vs AutoGen vs CrewAI",
        "keywords": "AIエージェント 比較 LangChain AutoGen CrewAI 2026",
        "search_query": "AI agent framework comparison LangChain AutoGen CrewAI 2026",
        "guidance": "主要なAIエージェントフレームワークを比較。機能、難易度、ユースケース、コミュニティ規模を解説。"
    },
    {
        "title": "プロンプトエンジニアリング実践テクニック10選",
        "keywords": "プロンプトエンジニアリング テクニック ChatGPT Claude 2026",
        "search_query": "prompt engineering techniques best practices 2026",
        "guidance": "実務で使えるテクニックを紹介。具体的なプロンプト例（before/after）を含める。"
    },
    {
        "title": "AI画像生成で稼ぐ方法｜ストックフォト販売完全ガイド",
        "keywords": "AI画像生成 稼ぐ Adobe Stock Midjourney 2026",
        "search_query": "AI image generation stock photo selling 2026",
        "guidance": "ストックフォトサイトで販売して収益を得る方法。ツール選び、審査のコツを解説。"
    },
    {
        "title": "AI音声合成アプリ比較｜ビジネス活用ガイド",
        "keywords": "AI音声合成 TTS アプリ 比較 2026",
        "search_query": "AI text to speech app comparison business use 2026",
        "guidance": "日本語対応TTSアプリを比較。ナレーションや動画制作での活用事例を解説。"
    },
    {
        "title": "LLMファインチューニング入門｜自分専用AIの作り方",
        "keywords": "LLM ファインチューニング 入門 LoRA 2026",
        "search_query": "LLM fine-tuning tutorial LoRA beginner guide 2026",
        "guidance": "LoRAの仕組みと実行手順を初心者向けに解説。必要な準備とコストを提示。"
    },
    {
        "title": "AIデータ分析ツール比較｜ノーコードで始めるデータサイエンス",
        "keywords": "AI データ分析 ツール ノーコード 2026",
        "search_query": "AI data analysis tools no-code comparison 2026",
        "guidance": "プログラミング不要な分析ツールを比較。具体的なユースケースを解説。"
    }
]

SYSTEM_PROMPT = (
    "あなたはAI技術と副業に詳しい技術ブロガーです。日本語で読者に具体的で実用的な情報を提供します。\n"
    "現在は2026年4月です。記事は2026年4月時点の最新情報として執筆してください。\n"
    "「2023年現在」「2024年最新」など古い年号を絶対に書かないこと。年号に言及する場合は必ず「2026年」と書いてください。\n\n"
    "【記事の要件】\n"
    "- 3000字以上（必達、不足する場合は章を追加して情報密度を上げる）\n"
    "- H2見出し（##）を5つ以上使用\n"
    "- 比較表（Markdownテーブル）または番号付き箇条書きを最低1つ含める\n"
    "- 比較表のセルに不明な情報がある場合は「要確認」と必ず書く（空セルにしない）\n"
    "- 一人称は「私」、文体は「です・ます」調\n"
    "- 「正直に言う」「お前ら」「絶対に〜」などの煽り口調・断定表現は使わない\n"
    "- 「最速」「業界No.1」など根拠なき断定は禁止。「公式発表によれば〜」「私が試した範囲では〜」など出典や経験を意識した表現を使う\n"
    "- 数値や手順は具体的に書く（例: 月額687円、所要15分、など）\n"
    "- 末尾に「## まとめ」セクションを必ず置き、要点を3〜5項目の箇条書きで示す\n\n"
    "【出力形式】\n"
    "- Markdown形式で記事本文のみを出力\n"
    "- frontmatter（YAML）は出力しない（呼び出し側で付与する）\n"
    "- 記事冒頭にH1見出し（# タイトル）は不要、H2（##）から始めてよい\n"
    "- 出力の冒頭・末尾に「以下が記事です」のような前置き・後置きを書かないこと、Markdown本文のみ\n"
)


# ============================================================
# ユーティリティ
# ============================================================
def load_env():
    env = {}
    # 1. .env file (local Mac execution)
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env[key.strip()] = val.strip().strip('"').strip("'")
    # 2. OS environment variables (CI/Actions execution, also used as fallback/override-source)
    for key in ("GOOGLE_API_KEY", "NVIDIA_API_KEY", "NVIDIA_BASE_URL",
                "FREELLMAPI_KEY", "OPENAI_API_KEY", "OPENAI_API_BASE",
                "GITHUB_TOKEN", "TAVILY_API_KEY"):
        os_val = os.environ.get(key, "")
        if os_val and not env.get(key):
            env[key] = os_val
    return env


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = text.strip("-")
    return text[:60]


def get_jst_now():
    return datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=9)


def get_today_topic():
    jst_now = get_jst_now()
    day_of_year = jst_now.timetuple().tm_yday
    idx = day_of_year % len(TOPICS)
    return TOPICS[idx]


def fetch_search_context(query):
    """TODO: Tavily APIで実装予定（Day7以降）"""
    return ""


def build_prompt(topic, search_context):
    parts = [
        "テーマ: " + topic["title"],
        "キーワード: " + topic["keywords"],
        "方向性: " + topic["guidance"],
    ]
    if search_context:
        parts.append("参考情報:\n" + search_context)
    parts.append("")
    parts.append("上記に基づき、3000字以上の詳細なブログ記事をMarkdown形式で書いてください。比較表を含め、各セクションには具体例や数値を必ず入れてください。")
    return "\n\n".join(parts)


# ============================================================
# LLM API呼び出し（3段フォールバック）
# ============================================================
def _http_post_json(url, headers, body, timeout):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def call_freellmapi(prompt, env, max_tokens=6000):
    api_key = env.get("FREELLMAPI_KEY", "")
    if not api_key:
        raise ValueError("FREELLMAPI_KEY not found in env")

    url = "http://localhost:3001/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    base_body = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    last_error = None
    for model_name in ["llama-3.3-70b-versatile", "qwen3-235b", "gemini-2.5-flash", "auto"]:
        try:
            body = dict(base_body)
            body["model"] = model_name
            data = _http_post_json(url, headers, body, timeout=90)
            content = data["choices"][0]["message"]["content"]
            if content and content.strip():
                return content
            last_error = "empty content from model " + model_name
        except Exception as e:
            last_error = "model " + model_name + ": " + str(e)
            continue

    raise RuntimeError("FreeLLMAPI failed: " + str(last_error))


def call_gemini_direct(prompt, env, max_tokens=6000):
    api_key = env.get("GOOGLE_API_KEY", "")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in env")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent?key=" + api_key
    )
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT + "\n\n" + prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.7,
        },
    }

    data = _http_post_json(url, headers, body, timeout=90)
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini returned no candidates: " + json.dumps(data)[:300])
    parts = candidates[0].get("content", {}).get("parts", [])
    texts = [p.get("text", "") for p in parts if p.get("text")]
    text = "\n".join(texts).strip()
    if not text:
        raise RuntimeError("Gemini returned empty text")
    return text


def call_nvidia_nim(prompt, env, max_tokens=6000):
    api_key = env.get("NVIDIA_API_KEY", "")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY not found in env")

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    body = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    data = _http_post_json(url, headers, body, timeout=90)
    content = data["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise RuntimeError("NVIDIA NIM returned empty content")
    return content


def generate_article_with_fallback(prompt, env):
    providers = [
        ("freellmapi", call_freellmapi),
        ("gemini_direct", call_gemini_direct),
        ("nvidia_nim", call_nvidia_nim),
    ]

    last_error = None
    for name, func in providers:
        print("[INFO] Trying provider: " + name)
        try:
            text = func(prompt, env)
            print("[INFO] Provider " + name + " succeeded (" + str(len(text)) + " chars)")
            return text, name
        except Exception as e:
            last_error = str(e)
            print("[WARN] " + name + " failed: " + last_error)
            time.sleep(3)

    raise RuntimeError("All 3 LLM providers failed. Last error: " + str(last_error))


def generate_description(article_text, env):
    snippet = article_text[:2000]
    prompt = (
        "以下の記事を、SEO用メタディスクリプションとして100〜120字の日本語で要約してください。"
        "記号や改行を含めず、純粋な要約文のみを出力してください。\n\n"
        + snippet
    )
    try:
        text, _ = generate_article_with_fallback(prompt, env)
        text = text.strip().replace("\n", " ").replace("\r", " ")
        if len(text) > 130:
            cut = text[:120]
            for sep in ["。", "．", ".", "！", "!", "？", "?"]:
                last = cut.rfind(sep)
                if last >= 60:
                    cut = cut[:last + len(sep)]
                    break
            text = cut
        return text
    except Exception as e:
        print("[WARN] description generation failed, using fallback: " + str(e))
        return ""


# ============================================================
# 記事ファイル書き出し
# ============================================================
def write_article_file(filepath, topic, article_body, description, provider, today):
    title_escaped = topic["title"].replace('"', '\\"')
    desc_escaped = description.replace('"', '\\"').replace("\n", " ")
    first_keyword = topic["keywords"].split()[0] if topic["keywords"] else "AI"

    frontmatter_lines = [
        "---",
        "layout: post.njk",
        'title: "' + title_escaped + '"',
        "date: " + today,
        "tags: [AI, " + first_keyword + "]",
        'description: "' + desc_escaped + '"',
        "ai_generated: true",
        'generated_via: "' + provider + '"',
        "---",
        "",
    ]
    frontmatter = "\n".join(frontmatter_lines)

    content = frontmatter + "\n" + article_body + "\n" + AFFILIATE_CTA + "\n"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# Git操作
# ============================================================
def git_commit_and_push(repo_dir, commit_message):
    try:
        subprocess.run(
            ["git", "add", "src/articles/"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )
        return True, "ok"
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
        return False, stderr
    except Exception as e:
        return False, str(e)


# ============================================================
# メイン処理
# ============================================================
def main():
    print("[INFO] === daily_article_generator.py start ===")
    env = load_env()
    if not env:
        print("[ERROR] env file empty or not found: " + ENV_FILE)
        return 1

    topic = get_today_topic()
    jst_now = get_jst_now()
    today = jst_now.date().isoformat()

    slug = slugify(topic["title"])
    filename = today + "-" + slug + ".md"
    filepath = os.path.join(ARTICLES_DIR, filename)

    print("[INFO] Topic: " + topic["title"])
    print("[INFO] Filepath: " + filepath)

    if os.path.exists(filepath):
        print("[SKIP] Already exists: " + filename)
        return 0

    search_context = fetch_search_context(topic["search_query"])
    prompt = build_prompt(topic, search_context)

    try:
        article_body, provider = generate_article_with_fallback(prompt, env)
    except Exception as e:
        print("[ERROR] Article generation failed: " + str(e))
        return 1

    print("[INFO] Generating description...")
    description = generate_description(article_body, env)
    if not description:
        description = topic["title"] + "について、最新情報と実践的な手順を解説します。"
    print("[INFO] Description: " + description)

    write_article_file(filepath, topic, article_body, description, provider, today)
    print("[INFO] Article written: " + filepath)

    commit_message = "Add daily article: " + topic["title"] + " (via " + provider + ")"
    push_ok, push_msg = git_commit_and_push(REPO_DIR, commit_message)
    if push_ok:
        print("[INFO] Git push succeeded")
    else:
        print("[WARN] Git push failed: " + push_msg)

    print("[INFO] === daily_article_generator.py done ===")
    return 0


if __name__ == "__main__":
    exit_code = main()
    raise SystemExit(exit_code)
