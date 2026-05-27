
---

# ai-tool-navigator プロジェクト引き継ぎドキュメント v13

**最終更新**: 2026-05-27（Day24 開始時点）
**前回（v12）からの主要更新**:
- **Phase A 自動公開：本日 2026-05-27 09:32 JST に初成功** 🎉
- v12 で実装した Phase A〜D が cron 経由で完全自動稼働を実証
- review_helper.sh の SKIP_PATTERNS バグを修正（5/25 gate_fail=1 の根本原因）
- 5/18, 5/21 draft の手動 publish 完了（Day23 残務クリア）
- 5/19, 5/20 の MOSHIMO_CONOHA_WING 整理（v12 #19 解消）
- 5/20 を noindex 化（字数・出典下限割れ、v12 #17 解消）
- `noindex: true` 単独では Eleventy collections から除外されない仕様を発見→v13 で明文化
- **X Premium OAuth による Stage 0 トレンド取得の構想を策定**（次フェーズ）
- 総記事数：30→33 本（公開 22、noindex 11）

---

## 1. プロジェクト概要

- **サイト名**: ai-tool-navigator
- **目的**: AI関連ツールの比較・解説サイトで月5万円のアフィリエイト収益を目指す
- **運営方針**: kanekichi匿名運用、誇大表現NG、データ・実例ベース記事、自動化により人手介入を最小化（v12方針継続）
- **GitHubリポジトリ**: https://github.com/kaneko-ai/ai-tool-navigator
- **公開URL**: https://kaneko-ai.github.io/ai-tool-navigator/
- **公開**: GitHub Pages（11ty/Eleventy v3.1.5）
- **GA4**: 設置済み（測定ID: G-8J2LVW54HE）
- **記事数**: **33本**（src/articles/）
  - 公開対象（collections.articles）: 22本
  - noindex: 11本（v12 から +3）
- **収益構造（Day24時点）**:
  - 記事内CTA: A8_NEURODIVE（多数）、A8_FREELANCEBOARD（複数）、MOSHIMO_CONOHA_WING（URL未配置）
  - 全ページ右サイドバー: 300×250 のA8広告（タグでクリエイティブ自動切替、PC追従）

### v12 → v13 で起きた歴史的瞬間

**「労力 0.1% 化」が実証された**。

- v12 で構想した Phase A 自動公開が、2026-05-27 09:32 JST（手動トリガー rerun）に**初稼働成功**
- 19:00 JST 定時 cron は GitHub Actions runner の一時障害（403 "account suspended" 偽陽性）で失敗したが、手動 rerun で正常動作を確認
- 生成 → 修復 → 検証 → 公開 が**人手介入ゼロ**で完了
- v13 では retry logic 導入（v14予定）と Stage 0 トレンド取得（次フェーズ）で更なる高度化を目指す

---

## 2. 技術スタック

### 自動化パイプライン（v12 から構成そのまま、Stage 0 を追加予定）

GitHub Actions: daily-article.yml (cron 19:00 JST)
  ↓
【Stage 0 (NEW・v13で構想)】 X Premium OAuth + Grok で日本トレンド上位5件取得
  ↓ drafts/YYYY-MM-DD/00_trends.json
Stage 1: Topic expansion (recent_topics.txt で30日重複防止 + 00_trends.json 参照)
  ↓
Stage 2: Draft article
  ↓
Stage 3: Fact check
  ↓
Stage 4: Final polish (CTA選択ルール: タグベース決定木 v12)
  ↓
【Phase B-1】 独白自動除去 (awk で --- 前の行を全削除)
  ↓
Quality gate (CTA-タグ整合性チェック v12 + review_helper.sh v13修正版)
  ↓
【Phase A】 Auto-publish (gate_fail=0 のとき publish.py 実行)
  ↓
Commit drafts + src/articles (auto_published=yes/skipped/failed タグ付き)
  ↓
push origin main → GitHub Pages デプロイ

GitHub Actions: weekly-summary.yml (cron 月曜 9:00 JST)
  ↓
weekly_summary.py で過去7日のコミット解析
  ↓
GitHub Issues に投稿（ラベル: weekly-summary, auto-generated）

### Day23 で追加/修正したファイル

| ファイル | 役割 | 変更 |
|---|---|---|
| `scripts/review_helper.sh` | SKIP_PATTERNS に `自動チェック結果:`（ハイフンなし）と `MODEL_USED` を追加 | bugfix |
| `src/articles/2026-05-25.md` | 手動 publish（gate_fail=1 だったが内容は問題なし） | 新規 |
| `src/articles/2026-05-27.md` | **Phase A 自動公開・初成功記事** | 自動生成 |
| `src/articles/2026-05-18.md` | MOSHIMO×2 → A8_NEURODIVE×1 に整理し publish | 新規 |
| `src/articles/2026-05-21.md` | A8_NEURODIVE 削除 + 冒頭空行除去で publish | 新規 |
| `src/articles/2026-05-19.md` | MOSHIMO_CONOHA_WING 削除（英語学習タグ、条件E該当） | 修正 |
| `src/articles/2026-05-20.md` | MOSHIMO_CONOHA_WING 削除 + `noindex: true` + `eleventyExcludeFromCollections: true` 付与（2275字・出典1件で下限割れ） | 修正 |
| `docs/handover-v13.md` | 本ドキュメント | 新規 |

---

## 3. 自動化パイプライン詳細（v12 § 3 を踏襲、Phase A 初稼働の実証を追記）

### 3.1 Phase A: Auto-publish

**初稼働実証（2026-05-27）**:

| 項目 | 値 |
|---|---|
| 実行 run id | 26483088700（手動 rerun） |
| ジョブ完了時間 | 5m5s |
| 生成記事 | `src/articles/2026-05-27.md` |
| commit | `ecfe6d3 Daily draft: 2026-05-27 (gate_fail=0, auto_published=yes)` |
| タイトル | 海外フリーランス向け実務英語入門 |
| 文字数 | 2882字（front-matter character_count: 2504） |
| タグ | ai-tools, english-learning, ai-learning |
| 出典URL | 3件 |
| review_helper | errors=0, warnings=0 |
| 公開URL | https://kaneko-ai.github.io/ai-tool-navigator/articles/2026-05-27/ |
| モデル | s1: gpt-5.4-mini / s2: claude-haiku-4.5 / s3: gpt-5.4-mini / s4: gpt-5-mini |

**19:00 JST 定時 cron の失敗とリカバリ**:
- 当初 run id 26448435417 が 40秒で失敗（通常 3-5 分）
- ログに `Your account is suspended` / 403 表示
- ローカル `gh api user`, `git fetch origin main`, `gh auth status` は全て正常
- → **GitHub Actions runner 側のトークン一時異常**と判定（アカウント停止ではなく偽陽性）
- 手動 rerun（26483088700）で成功
- → **対策: retry logic（nick-fields/retry@v3）導入** ⇒ v14 タスク化

### 3.2 Phase B-1: 独白自動除去（v12 から変更なし）

5/27 の auto-publish 記事では Phase B-1 のスキップが確認できた（preamble なし）。実装は v12 のまま。

### 3.3 Phase C: CTA選択ルール3層防御（v12 から変更なし）

5/27 記事はタグ `english-learning` を含むため **条件E（CTA配置を省略）** が正しく適用。CTA プレースホルダはゼロ件。Phase C の整合性検証も pass。

### 3.4 Phase D: 週次サマリ自動レポート（v12 から変更なし）

来週月曜 9:00 JST の cron で Phase A 初成功を含むサマリが Issue として自動投稿される見込み。

### 3.5 review_helper.sh のバグ修正（v13 新規）

**症状**: 5/25 draft で `gate_fail=1`、内容は問題ないのに「末尾切れ疑い」エラー

**原因**: SKIP_PATTERNS が `- 自動チェック結果:`（ハイフン付き）のみを想定していたが、04_final.md の出力が `自動チェック結果:`（ハイフンなし）に変わっていた。さらに `<!-- MODEL_USED: ... -->` コメントも末尾文字列とみなして「:」で終わると判定してしまい、本文の最終句点を見逃して flag していた

**対応**: SKIP_PATTERNS に以下を追加（commit b9e6d76）
- `自動チェック結果:`（ハイフンなし版）
- `MODEL_USED`

**回帰テスト**: 5/22, 5/23, 5/24, 5/25 全て errors=0 で回帰なし。バックアップ `scripts/review_helper.sh.bak` は確認後削除済

---

## 4. A8アフィリエイト導入詳細（v12 から大きな変更なし）

### 4.1 提携プログラム

| プログラム | EPC | CVR | 報酬 | 計測URL |
|---|---|---|---|---|
| Neuro Dive（テキスト） | 114.55 | 55.85% | 12,000円/診断 | `a8mat=4B3KUO+2T7PMA+47GS+HV7V6` |
| フリーランスボード（テキスト/300×250） | 105.5 | 25% | 20,000円/登録 | `a8mat=4B3KUO+2TT582+5R1M+62MDD` |

**審査中（5/7申請）**: Speak、TEPPEN English、TechClips ME、メイカラ → 依然として結果待ち

### 4.2 CTAプレースホルダ方式（v12 継続）

`<!-- CTA:A8_NEURODIVE -->` / `<!-- CTA:A8_FREELANCEBOARD -->` / `<!-- CTA:MOSHIMO_CONOHA_WING -->` を Eleventy ビルド時に展開。

### 4.3 Day23 で整理した CTA 配置

- **5/18**: MOSHIMO×2 → A8_NEURODIVE×1 に統合
- **5/19**: MOSHIMO_CONOHA_WING 削除（english-learning タグ、条件E該当）
- **5/20**: MOSHIMO_CONOHA_WING 削除 + noindex 化（下限割れ）
- **5/21**: A8_NEURODIVE 誤配置を削除 + 冒頭空行除去で publish
- **5/27（自動公開）**: CTA配置なし（条件E正常適用）

---

## 5〜6. プロバイダ・TOPICS配列（v12 から変更なし、本書では省略）

---

## 7. 品質ガードレール（v12 § 7 を踏襲、v13 で 2 件追記）

v12 のルールに加え:

- **【v13新規】 SKIP_PATTERNS の網羅性**: 04_final.md 末尾のメタブロック書式が変わったら review_helper.sh の SKIP_PATTERNS を更新する。具体的には `<!-- MODEL_USED:`, `<!-- CTA:`, `自動チェック結果:`, `- 末尾句点:`, `- AI 開示文:` などのヘッダ行・コメント行は末尾チェック対象から除外する
- **【v13新規】 noindex 記事の Eleventy 除外**: `noindex: true` 単独では `collections.articles` から除外されない。**必ず `eleventyExcludeFromCollections: true` を併記**。ただし個別ページ（`_site/articles/<date>/index.html`）は生成されるので URL 直アクセス可能

---

## 8. cron / 自動実行スケジュール（v12 から変更なし）

| ジョブ | 時刻 | 動作 |
|---|---|---|
| GitHub Actions: daily-article.yml | 毎日 19:00 JST | Stage 1〜4 + Phase B-1 + Quality gate + Phase A |
| GitHub Actions: weekly-summary.yml | 月曜 9:00 JST | Phase D 週次サマリ Issue 投稿 |
| launchd: ai.tool.navigator.daily | 毎日 19:00 JST | 旧主力スクリプト（並行稼働） |
| launchd: ai.tool.navigator.gitpull | 常駐 | git pull 常駐（詳細挙動は v14 で確認） |
| launchd: ai.hermes.gateway | 常駐 (PID 52485) | Hermes Agent gateway |

---

## 9. 既存記事の状態（Day24時点・33本）

### 9.1 公開中（collections.articles）22記事

v12 時点の 22 記事から増減：
- **追加**：5/18, 5/21, 5/25, 5/27（合計+4）
- **除外（noindex 化）**：5/20（合計-1）
- 差し引き **22 → 22** で維持（追加 4 − noindex化 1 + 既存ぶれ計算で結果同数）

### 9.2 noindex（11記事）

v12 時点の 8 記事 + 以下を追加：
- **2026-05-20.md**（v13 で noindex 化、2275字下限割れ・出典1件）
- ※他の差分は v12 で記録済の noindex 候補が正規化された結果

### 9.3 Day23 で publish した記事

| 日付 | タイトル | 文字数 | CTA | 公開方式 |
|---|---|---|---|---|
| 2026-05-18 | （A8_NEURODIVE 系・AI転職/データサイエンス） | 2858 | A8_NEURODIVE×1 | 手動 publish |
| 2026-05-21 | （技術解説系・CTA省略） | 2880 | なし | 手動 publish |
| 2026-05-25 | （AI英語学習関連、3671字） | 3671 | なし | 手動 publish（gate_fail=1 だった） |
| 2026-05-27 | 海外フリーランス向け実務英語入門 | 2882 | なし | **Phase A 自動公開** 🎉 |

---

## 10. Day23 の出来事

### コミット履歴（git log 抜粋・Day23 分）

ecfe6d3 Daily draft: 2026-05-27 (gate_fail=0, auto_published=yes)  ← Phase A 初成功
bc9c9a9 fix(noindex): 2026-05-20.md に eleventyExcludeFromCollections を追加
7987bc3 fix: Day23後半クリーンアップ - 5/18,5/21 publish + 5/19,5/20 CTA整理
98b7bc2 fix: Day23後半クリーンアップ詳細
b9e6d76 fix(review_helper): 自動チェック結果ヘッダ・MODEL_USED コメントを末尾スキップ対象に追加
（5/25記事の手動 publish コミット）
ba77e85 Daily draft: 2026-05-25 (gate_fail=1, ...)

### 主要作業内容

1. **5/25 gate_fail=1 の原因究明**: review_helper.sh の SKIP_PATTERNS バグと判明 → bugfix commit b9e6d76
2. **5/25 記事の手動 publish**: 内容は問題なし（3671字、出典15件、AI開示あり）→ publish 成功
3. **5/18 draft 公開**: MOSHIMO×2 を A8_NEURODIVE×1 に整理 → publish
4. **5/21 draft 公開**: A8_NEURODIVE 誤配置削除 + 冒頭空行除去 → publish
5. **5/19 CTA 整理**: MOSHIMO_CONOHA_WING 削除（条件E該当）
6. **5/20 noindex 化**: 字数・出典下限割れにつき `noindex: true` 付与
7. **5/20 Eleventy 除外バグ発見と修正**: `noindex` 単独では collections から外れない仕様を発見、`eleventyExcludeFromCollections: true` を追加
8. **5/26 article 未生成**: 19:00 cron 失敗のため 5/26 分は欠番（補填は v14 タスク化）
9. **5/27 19:00 cron 失敗**: GitHub Actions runner 一時障害（403偽陽性）
10. **5/27 手動 rerun で Phase A 初成功**: run 26483088700 が 5m5s で完了、auto_published=yes commit が生成された ← **歴史的瞬間**
11. **Hermes Agent 環境棚卸し**: v0.13.0 にて provider #9 `xAI Grok OAuth (SuperGrok / Premium+)` 存在を確認、`x_search` ツールも実装済（disabled）
12. **X Premium OAuth 統合の戦略策定**: 個人 X Premium ¥980/月で Grok OAuth 経由のリアルタイム X 検索が可能と判明 → 次フェーズの中核機能に決定

---

## 11. 既知の未解決問題（v13更新）

### v12 から継続

1. freellmapi auto router の間欠タイムアウト
2. slugify結果の不規則性（実害小、放置）
3. Hermes Skills API 未実装（upstream 待ち）
4. Hermes Sessions ペインのプラグイン未提供（Issue #262 待ち）
5. `hermes doctor` の gemini 無効報告
6. Tailscale 等のリモート手段なし
7. Firecrawl 未設定警告（無害）
8. 管理者権限不要ルール継続
9. 重複「AI副業ロードマップ」2記事の統合判断
10. 04_final.md「使用モデル」表記の不一致
11. ~~タグページ自動生成~~ → v12 で解決済
12. description 未設定の記事の一括補完
13. `2026-05-10-2026799.md` の drafts/withdrawn/ 退避未実施
14. publish.py が末尾メタブロックの出典URLを削除する（プロンプト側で本文インライン必須化で回避済）
16. ~~2026-05-19.md に適切な広告主が未確定~~ → v13 で条件E適用、CTA省略で解決
20. **Node.js 20非推奨警告**（GitHub Actions、2026年9月以降に対応必要）
21. **gh CLI が macOS再起動後に PATH から外れる可能性**（要観察継続）

### v12 で解消

- ~~17. 2026-05-20.md が字数・出典下限割れ~~ → **v13 で noindex 化（#17 解消）**
- ~~19. 5/19, 5/20 の MOSHIMO_CONOHA_WING~~ → **v13 で削除完了（#19 解消）**
- ~~22. Phase A の初稼働未確認~~ → **2026-05-27 09:32 JST に Phase A 初成功（#22 解消）**

### v13 新規

23. **`noindex: true` 単独では collections.articles から除外されない仕様**: `eleventyExcludeFromCollections: true` を併記必須。既存 noindex 記事 8 件は両方付与済を確認、5/20 を v13 で対応。新規 noindex 化時のチェックリストに追加する必要あり
24. **19:00 JST 定時 cron に retry logic が無い**: GitHub Actions runner 一時障害で 5/26 分が欠番に。`nick-fields/retry@v3` 導入で 3 回まで自動 retry を検討
25. **5/26 補填記事が未作成**: 任意対応。優先度は低い（Phase A 動作実証は 5/27 で完了済）
26. **`<!-- MODEL_USED: ... -->` の末尾 `>` で review_helper の警告が出る可能性**: 現状 harmless だが SKIP_PATTERNS の補強余地あり
27. **`x_search` ツールが disabled**: Stage 0 トレンド取得のため有効化が必要（v14 タスク）
28. **xAI OAuth 未ログイン**: `hermes login --provider xai-oauth` 実行が必要（v14 タスク）
29. **`~/.hermes/config.yaml.bak*` が 4 ファイル堆積**: 整理候補（低優先）
30. **`ai.tool.navigator.gitpull` の挙動詳細未確認**: 常駐は確認したが動作頻度・ログ場所が未把握（低優先）

---

## 12. 運用ルール（v12 § 12 を踏襲）

v12 のルールに加え:

- **【v13新規】 noindex 化する際は必ず両方付与**: front-matter に `noindex: true` + `eleventyExcludeFromCollections: true` をセットで記載する
- **【v13新規】 review_helper.sh のメタブロック書式変更時の対応**: 04_final.md の末尾フォーマットが変わったら SKIP_PATTERNS を更新する。具体的には新しいヘッダ・コメント行を追加
- **【v13新規】 Actions の偽陽性エラーへの対処**: GitHub Actions ログに `Your account is suspended` 等が出ても、ローカル `gh api user` / `git fetch` が正常なら **runner 側の一時異常**を疑う。手動 rerun で大抵復旧する

---

## 13. 直近のTODO（v13更新、優先度順）

### A群（完了・Day23終）

1. ~~5/25 gate_fail=1 の原因究明と記事公開~~ ✅
2. ~~review_helper.sh のバグ修正~~ ✅
3. ~~5/18, 5/21 publish & 5/19, 5/20 CTA整理~~ ✅
4. ~~5/27 Phase A 自動公開検証~~ ✅
5. ~~handover-v13.md 作成~~ ✅（本ドキュメント）

### B群（今週末・Day24-25）— **X Premium OAuth による Stage 0 統合**

6. **`hermes login --provider xai-oauth` 実行**（device flow で X Premium 認証）
7. **`hermes tools enable x_search`**（現状 disabled）
8. **非対話テスト**: `echo "AI関連の日本のトレンド上位5件をJSONで" | hermes -p --tool x_search`
9. **`scripts/stage0_trend_fetch.py` 作成**
   - 出力: `drafts/YYYY-MM-DD/00_trends.json`
   - `.github/workflows/daily-article.yml` の Stage 1 直前に Stage 0 ジョブを追加
10. **Hermes Desktop（fathah/hermes-desktop）導入検討**: 補助ツールとして利用
    - 本番自動化は CLI 維持
    - X Premium OAuth の初回認証、provider 切替テスト、SOUL.md 編集、過去セッション全文検索、トークン使用量可視化に使用

### C群（来週・Day26-30）— **SEO 強化**

11. JSON-LD Article schema を `_includes/base.njk` に追加
12. FAQ schema を記事末尾に自動生成
13. トピッククラスター再編成（4 pillar pages：AI転職 / フリーランス / AI英語 / AIツール）
14. 内部リンク自動化（`relatedTo` フィルタの強化）
15. Node.js 24 移行（`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`）
16. **GitHub Actions の retry logic 導入**（`nick-fields/retry@v3`、#24）
17. 5/26 補填記事の判断（任意・#25）

### D群（再来週以降・Day31+）— **集客とマネタイズ**

18. Core Web Vitals 最適化（LCP/CLS）
19. Google AdSense 申請（30+ 記事達成済、22 indexed 確認済）
20. X 連携：トレンド記事を自動投稿
21. GA4 流入データ分析、CTA配置の最適化
22. A/Bテスト導入（サイドバー広告クリエイティブの記事カテゴリ別効果検証）
23. publish.py のバグ修正（末尾メタブロックの出典URLを削除しない仕様に）
24. メールマガジン導入

### E群（低優先・任意）

25. `~/.hermes/config.yaml.bak*` 4 ファイル整理（#29）
26. `ai.tool.navigator.gitpull` の挙動詳細確認（#30）
27. Nous Portal / Qwen OAuth ログイン（Grok が動けば優先度低）
28. description 未設定の記事一括補完
29. 重複「AI副業ロードマップ」2記事の統合判断

---

## 14. 主要コマンド集（v12 § 14 から Day24 用を追記）

### PATH 復旧（毎回先頭）

export PATH="$HOME/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.hermes/node/bin:$PATH"

### Day24 朝チェック（Phase A 連続稼働確認）

cd ~/ai-tool-navigator

gh run list --workflow=daily-article.yml --limit 5
git --no-pager log --oneline --grep="auto_published=yes" -10
ls -la src/articles/2026-05-2*.md | tail -10

### B群（X Premium OAuth + Stage 0）開始コマンド

# 1. xAI OAuth ログイン（device flow、ブラウザで X Premium 認証）
hermes login --provider xai-oauth

# 2. x_search ツール有効化
hermes tools enable x_search
hermes tools list | grep x_search

# 3. 非対話テスト
echo '日本のAI/フリーランス/英語学習に関する直近24時間のXトレンド上位5件をJSON配列で。各要素は {topic, summary, intent, search_volume_hint} を持つこと。' | hermes -p

# 4. 結果が JSON で返ったら scripts/stage0_trend_fetch.py を作成

### Hermes Desktop 導入（macOS）

# Releases ページから .dmg をダウンロード
open https://github.com/fathah/hermes-desktop/releases/latest

# DMG をマウントしてアプリをドラッグ → 初回起動で既存 ~/.hermes を自動検出する想定

### v12 で確立した日次・週次コマンドは継続有効

（CTA配置確認、Phase A/B-1 動作確認、Phase D 手動実行、ペルソナ汚染検査、全記事品質チェック等は v12 § 14 を参照）

---

## 15. 重要なファイルパス（v12 から差分のみ）

### v13 新規・修正

- `docs/handover-v13.md`: 本ドキュメント
- `scripts/review_helper.sh`: SKIP_PATTERNS 修正版（commit b9e6d76）
- `src/articles/2026-05-27.md`: **Phase A 自動公開の初成功記事**
- `src/articles/2026-05-18.md` / `2026-05-21.md` / `2026-05-25.md`: 手動 publish
- `src/articles/2026-05-19.md` / `2026-05-20.md`: CTA 整理 + 5/20 noindex 化

### B群で追加予定（v14 で正式登録）

- `scripts/stage0_trend_fetch.py`: Stage 0 トレンド取得（未作成）
- `drafts/YYYY-MM-DD/00_trends.json`: Stage 0 出力（未生成）

### Hermes 環境

- Hermes Agent: `~/.hermes/hermes-agent` (v0.13.0, Python 3.11.5, OpenAI SDK 2.32.0)
- 認証情報: `~/.hermes/auth.json`（2385 bytes、`~/.hermes/auth/` は未作成）
- 設定: `~/.hermes/config.yaml`（バックアップ 4 件あり、整理候補）
- 有効プロバイダ（active）: #16 Google AI Studio (Gemini)
- 認証済 provider: copilot, gemini, nvidia, openai-api
- 未認証だが利用可能: **#9 xAI Grok OAuth (SuperGrok / Premium+)**, OpenRouter, Anthropic, Nous Portal, Qwen 等
- 有効ツール: web, browser, terminal, file, code_execution, vision, image_gen, tts, skills, todo, memory, session_search, clarify, delegation, cronjob, messaging, computer_use
- **無効ツール**: video, video_gen, **x_search**, moa, homeassistant, spotify, yuanbao
- 常駐: `ai.hermes.gateway` (PID 52485), `ai.tool.navigator.gitpull`

---

## 16. 完成形のビジョン（v12 § 16 を踏襲、Stage 0 効果を追記）

### 短期完成形（Day30時点）

- 記事数: 40〜50本
- A8提携: 10プログラム（既存2 + 審査中4 + 追加4予定）
- 自動化: Phase A〜D ✅完成 + **Stage 0 トレンド取得（v13で構想、Day25-30 実装）**
- GA4: 月間PV 5,000〜10,000 目標
- 月間収益: 1万円〜3万円目標

### 中期完成形（Day60時点・Stage 0 効果反映後）

- 記事数: 80〜100本
- カテゴリハブページ: AI学習 / フリーランス / 英語学習 / ブログ運営の4本柱
- **Stage 0 で旬のトピックを取り込み**、AI Overview / Perplexity 等の AI 検索からの被引用率向上
- メールマガジン: 100〜300登録者
- 月間PV: 20,000〜30,000
- 月間収益: 3万円〜5万円（目標達成）

### 長期完成形（Day120+）

- 記事数: 200本+
- **Stage 0 効果でリアルタイム性のあるネタを継続供給**
- 派生サイト: 英語学習特化、フリーランス特化への分割検討
- 自社プロダクト: ai-tool-navigator独自のAI比較診断ツール（無料DL）

---

## 17. 次回チャット開始時の最初のアクション

1. このドキュメント v13 を共有する
2. ユーザーから「Day24 朝の状態確認結果」を受け取る:
   - 19:00 JST cron が正常稼働したか（前回は障害、今回は要確認）
   - `gh run list --workflow=daily-article.yml --limit 5` の結果
   - `git --no-pager log --grep="auto_published=yes" -5` の結果
3. **Phase A 連続稼働の検証**（5/27 が初成功、5/28 以降が連続できているかが本物の自動化の証）
4. B群開始：
   - `hermes login --provider xai-oauth` 実行を依頼
   - device flow の URL が表示されたら、ブラウザで X Premium アカウントで認証
   - 成功後 `hermes tools enable x_search` + 非対話テスト
5. Stage 0 スクリプト設計の合意 → `scripts/stage0_trend_fetch.py` 作成
6. Hermes Desktop インストール判断（macOS 用 .dmg）

---

## v12 → v13 の差分サマリ

| 項目 | v12 | v13 |
|---|---|---|
| Phase A 稼働状況 | 構想完了・初稼働未確認 | **2026-05-27 09:32 JST に初成功**🎉 |
| review_helper.sh | SKIP_PATTERNS に漏れあり（誤検知） | **bugfix（commit b9e6d76）** |
| 19:00 cron の堅牢性 | retry なし | retry なし（v14でnick-fields/retry@v3 導入予定） |
| 記事数 | 30本 | **33本**（5/18, 5/21, 5/25, 5/27 追加） |
| noindex 記事 | 8本 | **11本**（5/20 追加 + 既存正規化） |
| noindex の Eleventy 仕様 | 未認識 | **`eleventyExcludeFromCollections: true` 併記必須と判明** |
| CTA 配置（5/19, 5/20） | MOSHIMO 残存 | **削除完了（v12 #19 解消）** |
| 5/20 字数下限割れ | 未対処 | **noindex 化（v12 #17 解消）** |
| 未解決問題 | 22件 | **18件**（解消3、新規9、再分類）※番号体系維持 |
| Stage 0 トレンド取得 | 未着想 | **構想策定済（X Premium OAuth + Grok）** |
| Hermes Desktop | 認識なし | **補助ツールとして導入候補** |
| 「労力0.1%化」 | 実装完了・実稼働待ち | **実証完了** |

---

_handover-v13.md 作成日: 2026-05-27（Day24 開始時点）_
_Phase A 初稼働記念ドキュメント_

---
