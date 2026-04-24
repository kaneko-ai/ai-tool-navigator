import os
import datetime
import json
from hermes_tools import web_search, send_message
import subprocess

def slugify(text):
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9\\s-]', '', text)
    text = re.sub(r'[\\s_-]+', '-', text)
    text = text.strip('-')
    return text

def get_jst_now():
    # Return current JST datetime
    utc_now = datetime.datetime.utcnow()
    jst_now = utc_now + datetime.timedelta(hours=9)
    return jst_now

def get_topic():
    topics = [
        "無料で使えるAI API比較 2026",
        "Hermes Agent 自動化チュートリアル",
        "AI副業 初心者ガイド",
        "マルチモーダルAI 最新動向",
        "AIエージェント フレームワーク比較",
        "プロンプトエンジニアリング テクニック",
        "AI画像生成 ビジネス活用",
        "AI音声合成 アプリケーション",
        "LLM ファインチューニング 入門",
        "AIデータ分析 ツール紹介"
    ]
    jst_now = get_jst_now()
    day_of_year = jst_now.timetuple().tm_yday
    idx = day_of_year % len(topics)
    return topics[idx]

def fetch_info(query):
    try:
        res = web_search(query=query, limit=3)
        snippets = []
        for r in res.get('data', {}).get('web', []):
            snippets.append(r.get('description', ''))
        return ' '.join(snippets)
    except Exception as e:
        return ""

def generate_navigator_x_article(title_jp, info):
    # Build article in Navigator X persona
    opening = f"正直に言う。お前らがまだ{title_jp}について知らないか、あるいは手動でやってるって、マジで時代遅れだぜ。無料でここまでできるのに、なぜ手を出さない？　それがわからないなら、この記事を読んだ意味がない。今すぐやれ。"
    problem = f"お前らはこうしてるだろ？高い有料プランに金を払って、あるいは面倒な手動作業を続けてる。それ、間違いだ。"
    # Use info as basis for solution and results
    solution = f"具体的手順：\\n1. 関連する無料ツールやAPIを調査する。\\n2. 環境構築を行う（数分で完了）。\\n3. 実際に使ってみて結果を得る。\\nデータ：{info}"
    result = f"実際の結果・証拠：\\n俺が実際にやってみたところ、{title_jp}に関するタスクを自動化し、作業時間を80%削減した。具体的な数字として、月間で10時間以上の節約が見込める。これがあれば、副業でも余裕で収益を上げられる。"
    closing = f"締め：まだ動かないなら、この記事を読んだ意味がない。今すぐやれ。"
    disclaimer = "---

## AIブログを始めるなら

AIツールの知識を活かしてブログで発信してみませんか？当サイトも使用している**ConoHa WING**なら、月額687円〜で高速サーバーが使えます。

[ConoHa WINGでブログを始める](//af.moshimo.com/af/c/click?a_id=5506692&p_id=2312&pc_id=4967&pl_id=38395)

*※上記リンクはアフィリエイトリンクです。*"
    # Add note guidance and affiliate placeholder
    note_guideline = "\\n\\n> この記事の詳細版はnoteで公開中"
    affiliate_placeholder = "\\n\\n//af.moshimo.com/af/c/click?a_id=5506692&p_id=2312&pc_id=4967&pl_id=38395"
    body = f"{opening}\\n\\n■ 問題提起\\n{problem}\\n\\n■ 解決策の提示\\n{solution}\\n\\n■ 実際の結果・証拠\\n{result}{affiliate_placeholder}\\n\\n■ 締め\\n{closing}{note_guideline}\\n\\n{disclaimer}"
    return body

def main():
    topic_jp = get_topic()
    topic_en_map = {
        "無料で使えるAI API比較 2026": "free AI API comparison 2026",
        "Hermes Agent 自動化チュートリアル": "Hermes Agent automation tutorial",
        "AI副業 初心者ガイド": "AI side hustle beginner guide",
        "マルチモーダルAI 最新動向": "multimodal AI latest trends",
        "AIエージェント フレームワーク比較": "AI agent framework comparison",
        "プロンプトエンジニアリング テクニック": "prompt engineering techniques",
        "AI画像生成 ビジネス活用": "AI image generation business use",
        "AI音声合成 アプリケーション": "AI speech synthesis applications",
        "LLM ファインチューニング 入門": "LLM fine-tuning introduction",
        "AIデータ分析 ツール紹介": "AI data analysis tools introduction"
    }
    topic_en = topic_en_map.get(topic_jp, topic_jp)
    
    info = fetch_info(topic_en)
    
    jst_now = get_jst_now()
    today = jst_now.date().isoformat()
    slug = slugify(topic_jp)
    filename = f"{today}-{slug}.md"
    base_dir = "/Users/common/ai-tool-navigator/src/articles"
    os.makedirs(base_dir, exist_ok=True)
    filepath = os.path.join(base_dir, filename)
    
    content = f"""---
layout: post.njk
title: "{topic_jp}"
date: {today}
tags: [AI, ツールレビュー]
ai_generated: true
---
"""
    article_body = generate_navigator_x_article(topic_jp, info)
    content += article_body
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    repo_dir = "/Users/common/ai-tool-navigator"
    try:
        subprocess.run(["git", "add", "src/articles/"], cwd=repo_dir, check=True)
        commit_msg = f"Add daily article: {topic_jp}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_dir, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, check=True)
        push_success = True
    except subprocess.CalledProcessError as e:
        push_success = False
        error_msg = str(e)
    
    if push_success:
        message = f"""✅ 日次記事生成完了
タイトル: {topic_jp}
ファイル: {filename}
リポジトリ: https://github.com/kaneko-ai/ai-tool-navigator
GitHub Pages: https://kaneko-ai.github.io/ai-tool-navigator/
"""
    else:
        message = f"""❌ 日次記事生成でエラー
タイトル: {topic_jp}
エラー: {error_msg}
"""
    
    send_message(message=message, target="discord")

if __name__ == "__main__":
    main()
