#!/bin/bash
set -u

# =============================================================
# generate_article.sh
# Copilotクレジット枯渇期間の代替: hermes(grok-4.3)で記事を半自動生成
# 使い方:
#   1) トレンド取得＋一覧表示（トピック選定用）:
#        ./scripts/generate_article.sh
#   2) トピックを指定して記事生成:
#        ./scripts/generate_article.sh "カテゴリ: フリーランス / 副業
#        テーマ: 副業で信頼できる案件を見つける現実的な方法"
# 生成後は人が内容確認し、publish.py で公開する（このスクリプトは公開しない）
# =============================================================

REPO_DIR="/Users/common/ai-tool-navigator"
cd "$REPO_DIR" || { echo "ERROR: repo dir not found"; exit 1; }

# JSTの今日の日付
TODAY="$(TZ=Asia/Tokyo date +%Y-%m-%d)"
DRAFT_DIR="drafts/${TODAY}"
TRENDS_SUMMARY="${DRAFT_DIR}/00_trends_summary.md"
FINAL="${DRAFT_DIR}/04_final.md"
STDERR="${DRAFT_DIR}/04_final.stderr"

PROVIDER="xai-oauth"
MODEL="grok-4.3"

echo "===== generate_article.sh ($(date +%T)) ====="
echo "対象日: ${TODAY}"

# ---- Stage 0: トレンド取得（無ければ） ----
if [ ! -f "${DRAFT_DIR}/00_trends.json" ]; then
  echo "[stage0] トレンド未取得。取得します..."
  python3 scripts/stage0_trend_fetch.py 2>&1 | tail -8
else
  echo "[stage0] トレンド取得済み（スキップ）: ${DRAFT_DIR}/00_trends.json"
fi

# ---- 引数なし: 一覧表示して終了 ----
TOPIC="${1:-}"
TAGS="${2:-}"   # カンマ区切りで明示指定可（例: "english-learning,ai-tools"）。未指定ならgrokが選ぶ
if [ -z "${TOPIC}" ]; then
  echo ""
  echo "===== 本日のトレンドサマリ（この中から1件選んでトピックを指定してください）====="
  cat "${TRENDS_SUMMARY}"
  echo ""
  echo "----------------------------------------------------------------"
  echo "次のステップ: トピックを指定して再実行してください。例:"
  echo "  ./scripts/generate_article.sh \"カテゴリ: フリーランス / 副業"
  echo "  テーマ: 副業で信頼できる案件を見つける現実的な方法\""
  echo "----------------------------------------------------------------"
  exit 0
fi

# ---- タグブロックの構築 ----
if [ -n "${TAGS}" ]; then
  # 明示指定: カンマ区切りを "  - xxx" 形式に展開
  TAGS_BLOCK="$(echo "${TAGS}" | tr ',' '\n' | sed 's/^ *//; s/ *$//; /^$/d; s/^/  - /')"
  TAG_INSTRUCTION="上記のtagsはそのまま使用すること。"
else
  # 未指定: 無難なデフォルト＋grokに選ばせる指示
  TAGS_BLOCK="  - ai-tools"
  TAG_INSTRUCTION="tags は次の語彙から記事内容に合うものを2〜3個だけ選んで置き換えること（新しいタグ名は作らない）: ai-tools, english-learning, freelance, side-business, ai-learning, career"
fi

# ---- 記事生成 ----
echo ""
echo "[generate] grok(${MODEL}) で記事生成を開始..."
echo "[generate] トピック: ${TOPIC}"
date +%T

PROMPT="$(cat prompts/02_draft.md)
===
# 追加の出力形式指示（最重要・必ず守る）
記事の一番先頭に、以下の YAML front-matter を必ず付けてください。
---
layout: post.njk
title: \"（30字程度の記事タイトル。）\"
description: \"（120-150字の説明文。）\"
date: ${TODAY}
tags:
${TAGS_BLOCK}
ai_assisted: true
editor_reviewed: false
provider: \"hermes_grok_manual\"
character_count: 0
---
※タグについて: ${TAG_INSTRUCTION}
（本文は 02_draft.md のルールに従って執筆）
===
# 本日のトピック
${TOPIC}
"

hermes -z "${PROMPT}" --provider "${PROVIDER}" -m "${MODEL}" \
  > "${FINAL}" 2> "${STDERR}"

date +%T

# ---- 生成結果チェック ----
echo ""
echo "===== 生成結果チェック ====="
if [ ! -s "${FINAL}" ]; then
  echo "ERROR: ${FINAL} が空です。stderr を確認してください:"
  cat "${STDERR}"
  exit 1
fi

echo "ファイル: ${FINAL}"
wc -l -c "${FINAL}"
echo "--- 先頭15行 ---"
head -15 "${FINAL}"
echo "--- H2見出し数 ---"
grep -c "^## " "${FINAL}"
echo "--- CTAプレースホルダ位置 ---"
grep -n "CTA:" "${FINAL}"
echo "--- 末尾5行（途切れ確認）---"
tail -5 "${FINAL}"
if [ -s "${STDERR}" ]; then
  echo "--- stderr（参考）---"
  head -10 "${STDERR}"
fi

echo ""
echo "----------------------------------------------------------------"
echo "確認後、問題なければ公開してください:"
echo "  python3 scripts/publish.py ${TODAY}"
echo "  npx @11ty/eleventy"
echo "  git add src/articles/${TODAY}.md ${DRAFT_DIR}/00_trends.json ${DRAFT_DIR}/00_trends_summary.md ${FINAL}"
echo "  git commit -m \"feat(article): ${TODAY} 記事公開（hermes/grok手動生成）\""
echo "  git push origin main"
echo "----------------------------------------------------------------"
