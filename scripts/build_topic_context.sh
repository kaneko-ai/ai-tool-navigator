#!/usr/bin/env bash
# Python版へのラッパー
# 使い方: build_topic_context.sh <output_file> [days] [articles_dir]
#   後方互換性のため第2引数は days として解釈する（articles_dirは第3引数）
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OUTPUT_FILE="${1:-/tmp/recent_topics.txt}"
DAYS="${2:-30}"
ARTICLES_DIR="${3:-$REPO_ROOT/src/articles}"

python3 "$SCRIPT_DIR/build_topic_context.py" "$OUTPUT_FILE" "$ARTICLES_DIR" "$DAYS"
