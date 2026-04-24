#!/usr/bin/env python3
import os
import re
import datetime
import json
import subprocess
import urllib.request
import urllib.error

# ============================================================
# 設定
# ============================================================
REPO_DIR = "/Users/common/ai-tool-navigator"
ARTICLES_DIR = os.path.join(REPO_DIR, "src/articles")
ENV_FILE = os.path.expanduser("~/.hermes/.env")

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
        "title": "Hermes Agent 完全セットアップガイド",
        "keywords": "Hermes Agent セットアップ Discord 自動化 AIエージェント",
        "search_query": "Hermes Agent setup guide Discord automation 2026",
        "guidance": "インストールから自動起動までの完全手順。実際のコマンド例やconfig.yamlの記述例を含める。"
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
        "title": "AIエージェント フレームワーク比較｜Hermes vs OpenClaw vs LangChain",
        "keywords": "AIエージェント 比較 Hermes OpenClaw LangChain 2026",
        "search_query": "AI agent framework comparison Hermes OpenClaw LangChain 2026",
        "guidance": "主要なフレームワークを比較。機能、難易度、ユースケースを解説。"
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

# ============================================================
# ユーティリティ
# ============================================================
def load_env():
    env = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    env[key.strip()] = val.strip()
    return env

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text[:60]

def get_jst_now():
    utc_now = datetime.datetime.utcnow()
    return utc_now + datetime.timedelta(hours=9)

def get_today_topic():
    jst_now = get_jst_now()
    day_of_year = jst_now.timetuple().tm_yday
    idx = day_of_year % len(TOPICS)
    return TOPICS[idx]

def fetch_search_context(query):
    try:
        from hermes_tools import web_search
        res = web_search(query=query, limit=5)
        snippets = []
        for r in res.get('data', {}).get('web', []):
            title = r.get('title', '')
            desc = r.get('description', '')
            if title and desc:
                snippets.append(f"- {title}: {desc}")
        return '\n'.join(snippets) if snippets else ""
    except Exception:
        return ""

# ============================================================
# LLM API呼び出し
# ============================================================
def call_openrouter(prompt, env):
    api_key = env.get('OPENROUTER_API_KEY', '')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")
    
    payload = json.dumps({
        "model": "qwen/qwen3.6-plus",
        "messages": [
            {
                "role": "system",
                "content": "あなたは「Navigator X」というAIツール専門ブロガーです。読者に具体的で実用的な情報を提供します。2000字以上の記事をMarkdown形式で書いてください。見出しを4つ以上使い、具体的数値や比較表を含めてください。定型文「正直に言う。お前らが〜」は使わず、信頼感のある口調でお願いします。"
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.7
    }).encode('utf-8')
    
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://kaneko-ai.github.io/ai-tool-navigator/",
            "X-Title": "AI Tool Navigator"
        }
    )
    
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data['choices'][0]['message']['content']

def generate_article_with_llm(topic, search_context, env):
    prompt = f"""テーマ: {topic['title']}\nキーワード: {topic['keywords']}\n方向性: {topic['guidance']}\n参考情報:\n{search_context}\n\n上記に基づき、2000字以上の詳細なブログ記事を書いてください。"""
    try:
        return call_openrouter(prompt, env)
    except Exception as e:
        print(f"[ERROR] LLM生成失敗: {e}")
        return f"記事の生成に失敗しました: {e}"

# ============================================================
# メイン処理
# ============================================================
def main():
    env = load_env()
    topic = get_today_topic()
    jst_now = get_jst_now()
    today = jst_now.date().isoformat()
    
    slug = slugify(topic['title'])
    filename = f"{today}-{slug}.md"
    filepath = os.path.join(ARTICLES_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"[SKIP] 既に存在: {filename}")
        return
    
    print(f"[INFO] 記事生成開始: {topic['title']}")
    search_context = fetch_search_context(topic['search_query'])
    article_body = generate_article_with_llm(topic, search_context, env)
    
    content = f"""---
layout: post.njk
title: "{topic['title']}"
date: {today}
tags: [AI, {topic['keywords'].split()[0]}]
description: "{topic['title']}の最新情報と活用ガイド。"
ai_generated: true
---

{article_body}

{AFFILIATE_CTA}
"""
    
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Git 操作
    try:
        subprocess.run(["git", "add", "src/articles/"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", f"Add daily article: {topic['title']}"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)
        push_success = True
    except Exception as e:
        push_success = False
        print(f"[ERROR] Git操作失敗: {e}")

    # Discord通知
    try:
        from hermes_tools import send_message
        msg = f"✅ 日次記事生成完了: {topic['title']}" if push_success else f"❌ 記事生成エラー: {topic['title']}"
        send_message(message=msg, target="discord")
    except:
        pass

if __name__ == "__main__":
    main()
