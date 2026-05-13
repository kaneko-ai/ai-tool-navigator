#!/usr/bin/env python3
"""既存記事のtagsを統一タグセットに正規化する"""
import re
import sys
from pathlib import Path

TAG_MAP = {
    "2026-04-23-nvidia-nim-api.md": ["ai-tools", "llm"],
    "2026-04-23-hermes-agent.md": ["agent", "tutorial"],
    "2026-04-23-hermes-agent-vs-openclaw.md": ["comparison", "agent"],
    "2026-04-23-ai.md": ["news", "ai-tools"],
    "2026-04-23-ai-5.md": ["side-business"],
    "2026-04-23-2026-ai-api-nvidia-nim-google-ai-etc.md": ["comparison", "llm"],
    "2026-04-24-ai-hermes-vs-langchain.md": ["comparison", "agent"],
    "2026-04-27-ai.md": ["comparison", "ai-tools"],
    "2026-04-28-llmai.md": ["llm", "tutorial"],
    "2026-04-29-ai.md": ["comparison", "ai-tools"],
    "2026-04-30-ai-api-2026.md": ["comparison", "llm"],
    "2026-05-01-freellmapi-14401.md": ["llm", "tutorial"],
    "2026-05-02-ai5.md": ["side-business", "tutorial"],
    "2026-05-03-aigpt-5-vs-gemini-vs-claude.md": ["comparison", "llm"],
    "2026-05-04-ai-langchain-vs-autogen-vs-crewai.md": ["comparison", "agent"],
    "2026-05-07-2026.md": ["career", "news"],
    "2026-05-08-llmai.md": ["llm", "tutorial"],
    "2026-05-08-ai.md": ["career", "tutorial"],
    "2026-05-09-2026ai5gepythonai.md": ["career", "tutorial"],
    "2026-05-10-2026799.md": ["career", "news"],
    "2026-05-11-hermes-agent.md": ["agent", "tutorial"],
    "2026-05-11-ai2026595900.md": ["career", "news"],
    "2026-05-12-it72026saasai.md": ["comparison", "career"],
    "2026-05-12-ai5.md": ["side-business", "tutorial"],
    "2026-05-13-miraif-career-guide.md": ["career"],
}

ARTICLES_DIR = Path("src/articles")
updated = 0
skipped = 0

for fname, new_tags in TAG_MAP.items():
    path = ARTICLES_DIR / fname
    if not path.exists():
        print(f"⚠️  Skip (not found): {fname}")
        skipped += 1
        continue

    content = path.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not fm_match:
        print(f"⚠️  No front-matter: {fname}")
        skipped += 1
        continue

    fm = fm_match.group(1)
    rest = content[fm_match.end():]

    # 既存のtags行を削除（単一行形式・複数行リスト形式の両方に対応）
    fm_lines = fm.split("\n")
    new_fm_lines = []
    skip_until_unindent = False
    for line in fm_lines:
        if skip_until_unindent:
            if line.startswith(("  - ", "- ", "    ")):
                continue
            else:
                skip_until_unindent = False
        stripped = line.strip()
        if stripped.startswith("tags:"):
            if stripped == "tags:":
                skip_until_unindent = True
                continue
            else:
                # tags: [...] や tags: foo の単一行
                continue
        new_fm_lines.append(line)

    # 末尾にtags行を追加（JSON互換YAML形式）
    tags_json = ", ".join(f'"{t}"' for t in new_tags)
    new_fm_lines.append(f"tags: [{tags_json}]")

    new_fm = "\n".join(new_fm_lines)
    new_content = f"---\n{new_fm}\n---\n{rest}"
    path.write_text(new_content, encoding="utf-8")
    print(f"✅ {fname} → {new_tags}")
    updated += 1

print(f"\n=== 完了 ===\nUpdated: {updated}\nSkipped: {skipped}")
