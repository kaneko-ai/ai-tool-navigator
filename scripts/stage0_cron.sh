#!/bin/bash
set -u
REPO_DIR="/Users/common/ai-tool-navigator"
LOG_DIR="${HOME}/Library/Logs/ai-tool-navigator"
LOG="${LOG_DIR}/stage0.log"
mkdir -p "${LOG_DIR}"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${LOG}"
}

log "=== Stage 0 cron start ==="
cd "${REPO_DIR}" || { log "ERROR: cd failed"; exit 1; }

export PATH="${HOME}/.local/bin:${HOME}/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"

if ! git pull --ff-only origin main >> "${LOG}" 2>&1; then
  log "WARN: pre-pull non-ff or failed, continuing"
fi

DATE_JST=$(TZ=Asia/Tokyo date +%Y-%m-%d)
TRENDS_JSON="${REPO_DIR}/drafts/${DATE_JST}/00_trends.json"

if [ -f "${TRENDS_JSON}" ]; then
  log "INFO: ${TRENDS_JSON} already exists, skipping"
  log "=== Stage 0 cron end (skipped) ==="
  exit 0
fi

log "INFO: fetching trends for ${DATE_JST}"
if ! /Users/common/anaconda3/bin/python3 scripts/stage0_trend_fetch.py "${DATE_JST}" >> "${LOG}" 2>&1; then
  log "ERROR: stage0_trend_fetch.py failed"
  exit 1
fi

if [ ! -f "${TRENDS_JSON}" ]; then
  log "ERROR: ${TRENDS_JSON} was not created"
  exit 1
fi

SIZE=$(wc -c < "${TRENDS_JSON}" | tr -d ' ')
log "INFO: ${TRENDS_JSON} created (${SIZE} bytes)"

git add "drafts/${DATE_JST}/00_trends.json" "drafts/${DATE_JST}/00_trends_summary.md" 2>>"${LOG}"
if git diff --staged --quiet; then
  log "INFO: no changes to commit"
else
  if git commit -m "stage0: ${DATE_JST} のXトレンド取得" >> "${LOG}" 2>&1; then
    log "INFO: commit OK"
    if git push origin main >> "${LOG}" 2>&1; then
      log "INFO: push OK"
    else
      log "ERROR: push failed"
      exit 1
    fi
  fi
fi

log "=== Stage 0 cron end (success) ==="
