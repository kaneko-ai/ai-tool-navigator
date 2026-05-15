#!/usr/bin/env python3
"""直近N日の記事タイトル一覧を抽出し、トピック選定プロンプトに渡すコンテキストを生成する。

bash 3.2 (macOS) / bash 5+ (Linux) の挙動差を回避するためPython製。
"""
import sys
import re
from pathlib import Path
from datetime import date, timedelta

output_file = sys.argv[1] if len(sys.argv) > 1 else "/tmp/recent_topics.txt"
articles_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("src/articles")
days = int(sys.argv[3]) if len(sys.argv) > 3 else 30

threshold = date.today() - timedelta(days=days)

lines = []
lines.append(f"## 直近{days}日間に公開済みの記事タイトル一覧（重複・類似テーマ禁止）")
lines.append("")

match_count = 0
date_re = re.compile(r"^(\d{4}-\d{2}-\d{2})")

for f in sorted(articles_dir.glob("*.md")):
    m = date_re.match(f.name)
    if not m:
        continue
    try:
        file_date = date.fromisoformat(m.group(1))
    except ValueError:
        continue
    if file_date < threshold:
        continue

    title = "(no title)"
    tags = "(no tags)"
    try:
        text = f.read_text(encoding="utf-8")
    except Exception:
        continue
    for line in text.splitlines()[:30]:
        if line.startswith("title:"):
            title = line[len("title:"):].strip().strip('"').strip("'")
        elif line.startswith("tags:"):
            tags = line[len("tags:"):].strip()
    lines.append(f"- {file_date.isoformat()} | {title} | {tags}")
    match_count += 1

lines.append("")
lines.append("### 重複判定ルール")
lines.append("- 上記タイトルと主題（メインキーワード）が一致するテーマは選定禁止")
lines.append("- タイトル中の主要名詞が2語以上一致する場合は別の切り口に変更すること")
lines.append("- 例: 「AI副業で月5万円」と「副業で月5万円稼ぐAI」は重複扱い")
lines.append("")
lines.append("### フォールバック指示")
lines.append("- 上記リストが空でも、軸0-29から1件を自律的に選び、停止せず必ず展開ノートを生成すること")
lines.append("- 「必須入力が不足」等の理由で生成を拒否してはならない")

Path(output_file).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"✅ 生成完了: {output_file} (マッチ件数: {match_count})")
