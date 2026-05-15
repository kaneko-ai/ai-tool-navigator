
---

# ai-tool-navigator プロジェクト引き継ぎドキュメント v9

**最終更新**: 2026-05-15（Day19 朝の作業完了時点）
**前回（v7, 2026-05-12）からの主要更新**:
- Day18朝: タグページ自動生成（8タグ）、SEO最適化（OGP/Twitter Card/JSON-LD/sitemap/robots）、関連記事自動生成、Stage4プロンプト強化、front-matter漏れ検知quality gate、review_helper.sh導入
- Day18夜: 5/13-2 prelude leak draftを `drafts/withdrawn/` へ退避
- Day19朝: Run #8失敗の真因特定（`build_topic_context.sh` の引数順バグ）、Python版書き換え、5/14ドラフトを withdrawn/ へ退避、review_helper.sh をworkflow統合
- v7時点の17件の未解決問題のうち約半数が解決、新規4件発覚（モデル変動、bash 3.2 vs 5系、heredocネスト、zsh # コメント）

> **本v9はv7をベースに、Day18-19の進捗を反映した版。v8はチャット運用のままドキュメント化されなかったため欠番。**

---

## 1. プロジェクト概要（v7から変更なし）

- **サイト名**: ai-tool-navigator
- **目的**: AI関連ツールの比較・解説サイトで月5万円のアフィリエイト収益を目指す
- **運営方針**: kanekichi匿名運用継続、誇大表現NG、データ・実例ベース記事、AI生成は必ず人手校閲を経て公開
- **GitHubリポジトリ**: kaneko-ai/ai-tool-navigator
- **公開URL**: https://kaneko-ai.github.io/ai-tool-navigator/
- **公開**: GitHub Pages（11ty/Eleventy v3.1.5）
- **GA4**: 設置済み（測定ID: G-8J2LVW54HE）

---

## 2. 技術スタック（v7から更新）

### 記事生成系（v7から継続）

- **記事生成スクリプト（旧主力、現在は補助）**: `daily_article_generator.py`
- **環境変数**: `~/ai-blog-config/.env`
- **記事保存先**: `src/articles/`
- **ドラフト退避**: `drafts/withdrawn/`
- **launchd**: `ai.tool.navigator.daily`（現在は実質停止、GitHub Actionsに一本化）

### GitHub Actions 4段パイプライン（v7から仕様強化）

- **ファイル**: `.github/workflows/daily-article.yml`（v9時点で282行）
- **実行**: 毎日19:00 JST（cron `0 10 * * *` UTC）+ 手動 workflow_dispatch
- **CLI**: GitHub Copilot CLI（全段 `--model auto`、日次でgpt-5-mini ↔ claude-haiku-4.5 等が変動）
- **段階構成**:
  - Build recent topics context (行50-): `scripts/build_topic_context.py` を呼び `/tmp/recent_topics.txt` 生成（**Day19でPython版に書き換え**）
  - Stage1 Topic expansion (行60-): `01_topic_select.md` + `recent_topics.txt` → `01_topic.md`
  - Stage2 Draft (行97-): `02_draft.md` 生成
  - Stage3 Factcheck (行129-): `03_factcheck.md` 生成
  - Stage4 Polish (行162-): `04_final.md` 生成（**Day18でプロンプト強化、front-matter冒頭厳守ルール追加**）
  - Quality gate (行200-): 文字数2500-3500、front-matter先頭検査（Day18追加）、末尾句点、`ai_assisted/editor_reviewed` 必須キー検査
  - **Review helper (行215-, Day19追加)**: `scripts/review_helper.sh` で5項目チェック（誇大表現/偽ペルソナ/末尾切れ/URL数/AI開示）、exit 2でgate_fail=1

### Day18-19で追加・修正したファイル（v9で新規記載）

| ファイル | 役割 | 追加日 |
|---|---|---|
| `src/tags/tag.njk` | タグページのテンプレート（pagination で8タグ自動生成） | Day18 |
| `src/tags/index.njk` | タグ一覧ページ `/tags/` | Day18 |
| `src/sitemap.njk` | sitemap.xml 自動生成 | Day18 |
| `src/robots.njk` | robots.txt 自動生成 | Day18 |
| `_includes/partials/related-articles.njk` | 関連記事カード（タグ重複×10 + 新しさボーナス、最大4枚） | Day18 |
| `eleventy.config.js` | `relatedTo` カスタムフィルタ追加（共通タグスコアリング） | Day18 |
| `_includes/base.njk` | OGP/Twitter Card/canonical/noindex メタ追加 | Day18 |
| `_includes/post.njk` | JSON-LD BlogPosting 構造化データ追加、関連記事 include | Day18 |
| `prompts/04_polish.md` | 「先頭は必ず `---`、MODEL_USEDは末尾1行」META追加 | Day18 |
| `scripts/review_helper.sh` | grep ベースの機械校閲（追加コストなし） | Day18 |
| `scripts/build_topic_context.py` | 旧bash版を置き換え（bash 3.2/5系の挙動差を回避） | Day19 |
| `scripts/build_topic_context.sh` | Python版へのラッパー、引数順バグ修正 | Day19 |
| `drafts/withdrawn/2026-05-13-2-prelude-leak/` | Stage4独白漏れドラフト退避 | Day18 |
| `drafts/withdrawn/2026-05-14-stage1-input-missing/` | Stage1全失敗ドラフト退避 | Day19 |

### Hermes Agent v0.13.0（v7から変更なし、参考）

- 本体: `~/.hermes/`、Workspace UI: `http://localhost:3000`、Gateway: `http://127.0.0.1:8642`
- 既知制限: Skills API 404、Sessions ペイン未提供、Firecrawl 未設定警告（無害）、GEPA保留
- **Day20+ にトリアージ予定（それまで触らない）**

---

## 3. プロバイダ・フォールバック構成（v7から変更なし）

- Copilot CLIが `--model auto` で日次変動（gpt-5-mini, gpt-5.3-codex, gpt-5.4-mini, claude-haiku-4.5, claude-sonnet-4-6 等）
- フォールバック: gemini_direct → freellmapi（旧 daily_article_generator.py 系列、現在は補助）
- **Day19新規発覚**: モデル変動でプロンプト解釈が変わる（gpt-5-mini は寛容、claude-haiku-4.5 は厳密で「必須入力不足」と拒否する）→ §10 #19 参照

---

## 4. TOPICS配列（v7から変更なし）

- 30件、3軸構成（AI学習・スクール系 / AIツール・LLM系 / キャリア・転職系）
- インデックス0-29で管理、`prompts/01_topic_select.md` 内に定義

---

## 5. アフィリエイト戦略（v7から変更なし）

### 5.1 方針継続

- 月5万円目標、A8申請済10件、ConoHa WING（もしも経由）が現状の主軸
- CTAプレースホルダ `<!-- CTA:MOSHIMO_CONOHA_WING -->` を1-2箇所配置

### 5.2 規約根拠
- もしもアフィリエイト規約遵守、誇大表現NG、AI生成記事の開示必須

### 5.3 A8申請済10件（進捗未確認、Day20+ で再確認）

---

## 6. 品質ガードレール（v7から大幅強化）

### 6.1 SKILL.md v2.0.0（v7から変更なし）

### 6.2 NGパターン蓄積ログ（v7から変更なし）
- `~/ai-blog-config/ng_patterns.log` に集約

### 6.3 校閲ワークフロー4段（v7から継続 + Day18-19強化）
- Stage1 トピック展開（with 直近30日記事リスト注入）
- Stage2 ドラフト生成
- Stage3 ファクトチェック
- Stage4 校閲（**Day18でプロンプト強化**: 先頭`---`厳守、MODEL_USED末尾1行）

### 6.4 quality gate（Day18追加、Day19拡張）

- 文字数 2500-3500
- front-matter 先頭検査（Day18追加、最初の非空行が `---` か）
- 末尾句点（。, ！, ？, ）, 」, * のいずれか）
- 必須キー: layout/title/date/description/tags/ai_assisted/editor_reviewed
- **review_helper.sh 連携（Day19追加）**: 5項目検査でexit 2なら gate_fail=1

### 6.5 サイト表面の品質基準（v7から継続 + Day18追加）

- 明色テーマ、カードUI、タグページ自動生成（Day18追加）
- 関連記事4枚自動表示（Day18追加）
- OGP/Twitter Card/JSON-LD/sitemap.xml/robots.txt（Day18追加）

---

## 7. cron / 自動実行スケジュール（v7から微更新）

- GitHub Actions: 毎日19:00 JST（cron `0 10 * * *` UTC）
- launchd `ai.tool.navigator.daily`: 実質停止（**Day18でドキュメント化、二重生成回避**）

---

## 8. 既存記事の状態（Day19時点）

### 8.1 公開中（collections.articles に含まれる）

Day19朝時点で **18記事**（v7時点19→ 2026-05-12-ai5.md を 503エラー記事として退避）。

### 8.2 noindex（直リンクのみ、一覧除外）

- 6記事（2026-04-23 の煽り口調記事群）、`eleventyExcludeFromCollections: true` 付与済み

### 8.3 撤回済（v7から拡張）

- `drafts/withdrawn/articles/2026-05-12-ai5-503-error.md`（Day18追加）
- `drafts/withdrawn/2026-05-13-2-prelude-leak/`（Day18追加、Stage4独白漏れ）
- `drafts/withdrawn/2026-05-14-stage1-input-missing/`（Day19追加、Stage1全失敗）

### 8.4 既知の重複タイトル

- LLMファインチューニング入門（4/28版 + 5/8版）→ **未統合**、Day20+
- AI副業ロードマップ（4/23版 + 5/2版）→ **未統合**、Day20+

### 8.5 タグ集計（Day18時点、normalize_tags.py 後）

- tutorial(8) / comparison(8) / career(7) / llm(6) / ai-tools(6) / news(4) / agent(4) / side-business(3)

---

## 9. Day12〜19 の出来事

### Day12〜17（v7で記録済）

### Day18 朝（v9で追記）

- **退避**: drafts/2026-05-13-2 → withdrawn/2026-05-13-2-prelude-leak/
- **タグページ自動化**: `src/tags/tag.njk` + `src/tags/index.njk`、`relatedTo` フィルタ追加（実は Day18 後半）、8タグ全自動生成
- **SEO最適化**: OGP/Twitter Card/canonical/noindex メタ、JSON-LD BlogPosting、sitemap.xml（29 URL）、robots.txt
- **関連記事**: `_includes/partials/related-articles.njk`、タグ共通数×10 + 新しさボーナスでスコア計算、最大4枚
- **Stage4強化**: `prompts/04_polish.md` に「先頭は`---`、MODEL_USEDは末尾1行」META追加
- **quality gate拡張**: front-matter先頭検査追加
- **review_helper.sh**: grepベースの機械校閲導入（追加コスト0）
- **AI開示判定修正**: front-matterの `ai_assisted: true` 検出で OK（post.njk が自動出力するため）

### Day18 夜

- Run #8 待機、commit `7288ee4`, `d8e6d35`, `88a73ac`, `2d2dfa2`, `c93f0f4`, `d549de8` を push

### Day19 朝（v9で追記）

- **Run #8 結果**: gate_fail=1（**quality gate が正しく動作**してpublishを阻止）
- **真因特定**:
  - 表面: Stage1 が「必須入力不足」と拒否 → カスケード失敗 → Stage4で前日のドラフトをテンプレに即興生成 → 冒頭3行が英語独白に漏れ → front-matter先頭検査でブロック
  - **根本: `scripts/build_topic_context.sh` の引数順バグ**。ラッパーが `output_file → articles_dir → days` の順で受け取るのに、ワークフローからは `output_file → days` の2引数で呼ばれていた。結果 `articles_dir=30` と解釈され存在しないディレクトリを見ていた → 直近記事リストが常に空
  - 5/13までは gpt-5-mini がリスト空でも自走してくれていたため隠れたまま、5/14に claude-haiku-4.5 が割り当てられ表面化
- **修正**:
  - `scripts/build_topic_context.py` を新規追加（Python版、bash 3.2/5系の挙動差も回避）
  - `scripts/build_topic_context.sh` をPython版へのラッパーに簡素化、引数順を `output_file → days → articles_dir` に修正（ワークフローからの呼び出しと整合）
  - プロンプトに「フォールバック指示」を追加: リスト空でも軸0-29から自律的に1件選び停止しないこと
- **5/14ドラフト退避**: `drafts/withdrawn/2026-05-14-stage1-input-missing/`
- **review_helper.sh のworkflow統合**: stash pop → コミット&push（commit `1e56a6d`）
- **コミット履歴**: `8290939`(build_topic_context修正), `1e56a6d`(review_helper統合)

---


## 10. 既知の未解決問題（v7から大幅更新）

### 10.1 v7時点の17件のステータス（Day19朝時点）

| # | 問題 | v7 | v9ステータス |
|---|---|---|---|
| 1 | freellmapi auto router 間欠タイムアウト | Day30+ | 継続（補助系のため優先度低） |
| 2 | CTA一括置換スクリプト未作成 | Day20+ | 継続 |
| 3 | slugify結果の不規則性 | 放置 | 放置 |
| 4 | 既存記事のmoshimo CTA | 校閲後置換 | 継続 |
| 5 | Hermes Skills API 未実装 | upstream待ち | 継続 |
| 6 | Hermes Sessions ペイン未提供 | Issue #262待ち | 継続 |
| 7 | `hermes doctor` gemini無効 | Day30+ | 継続 |
| 8 | Tailscale等のリモート手段なし | - | 継続 |
| 9 | Firecrawl未設定警告 | 無害 | 継続 |
| 10 | 管理者権限不可 | - | 継続 |
| 11 | 既存重複タイトル2件 | Day19+ | **未解決、Day20+** |
| 12 | noindex 6記事の本文品質 | Day20+ | 継続 |
| 13 | Run #7 が3,740字で上限超過 | 要対処 | **✅ 解決**（Stage4プロンプト強化＋quality gate） |
| 14 | 04_final.md「使用モデル」表記が3回失敗 | 未対応 | **✅ 解決**（末尾1行のMODEL_USEDで統一） |
| 15 | タグページ自動生成未実装 | Day18+ | **✅ 解決**（Day18） |
| 16 | description未設定の記事 | Day18+ | **部分解決**（5記事のみ要補完、noindex記事中心） |
| 17 | 2026-05-10-2026799.md 公開中だが校閲不可 | 退避未実施 | **未解決**、Day20+ |
| 18 | 2026-04-23-ai.md ほぼ空 | 退避候補 | **未解決**（noindex扱いで一覧除外済み、暫定対応） |

### 10.2 v9で新規追加の問題

19. **【v9新規】 Copilot CLI `--model auto` の日次変動が品質に影響**
    - 5/13は gpt-5-mini（寛容、リスト空でも自走）、5/14は claude-haiku-4.5（厳密、必須入力不足で停止）
    - 対策案: `--model gpt-5-mini` 明示固定 or プロンプトのフォールバック指示で吸収（Day19はフォールバック指示で対応）
    - Day20+で要検討: モデル明示固定にするか、現状の自動振り分けに任せるか

20. **【v9新規】 bash 3.2 (macOS) vs bash 5+ (GitHub Actions) の挙動差**
    - `[[ str1 > str2 ]]` の文字列比較がbash 3.2で予期しない結果になることがある
    - サブシェル内の変数更新（`{ ... } > FILE` ブロック内のカウンタ等）が外に伝播しないことがある
    - **対策**: シェルスクリプトはPython製ラッパーに段階的に移行（Day19実施: build_topic_context）

21. **【v9新規】 heredoc多重ネストの誤動作**
    - `cat > file <<'OUTER'` 内に `cat > file2 <<'INNER'` を書くと、シェルがOUTERマーカーまでで切ってしまうことがある
    - **対策**: ネストを避け、Pythonスクリプトを別ファイルとして作成してから呼ぶ

22. **【v9新規】 zsh の `#` コメントが効かない**
    - macOSデフォルトのzshは `setopt interactive_comments` しないと `#` コメント行が「command not found: #」エラー
    - **対策**: コマンドブロックの先頭に `setopt interactive_comments` を入れる

23. **【v9新規】 publish自動化未実装**
    - 現状: gate_fail=0 でもドラフトのまま、手動で `src/articles/` にコピーが必要
    - Day20で設計検討予定

24. **【v9新規】 PageSpeed最適化未着手**
    - 画像 lazy loading 等の軽量改善、Day19午後に着手予定

---

## 11. 運用ルール（v7から追記）

### v7から継続
- 4キャラ会議は明示要請時のみ
- Hermes修正は Day30+
- sudo 不使用、PATH復旧は新ターミナル先頭で実行
- 記事品質ルール、校閲フロー必須
- `_site/` は git 管理外、noindex 記事は2フラグ両方、front-matter 終端改行、commit分割

### v9で追加

- **【v9新規】 シェルスクリプト引数順序の標準**:
  - 出力先 → 主要オプション → 副次オプションの順
  - 例: `build_topic_context.sh <output_file> [days] [articles_dir]`
  - ワークフロー側の呼び出しと必ず整合させる（Day19の引数順バグの教訓）
- **【v9新規】 シェルスクリプトは Python ラッパー方式に統一**:
  - 複雑な処理（日付計算、文字列比較、ファイルglob）は Python で書く
  - シェル側は引数受け取りとPython呼び出しのみに簡素化
  - bash 3.2/5系の挙動差を完全排除
- **【v9新規】 `--no-pager` 推奨**:
  - `git --no-pager log/diff/stash show` を使う（less に入って詰まる事故防止）
- **【v9新規】 退避ディレクトリ命名規則**:
  - `drafts/withdrawn/<日付>-<失敗理由>/`
  - 例: `2026-05-13-2-prelude-leak`, `2026-05-14-stage1-input-missing`
- **【v9新規】 quality gate に Run結果検証を委ねる**:
  - 機械的に検出可能な問題（front-matter漏れ、文字数、URL数、誇大表現）は workflow 側で gate_fail にする
  - 人手校閲は内容の妥当性・読みやすさ・最新性に集中
- **【v9新規】 ローカル検証用 zsh 設定**:
  - `~/.zshrc` に `setopt interactive_comments` を追加することを検討（今回は都度実行）

---

## 12. 直近のTODO（v9更新、優先度順）

### Day19 残作業（本日）

- ✅ Run #8 結果確認＆失敗原因特定
- ✅ build_topic_context Python版書き換え
- ✅ 5/14ドラフト退避
- ✅ review_helper.sh をworkflow統合
- ✅ ハンドオーバー資料 v9 作成（**本作業**）
- 🔜 **publish自動化の設計検討**（Day20以降の作業計画）
- 🔜 **PageSpeed軽量改善**（画像 lazy loading 等）
- 🔜 **Run #9 結果待機**（19:00 JST、直近30日リスト24件付きで成功するか検証）

### Day20 朝チェック

- Run #9 の結果確認: 5/15記事が gate_fail=0 で生成されたか、front-matter漏れなし、review_helper通過、文字数範囲内
- 失敗していた場合: Stage1 の出力（01_topic.md）にトピックがちゃんと選定されたか確認

### Day20 着手タスク

1. publish自動化（level-up #1）: `04_final.md` の front-matter から date を読み、`src/articles/<date>-<slug>.md` に自動配置
2. 既存重複タイトル2件の統合判断
3. description 未設定5記事の補完判断（noindex扱いなら放置でも可）
4. PageSpeed 改善の継続

### Day21-30

- A8申請進捗確認、CTA一括置換、校閲済10本到達後の収益測定基盤

### Day30+

- Hermes Skills API トリアージ、freellmapi タイムアウト根本対応、GEPA 検討

---

## 13. 主要コマンド集（v7から拡張）

### PATH 復旧（毎ターミナル先頭）

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:

HOME/.hermes/node/bin:PATH" setopt interactive_comments # zsh で # コメントを有効化

### 【v9新規】 毎朝のRun結果確認ワンライナー

cd ~/ai-tool-navigator && git pull origin main && echo "=== 最新5コミット =" && git --no-pager log --oneline -5 && echo "= 本日のドラフト =" && ls -la drafts/$(date +%Y-%m-%d)*/ 2>/dev/null && echo "= 04_final.md チェック =" && for f in drafts/$(date +%Y-%m-%d)*/04_final.md; do echo "--- $f ---" wc -m "$f" echo "[先頭3行]"; head -3 "$f" echo "[末尾3行]"; tail -3 "$f" done && echo "= src/articles に公開されたか ===" && ls src/articles/$(date +%Y-%m-%d)*.md 2>/dev/null || echo "未公開（gate_fail or 手動公開待ち）"

### 【v9新規】 review_helper.sh のローカル実行

bash scripts/review_helper.sh src/articles/<記事ファイル>.md
exit 0: 完全クリーン
exit 1: warning あり（gate_failにはしない）
exit 2: error あり（gate_fail=1）

### 【v9新規】 build_topic_context.py の動作確認

./scripts/build_topic_context.sh /tmp/test.txt 30 grep -c '^- 2026-' /tmp/test.txt # 直近30日の記事数（v9時点で24件想定）

### 日次状態確認（v7から継続）
- 後述のサイト整合性チェック、重複防止コンテキスト確認、タグ正規化 等は v7 §13 と同じ

### 記事撤回フロー

mkdir -p drafts/withdrawn mv src/articles/<退避対象>.md drafts/withdrawn/articles/<日付>-<理由>.md
または
mv drafts/<退避対象ディレクトリ> drafts/withdrawn/<日付>-<失敗理由>/ git add -A && git commit -m "withdraw: <理由>" && git push origin main

---

## 14. 重要なファイルパス（v9更新）

### リポジトリ直下

- `daily_article_generator.py`（旧主力、現在は補助）
- `eleventy.config.js`（11ty設定、Day18で `relatedTo` フィルタ追加）

### .github/workflows/

- `daily-article.yml`（282行、Day18-19で gate拡張＋review_helper統合）

### prompts/

- `01_topic_select.md`（トピック選定）
- `02_draft.md`（ドラフト生成）
- `03_factcheck.md`（ファクトチェック）
- `04_polish.md`（**Day18で先頭`---`厳守META追加**）

### scripts/

- `build_topic_context.py`（**Day19新規、Python版**）
- `build_topic_context.sh`（**Day19書き換え、Pythonラッパー**）
- `review_helper.sh`（**Day18新規、grep校閲**）
- `normalize_tags.py`（Day17、タグ正規化）

### src/

- `articles/`（公開記事18本）
- `articles/articles.json`（templateEngineOverride: njk,md、Day18追加）
- `tags/tag.njk`（**Day18新規**、ページネーション）
- `tags/index.njk`（**Day18新規**、タグ一覧）
- `sitemap.njk`（**Day18新規**）
- `robots.njk`（**Day18新規**）
- `assets/css/style.css`（明色テーマ、Day18でタグ・関連記事用CSS追加）

### _includes/

- `base.njk`（**Day18でOGP/Twitter/canonical/noindex メタ追加**）
- `post.njk`（**Day18でJSON-LD BlogPosting・関連記事include追加**）
- `partials/related-articles.njk`（**Day18新規**）

### drafts/

- `withdrawn/articles/`（個別退避記事）
- `withdrawn/2026-05-13-2-prelude-leak/`（**Day18**）
- `withdrawn/2026-05-14-stage1-input-missing/`（**Day19**）

### Hermes Agent（v7から変更なし）

- `~/.hermes/` 配下、Workspace UI、Gateway、Skills等

---

## 15. 次回チャット開始時の最初のアクション

1. **このv9ドキュメントを共有**
2. **「Day20朝の状態確認結果」を実行・貼り付け**:
cd ~/ai-tool-navigator setopt interactive_comments git pull origin main git --no-pager log --oneline -5 ls -la drafts/2026-05-15*/ # 本日分（または該当日） for f in drafts/2026-05-15*/04_final.md; do wc -m "

f";head−3"f"; tail -3 "$f" done ls src/articles/2026-05-15*.md 2>/dev/null

3. **Run #9 が成功していれば**: publish自動化の設計検討、PageSpeed改善、既存重複記事の統合判断
4. **Run #9 が失敗していれば**: 原因切り分け（モデル変動か、別の隠れバグか）

---

## 16. 【v9新規】 落とし穴サマリ（今後の事故防止メモ）

1. **シェルスクリプトの引数順は呼び出し元と整合させる**
- 5/14 Run #8 失敗の真因。`build_topic_context.sh` で `output → articles_dir → days` のつもりが、ワークフローでは `output → days` で呼ばれていた

2. **bash 3.2 (macOS) と 5+ (Linux) は別物と思え**
- 文字列比較、サブシェル変数伝播、heredoc挙動が微妙に違う
- 複雑な処理は Python に逃がす

3. **heredoc を多重にネストしない**
- 外側マーカーで早期終了する事故が起きる
- Python等は別ファイルに書き出してから呼ぶ

4. **zsh の `#` コメントは `setopt interactive_comments` が必要**
- macOSデフォルトzshだと `command not found: #` で全停止

5. **Copilot CLI `--model auto` は日次変動**
- モデルによってプロンプト解釈の厳密さが変わる
- 「リストが空でも自走せよ」のようなフォールバック指示を必ず入れる

6. **`git stash show -p` などは pager に入る**
- `git --no-pager` を付けるか、`q` で抜けることを覚えておく

7. **scripts のbackupファイルは .gitignore で除外**
- `*.bak.*` パターンを .gitignore に追加済み（Day18）

---

## v7 → v9 の差分サマリ

- **主力パイプライン**: v7時点でGitHub Actions 4段化完了 → v9で **review_helper.sh統合**で5段相当に
- **サイト表面**: 明色テーマ + カードUI → **タグページ自動化、SEO（OGP/JSON-LD/sitemap）、関連記事自動表示**
- **quality gate**: 文字数チェックのみ → **front-matter先頭検査、末尾句点、必須キー、review_helper 5項目** の多層化
- **ドラフト品質**: Stage4 プロンプト強化、独白漏れ完全防止
- **トピック重複防止**: bash 3.2脆弱なスクリプト → **Python版で堅牢化**、引数順バグ修正、フォールバック指示追加
- **退避運用**: 個別ファイル退避 → **失敗理由を含むディレクトリ命名規則化**（prelude-leak, stage1-input-missing 等）
- **未解決問題**: v7で17件 → v9でうち6件解決、新規6件追加で17件継続

---
