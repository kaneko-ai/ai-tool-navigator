#!/usr/bin/env bash
# 19:00 cron の進捗をリアルタイム監視
# Usage: ./scripts/watch_daily_cron.sh
#   30秒ごとに状態を更新表示
#   本日分の auto_published commit を検出したら自動終了
#   Ctrl+C で手動終了
set -euo pipefail
cd "$(dirname "$0")/.."

TODAY=$(TZ=Asia/Tokyo date +%Y-%m-%d)
STAGE0_LOG="$HOME/Library/Logs/ai-tool-navigator/stage0.log"

while true; do
  clear
  echo "=========================================="
  echo "  Watch Daily Cron — $(TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M:%S JST')"
  echo "  本日対象: $TODAY"
  echo "=========================================="
  echo ""

  echo "## [1] Stage 0 ログ末尾 (launchd, 18:55 起動分)"
  if [ -f "$STAGE0_LOG" ]; then
    tail -n 8 "$STAGE0_LOG" | sed 's/^/    /'
  else
    echo "    (ログ未生成)"
  fi
  echo ""

  echo "## [2] 最新の GitHub Actions run (5件)"
  gh run list --workflow=daily-article.yml --limit 5 2>/dev/null | sed 's/^/    /' || echo "    (gh CLI エラー)"
  echo ""

  echo "## [3] git remote の直近 commit (5件)"
  git fetch origin main --quiet 2>/dev/null || true
  git --no-pager log origin/main --oneline -5 | sed 's/^/    /'
  echo ""

  echo "## [4] drafts/$TODAY/ の中身"
  if [ -d "drafts/$TODAY" ]; then
    ls -la "drafts/$TODAY/" | tail -n +2 | sed 's/^/    /'
  else
    echo "    (未生成)"
  fi
  echo ""

  echo "## [5] src/articles/$TODAY.md (Phase A 公開対象)"
  if [ -f "src/articles/$TODAY.md" ]; then
    echo "    ✅ 存在: $(wc -c < src/articles/$TODAY.md) bytes"
    head -8 "src/articles/$TODAY.md" | sed 's/^/    | /'
  else
    echo "    ⏳ 未公開"
  fi
  echo ""

  echo "=========================================="
  echo "(30秒ごとに更新 / Ctrl+C で終了)"

  # 終了判定: 本日分の auto_published=yes commit があれば自動終了
  if git --no-pager log origin/main --oneline -10 | grep -q "Daily draft: $TODAY .*auto_published=yes"; then
    echo ""
    echo "🎉 本日分の auto_published=yes commit を検出！監視終了。"
    echo ""
    git --no-pager log origin/main --oneline -3
    break
  fi

  sleep 30
done
