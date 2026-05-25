#!/usr/bin/env python3
"""
weekly_summary.py — 過去7日間の運用サマリを Markdown で出力する。

GitHub Actions の weekly-summary.yml から実行され、出力を Issues として投稿する。
ローカル実行時は標準出力に Markdown を出すだけ（dry-run 相当）。

Usage:
  python3 scripts/weekly_summary.py                # 標準出力
  python3 scripts/weekly_summary.py --output FILE  # ファイル出力
  python3 scripts/weekly_summary.py --days 14      # 集計期間変更（既定7日）
"""
import sys
import re
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "src" / "articles"
DRAFTS_DIR = REPO_ROOT / "drafts"

JST = timezone(timedelta(hours=9))


def run_git(args, default=""):
    try:
        r = subprocess.run(["git", "-C", str(REPO_ROOT)] + args,
                          capture_output=True, text=True, check=True)
        return r.stdout.strip()
    except subprocess.CalledProcessError:
        return default


def get_commits_in_range(since_iso, until_iso):
    """指定範囲のコミットを取得"""
    log = run_git(["log", f"--since={since_iso}", f"--until={until_iso}",
                   "--pretty=format:%H|%ai|%s", "--no-merges"])
    if not log:
        return []
    commits = []
    for line in log.split("\n"):
        if "|" in line:
            sha, date, subject = line.split("|", 2)
            commits.append({"sha": sha, "date": date, "subject": subject})
    return commits


def parse_frontmatter(md_path):
    """記事のfrontmatterから tags, title を抽出"""
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fm = m.group(1)
    result = {}
    title_m = re.search(r'^title:\s*"?(.+?)"?\s*$', fm, re.MULTILINE)
    if title_m:
        result["title"] = title_m.group(1)
    tags = re.findall(r"^\s*-\s*(.+?)\s*$", fm, re.MULTILINE)
    if tags:
        result["tags"] = tags
    return result


def count_cta_in_article(md_path):
    """記事内のCTAキーを集計"""
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return {}
    return {
        "A8_NEURODIVE": text.count("CTA:A8_NEURODIVE"),
        "A8_FREELANCEBOARD": text.count("CTA:A8_FREELANCEBOARD"),
        "MOSHIMO_CONOHA_WING": text.count("CTA:MOSHIMO_CONOHA_WING"),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--output", type=str, default=None)
    args = p.parse_args()

    now = datetime.now(JST)
    since = now - timedelta(days=args.days)
    since_iso = since.strftime("%Y-%m-%d %H:%M:%S")
    until_iso = now.strftime("%Y-%m-%d %H:%M:%S")

    # === 1. 期間内コミット ===
    commits = get_commits_in_range(since_iso, until_iso)

    # === 2. 公開記事（期間内で src/articles/ に追加されたファイル）===
    published_files = []
    diff_added = run_git(["log", f"--since={since_iso}", f"--until={until_iso}",
                          "--name-only", "--pretty=format:", "--diff-filter=A"])
    for line in diff_added.split("\n"):
        line = line.strip()
        if line.startswith("src/articles/") and line.endswith(".md"):
            published_files.append(line)
    published_files = sorted(set(published_files))

    # === 3. Daily draft 関連コミット解析 ===
    daily_commits = [c for c in commits if "Daily draft:" in c["subject"]]
    gate_pass = [c for c in daily_commits if "gate_fail=0" in c["subject"]]
    gate_fail = [c for c in daily_commits if "gate_fail=1" in c["subject"]]
    auto_published_yes = [c for c in daily_commits if "auto_published=yes" in c["subject"]]
    auto_published_skipped = [c for c in daily_commits if "auto_published=skipped" in c["subject"]]
    auto_published_failed = [c for c in daily_commits if "auto_published=failed" in c["subject"]]

    # === 4. Phase B-1 で除去された独白サンプル ===
    preamble_files = []
    if DRAFTS_DIR.exists():
        for d in sorted(DRAFTS_DIR.glob("2026-*")):
            p_file = d / "_preamble_removed.txt"
            if p_file.exists():
                # 期間内のみ
                mtime = datetime.fromtimestamp(p_file.stat().st_mtime, JST)
                if since <= mtime <= now:
                    preamble_files.append(p_file)

    # === 5. CTA配置の集計（公開記事全体）===
    cta_totals = {"A8_NEURODIVE": 0, "A8_FREELANCEBOARD": 0, "MOSHIMO_CONOHA_WING": 0}
    total_articles = 0
    noindex_articles = 0
    if ARTICLES_DIR.exists():
        for md in sorted(ARTICLES_DIR.glob("*.md")):
            total_articles += 1
            ctas = count_cta_in_article(md)
            for k, v in ctas.items():
                cta_totals[k] += v
            # noindex検出
            try:
                if "noindex: true" in md.read_text(encoding="utf-8"):
                    noindex_articles += 1
            except Exception:
                pass

    # === 6. 期間内公開記事のCTA内訳 ===
    weekly_cta = {"A8_NEURODIVE": 0, "A8_FREELANCEBOARD": 0, "MOSHIMO_CONOHA_WING": 0, "none": 0}
    weekly_titles = []
    for rel_path in published_files:
        md_path = REPO_ROOT / rel_path
        if not md_path.exists():
            continue
        fm = parse_frontmatter(md_path)
        title = fm.get("title", md_path.stem)
        ctas = count_cta_in_article(md_path)
        cta_str_parts = []
        any_cta = False
        for k, v in ctas.items():
            if v > 0:
                weekly_cta[k] += v
                cta_str_parts.append(f"{k}×{v}")
                any_cta = True
        if not any_cta:
            weekly_cta["none"] += 1
            cta_str_parts.append("(CTA省略)")
        weekly_titles.append({
            "path": rel_path,
            "title": title,
            "tags": fm.get("tags", []),
            "cta": ", ".join(cta_str_parts)
        })

    # === Markdown レポート生成 ===
    lines = []
    lines.append(f"# 📊 週次サマリ {since.strftime('%Y-%m-%d')} 〜 {now.strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"**生成日時**: {now.strftime('%Y-%m-%d %H:%M:%S JST')}  ")
    lines.append(f"**集計期間**: 過去{args.days}日間")
    lines.append("")
    lines.append("---")
    lines.append("")

    # サイト全体サマリ
    lines.append("## 🏠 サイト全体スナップショット")
    lines.append("")
    lines.append(f"- 公開記事総数: **{total_articles}本**")
    lines.append(f"- noindex記事数: {noindex_articles}本")
    lines.append(f"- CTA配置（全記事累計）:")
    lines.append(f"  - A8_NEURODIVE: {cta_totals['A8_NEURODIVE']}箇所")
    lines.append(f"  - A8_FREELANCEBOARD: {cta_totals['A8_FREELANCEBOARD']}箇所")
    lines.append(f"  - MOSHIMO_CONOHA_WING: {cta_totals['MOSHIMO_CONOHA_WING']}箇所")
    lines.append("")

    # 今週の公開記事
    lines.append(f"## 📝 今週の公開記事（{len(weekly_titles)}本）")
    lines.append("")
    if weekly_titles:
        for w in weekly_titles:
            tag_str = ", ".join(w["tags"][:3]) if w["tags"] else "(タグなし)"
            lines.append(f"- **{w['title']}**")
            lines.append(f"  - `{w['path']}`")
            lines.append(f"  - tags: {tag_str}")
            lines.append(f"  - CTA: {w['cta']}")
    else:
        lines.append("（今週の新規公開記事はありませんでした）")
    lines.append("")

    # 自動化パイプライン稼働状況
    lines.append("## 🤖 自動化パイプライン稼働状況")
    lines.append("")
    lines.append(f"- Daily draft 実行回数: **{len(daily_commits)}回**")
    lines.append(f"  - gate_fail=0 (品質OK): {len(gate_pass)}回")
    lines.append(f"  - gate_fail=1 (要修正): {len(gate_fail)}回")
    lines.append(f"- Phase A (Auto-publish):")
    lines.append(f"  - ✅ auto_published=yes: {len(auto_published_yes)}回")
    lines.append(f"  - ⏭️ auto_published=skipped (既存記事ガード): {len(auto_published_skipped)}回")
    lines.append(f"  - ❌ auto_published=failed: {len(auto_published_failed)}回")
    lines.append(f"- Phase B-1 (独白自動除去):")
    lines.append(f"  - 除去発生件数: {len(preamble_files)}回")
    if preamble_files:
        lines.append(f"  - サンプル（最新3件）:")
        for pf in preamble_files[-3:]:
            try:
                sample = pf.read_text(encoding="utf-8").strip().split("\n")[0][:80]
                lines.append(f"    - `{pf.parent.name}`: {sample}")
            except Exception:
                pass
    lines.append("")

    # gate_fail パターン分析（subject から拾える範囲で）
    if gate_fail:
        lines.append("## ⚠️ gate_fail=1 発生記録")
        lines.append("")
        for c in gate_fail:
            lines.append(f"- `{c['date'][:10]}`: {c['subject']}")
        lines.append("")
        lines.append("> 対処: drafts/ に保存されています。手動で確認して publish または withdraw を判断してください。")
        lines.append("")

    # 推奨アクション
    lines.append("## ✅ 推奨アクション")
    lines.append("")
    if gate_fail:
        lines.append(f"- [ ] gate_fail draft {len(gate_fail)}件 を確認")
    if cta_totals['A8_NEURODIVE'] == 0 and cta_totals['A8_FREELANCEBOARD'] == 0:
        lines.append("- [ ] CTA が全く配置されていません。記事カテゴリを確認してください")
    if len(weekly_titles) == 0:
        lines.append("- [ ] 今週の公開記事ゼロ。cron が正常稼働しているか確認してください")
    if not gate_fail and len(auto_published_yes) >= 5:
        lines.append("- 🎉 今週は完全自動運用が成功しました。何もする必要はありません。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("_このレポートは GitHub Actions weekly-summary.yml により自動生成されました_")

    output = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ Wrote: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
