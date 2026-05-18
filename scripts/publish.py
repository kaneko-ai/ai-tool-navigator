#!/usr/bin/env python3
"""
publish.py — drafts/<date>/04_final.md を src/articles/<date>.md として公開する。

変換ルール (docs/publish-design.md 準拠):
  1. 冒頭の空行・独白を除去（最初の `---` までスキップ）
  2. front-matter 内 `editor_reviewed: false` → `true`
  3. 末尾の自動チェック結果ブロック（最終 `---` 区切り以降のメタ情報）を削除
  4. `<!-- MODEL_USED: ... -->` は保持（末尾に1行）
  5. front-matter 終端の改行保証
  6. ファイル名: <date>.md（slug 未対応、重複時 -2, -3, ...）

Usage:
  python3 scripts/publish.py <YYYY-MM-DD>           # 本番書き込み
  python3 scripts/publish.py <YYYY-MM-DD> --dry-run # 標準出力に変換結果のみ表示
"""
import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = REPO_ROOT / "drafts"
ARTICLES_DIR = REPO_ROOT / "src" / "articles"


def fail(msg: str) -> None:
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)


def parse_args():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    date = args[0]
    dry_run = "--dry-run" in args[1:]
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        fail(f"date は YYYY-MM-DD 形式で指定してください: {date!r}")
    return date, dry_run


def load_draft(date: str) -> str:
    draft_path = DRAFTS_DIR / date / "04_final.md"
    if not draft_path.exists():
        fail(f"draft が存在しません: {draft_path}")
    return draft_path.read_text(encoding="utf-8")


def strip_leading_noise(text: str) -> str:
    """最初の `---` 行までをスキップする。"""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "---":
            return "\n".join(lines[i:])
    fail("front-matter 開始の `---` が見つかりません。")


def split_frontmatter(text: str):
    """先頭 front-matter ブロックと残り本文を分離する。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail("先頭が `---` で始まっていません。strip_leading_noise の後で呼ばれるはず。")
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        fail("front-matter 終端の `---` が見つかりません。")
    fm = "\n".join(lines[: end_idx + 1])
    body = "\n".join(lines[end_idx + 1 :])
    return fm, body


def flip_editor_reviewed(fm: str) -> str:
    """editor_reviewed: false → true。"""
    new_fm, n = re.subn(
        r"^(editor_reviewed:\s*)false\s*$",
        r"\1true",
        fm,
        count=1,
        flags=re.MULTILINE,
    )
    if n == 0:
        print("⚠️  editor_reviewed: false が見つかりませんでした（既に true か未定義）。", file=sys.stderr)
    return new_fm


def strip_trailing_meta(body: str):
    """
    本文末尾の `---` 区切り以降のメタ情報ブロックを削除する。
    `<!-- MODEL_USED: ... -->` 行は保持して末尾に再付与する。
    戻り値: (clean_body, model_used_line or None)
    """
    # MODEL_USED コメントを先に抽出
    model_used_line = None
    m = re.search(r"<!--\s*MODEL_USED:[^>]*-->", body)
    if m:
        model_used_line = m.group(0).strip()

    lines = body.splitlines()
    # 末尾から走査し、最後の `---` 行を探す
    last_sep_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "---":
            last_sep_idx = i
            break

    if last_sep_idx is not None:
        # `---` 以降にメタブロックがあると判断し、`---` 含めて切り捨て
        clean_lines = lines[:last_sep_idx]
    else:
        clean_lines = lines

    # 末尾の空行を除去
    while clean_lines and clean_lines[-1].strip() == "":
        clean_lines.pop()

    return "\n".join(clean_lines), model_used_line


def resolve_output_path(date: str) -> Path:
    """同名重複時は -2, -3, ... を付ける。"""
    base = ARTICLES_DIR / f"{date}.md"
    if not base.exists():
        return base
    n = 2
    while True:
        candidate = ARTICLES_DIR / f"{date}-{n}.md"
        if not candidate.exists():
            return candidate
        n += 1


def main():
    date, dry_run = parse_args()
    raw = load_draft(date)

    stripped = strip_leading_noise(raw)
    fm, body = split_frontmatter(stripped)
    fm = flip_editor_reviewed(fm)
    clean_body, model_used_line = strip_trailing_meta(body)

    # 組み立て: front-matter + 空行 + 本文 + 末尾 MODEL_USED
    parts = [fm, "", clean_body.lstrip("\n")]
    output = "\n".join(parts).rstrip() + "\n"
    if model_used_line:
        output += model_used_line + "\n"

    if dry_run:
        print("===== DRY RUN OUTPUT =====")
        print(output, end="")
        print("===== END =====")
        print(f"[INFO] 出力先候補: {resolve_output_path(date)}", file=sys.stderr)
        print(f"[INFO] 本文行数: {len(output.splitlines())}", file=sys.stderr)
        return

    out_path = resolve_output_path(date)
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")
    print(f"✅ 公開しました: {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
