#!/usr/bin/env bash
# 直近30日の記事タイトル一覧を抽出し、トピック選定プロンプトに渡すコンテキストを生成する
set -euo pipefail

OUTPUT_FILE="${1:-/tmp/recent_topics.txt}"
ARTICLES_DIR="${2:-src/articles}"
DAYS="${3:-30}"

# 日付しきい値（GNU date / BSD date 両対応）
if date -v-1d +%Y-%m-%d >/dev/null 2>&1; then
  THRESHOLD=$(date -v-${DAYS}d +%Y-%m-%d)
else
  THRESHOLD=$(date -d "${DAYS} days ago" +%Y-%m-%d)
fi

{
  echo "## 直近${DAYS}日間に公開済みの記事タイトル一覧（重複・類似テーマ禁止）"
  echo ""
  for f in "${ARTICLES_DIR}"/*.md; do
    [ -f "$f" ] || continue
    fname=$(basename "$f")
    file_date="${fname:0:10}"
    if [[ "$file_date" > "$THRESHOLD" || "$file_date" == "$THRESHOLD" ]]; then
      title=$(grep -m1 '^title:' "$f" | sed 's/^title: *//; s/^"//; s/"$//')
      tags=$(grep -m1 '^tags:' "$f" | sed 's/^tags: *//')
      echo "- ${file_date} | ${title} | ${tags}"
    fi
  done
  echo ""
  echo "### 重複判定ルール"
  echo "- 上記タイトルと主題（メインキーワード）が一致するテーマは選定禁止"
  echo "- タイトル中の主要名詞が2語以上一致する場合は別の切り口に変更すること"
  echo "- 例: 「AI副業で月5万円」と「副業で月5万円稼ぐAI」は重複扱い"
} > "${OUTPUT_FILE}"

echo "✅ 生成完了: ${OUTPUT_FILE}"
echo "--- 内容プレビュー ---"
head -40 "${OUTPUT_FILE}"
