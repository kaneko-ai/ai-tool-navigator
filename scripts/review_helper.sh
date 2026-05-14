#!/usr/bin/env bash
# review_helper.sh - 記事Markdown の機械校閲（grep ベース、追加コストなし）
# 使い方: bash scripts/review_helper.sh <path/to/article.md>
# 終了コード: 0=OK, 1=warning, 2=error

set -o pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <path/to/article.md>" >&2
  exit 2
fi

FILE="$1"
if [ ! -f "$FILE" ]; then
  echo "ERROR: ファイルが存在しません: $FILE" >&2
  exit 2
fi

ERRORS=0
WARNINGS=0
emit_error() { echo "[ERROR] $1"; ERRORS=$((ERRORS + 1)); }
emit_warn()  { echo "[WARN ] $1"; WARNINGS=$((WARNINGS + 1)); }
emit_ok()    { echo "[OK   ] $1"; }

echo "=== Review: $FILE ==="
echo ""

# ============================================================
# 1. 誇大表現リスト（grep -E パターン1本に集約）
# ============================================================
echo "[1/5] 誇大表現チェック"
EXAG_PATTERN='最速|業界No\.1|業界一|絶対|100%稼げる|必ず合格|圧倒的|誰でも簡単|誰でも稼げる|確実に儲かる|必ず儲かる'
EXAG_HITS=$(grep -nE "$EXAG_PATTERN" "$FILE" 2>/dev/null || true)
if [ -n "$EXAG_HITS" ]; then
  emit_error "誇大表現を検出"
  echo "$EXAG_HITS" | head -5 | sed 's/^/    /'
else
  emit_ok "誇大表現なし"
fi
echo ""

# ============================================================
# 2. 一人称ペルソナ・架空ブランド
# ============================================================
echo "[2/5] 一人称ペルソナ・架空ブランド チェック"
PERSONA_PATTERN='技術ブロガーの〇〇|技術ブロガーの○○|技術ブロガーの[^ 　、。]|私は元SIer|私は元エンジニア|皆さん.{0,3}こんにちは|Navigator X|の航海|こんにちは.{0,3}技術ブロガー'
PERSONA_HITS=$(grep -nE "$PERSONA_PATTERN" "$FILE" 2>/dev/null || true)
if [ -n "$PERSONA_HITS" ]; then
  emit_error "虚偽の一人称ペルソナ・架空ブランドを検出"
  echo "$PERSONA_HITS" | head -5 | sed 's/^/    /'
else
  emit_ok "ペルソナ問題なし"
fi
echo ""

# ============================================================
# 3. 本文末尾の途中切れ検出（Python で堅牢に判定）
# ============================================================
echo "[3/5] 本文末尾チェック"
END_OK=$(python3 -c "
import sys
with open('$FILE', encoding='utf-8') as f:
    lines = [l.rstrip() for l in f if l.strip()]
# CTA フッター（moshimo / アフィリエイト注記 / 共通 CTA セクション）を末尾から除外
SKIP_PATTERNS = [
    '※上記リンクはアフィリエイト',
    'CTA:MOSHIMO',
    'ConoHa WING',
    '※本記事は広告',
    '* * *',
    '---',
]
while lines and any(pat in lines[-1] for pat in SKIP_PATTERNS):
    lines.pop()
# 見出し行のみで終わるのも本文末尾とは認めない
while lines and lines[-1].lstrip().startswith('#'):
    lines.pop()
if not lines:
    print('EMPTY')
    sys.exit()
last = lines[-1].rstrip('*_ 　')
ok_chars = ['。', '！', '？', '）', '.', '!', '?', ')', '\"', \"'\", '」', '』']
if any(last.endswith(c) for c in ok_chars):
    print('OK:' + last[-30:])
else:
    print('NG:' + last[-50:])
")
case "$END_OK" in
  OK:*) emit_ok "末尾句点OK ${END_OK#OK:}" ;;
  NG:*) emit_error "末尾切れ疑い: ${END_OK#NG:}" ;;
  EMPTY) emit_error "ファイル本文が空" ;;
  *) emit_warn "末尾判定失敗: $END_OK" ;;
esac
echo ""

# ============================================================
# 4. 出典URL数
# ============================================================
echo "[4/5] 出典URLチェック"
URL_COUNT=$(grep -oE 'https?://[^[:space:])"<>]+' "$FILE" 2>/dev/null | sort -u | wc -l | tr -d ' ')
if [ "${URL_COUNT:-0}" -ge 3 ]; then
  emit_ok "出典URL数: ${URL_COUNT} 件"
else
  emit_warn "出典URL数: ${URL_COUNT} 件（3件未満）"
fi
echo ""

# ============================================================
# 5. AI開示の本文内必須
# ============================================================
echo "[5/5] AI開示チェック"
# front-matterに ai_assisted: true があれば post.njk 側で自動出力されるためOK
if awk 'BEGIN{c=0} /^---$/{c++; next} c==1 && /^ai_assisted: *true/{found=1; exit} END{exit !found}' "$FILE"; then
  emit_ok "ai_assisted: true をfront-matterで検出（テンプレート側で開示文を自動出力）"
elif awk 'BEGIN{c=0} /^---$/{c++; next} c >= 2 && (/※本記事は ?AI/ || /本記事は ?AI/ || /AI を活用/ || /AIを活用/ || /本記事はAIで下書き/ || /AIで下書きを作成/) { print; exit }' "$FILE" | grep -q .; then
  emit_ok "AI開示文を本文内に検出"
else
  emit_warn "AI開示文が本文内・front-matter共に見つかりません"
fi

# ============================================================
# 文字数（参考）
# ============================================================
CHARS=$(wc -m < "$FILE" | tr -d ' ')
echo "[INFO] 総文字数: $CHARS"
if [ "${CHARS:-0}" -lt 2500 ]; then
  emit_warn "文字数 $CHARS が 2500字未満"
elif [ "${CHARS:-0}" -gt 3800 ]; then
  emit_warn "文字数 $CHARS が 3800字超過"
fi
echo ""

echo "==================================="
echo "Summary: errors=$ERRORS, warnings=$WARNINGS"
echo "==================================="

if [ $ERRORS -gt 0 ]; then
  exit 2
elif [ $WARNINGS -gt 0 ]; then
  exit 1
else
  exit 0
fi
