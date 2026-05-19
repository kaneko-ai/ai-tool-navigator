# ai-tool-navigator プロジェクト引き継ぎドキュメント v10

**最終更新**: 2026-05-19（Day19 夕方）
**前回（v9）からの主要更新**:
- Day18: タグページ自動生成、SEO最適化（OGP/Twitter Card/JSON-LD/sitemap/robots）、関連記事カード自動生成、review_helper.sh の AI開示判定を front-matter優先に修正、Stage4プロンプト強化＋front-matter漏れgate、5/13-2ドラフトの退避
- Day19朝: build_topic_context.sh の引数順バグ修正（Python版へ書き換え、24件マッチ確認）、review_helper.sh を quality gate として workflow に統合、2026-05-14 ドラフトを withdrawn 退避
- Day19夕: handover-v9 作成、publish-design.md 作成、publish.py 実装（ローカル動作確認済）、review_helper.sh の HTML コメント除外修正、Stage4プロンプト5項目絶対ルール化、Run #12（5/18）の効果検証
- GitHub CLI 導入は Homebrew 所有権問題で一旦見送り（C案、ブラウザでログ確認継続）

---

## 1. プロジェクト概要（当初の目的を再確認）

> **当初の目的（不変）**: AI関連ツールの比較・解説サイトで月5万円のアフィリエイト収益を目指す。kanekichi匿名運用、誇大表現NG、データ・実例ベース記事、AI生成は必ず人手校閲を経て公開。技術的な実装は手段であり、目的ではない。

- **サイト名**: ai-tool-navigator
- **GitHubリポジトリ**: kaneko-ai/ai-tool-navigator
- **公開URL**: https://kaneko-ai.github.io/ai-tool-navigator/
- **公開**: GitHub Pages（11ty/Eleventy v3.1.5）
- **GA4**: 設置済み（測定ID: G-8J2LVW54HE）

### 重要な視点（v10で再強調）

直近のDay18〜19は「記事生成パイプラインの自動化と品質安定化」に大きく投資した。しかし当初の目的は **アフィリエイト収益化** であり、技術整備はそのための手段である。Day20以降は技術整備の優先度を下げ、A8提携審査の進捗確認・既存記事の品質改善・CTA配置の最適化など、**収益化に直結する作業**へリソースを振り向ける必要がある。

---

## 2. 技術スタック

### 主力パイプライン: GitHub Actions 4段ワークフロー

- **ファイル**: `.github/workflows/daily-article.yml`
- **実行**: 毎日10:00 UTC（=19:00 JST）+ 手動 workflow_dispatch
- **CLI**: GitHub Copilot CLI（`copilot` コマンド、`--model auto` で動的選択）
- **段階構成**:
  - Stage1: トピック選定（`prompts/01_topic_select.md` + 直近30日記事リスト注入）→ `drafts/$DRAFT_DATE/01_topic.md`
  - Stage2: ドラフト生成 → `02_draft.md`
  - Stage3: ファクトチェック → `03_factcheck.md`
  - Stage4: 校閲・最終版（`prompts/04_polish.md`、quality gate あり）→ `04_final.md`
- **quality gate**: gate_fail=1 で publish 停止、コミットメッセージに記録

### 旧主力: launchd + Hermes Agent（並行稼働、Day30+ で再評価）

- `daily_article_generator.py`（585行、launchd で19:00 JST）
- Hermes Agent v0.13.0、Workspace UI（localhost:3000）、Gateway（127.0.0.1:8642）
- 詳細は v7 §2 参照

### Day18〜19 で追加・修正したファイル一覧

| ファイル | 役割 | 追加/修正日 |
|---|---|---|
| `scripts/build_topic_context.py` | 直近N日の記事タイトル・タグを集計（Python版、bash版を置き換え） | Day19朝 |
| `scripts/build_topic_context.sh` | Python版を呼ぶラッパー（引数順バグ修正済） | Day19朝 |
| `scripts/publish.py` | drafts/<date>/04_final.md を src/articles/<date>.md へ変換 | Day19夕 |
| `scripts/review_helper.sh` | quality gate 用品質チェック（HTML コメント除外対応） | Day18→Day19夕 |
| `scripts/normalize_tags.py` | タグ正規化（v7から継続、実行権限が外れているので注意） | Day17 |
| `prompts/04_polish.md` | Stage4プロンプト5項目絶対ルール化 | Day19夕 |
| `prompts/04_polish.md.bak.20260518` | 同上のバックアップ | Day19夕 |
| `docs/handover-v9.md` | 旧引き継ぎ資料（参照用に保持） | Day19朝 |
| `docs/publish-design.md` | publish 自動化の設計書 | Day19朝 |
| `.github/workflows/daily-article.yml` | review_helper.sh 統合済 | Day19朝 |

---

## 3. プロバイダ・フォールバック構成（v7から変更なし）

3段フォールバック（freellmapi → gemini_direct → nvidia_nim）。詳細は v7 §3 参照。

---

## 4. TOPICS配列（v7から変更なし）

軸1（AI学習・スクール10件）、軸2（フリーランス・転職10件）、軸3（AI英語学習10件）。GitHub Actions 側は Stage1 プロンプトで直近30日リストを注入し重複回避。

---

## 5. アフィリエイト戦略（v7から継続、Day20以降の最重要トピック）

### 現状

- A8提携審査の進捗確認は **棚上げ継続**
- 校閲済みで公開できる記事は現状 1記事のみ（`2026-05-13-miraif-career-guide.md`、editor_reviewed:true）
- 自動生成記事は 24記事だが全て editor_reviewed:false
- **当初の目的に照らすと、ここが最大のボトルネック**

### Day20以降の戦略再構築（v10新規記載）

技術整備が一段落した今、**アフィリエイト収益化に直結する作業**へ優先度を戻す:

1. publish.py を本番投入し、quality gate 通過記事を機械的に publish
2. 公開記事10本到達後、A8提携審査の進捗を一括確認
3. 既存24記事のうち品質基準を満たすものを `editor_reviewed:true` 化する基準を策定
4. moshimo CTA → A8確定リンクへの一括置換スクリプト作成

### 規約根拠（v7から再掲）

- Amazon アソシエイト 2025改定: AI生成コンテンツへの明示ラベル必須
- A8.net: SNS/コンテンツ運用の明示要件、未承認サイトでの掲載禁止
- 楽天アフィリエイト 2026改定: AI条項追加

### A8申請済10件（進捗未確認）

AI学習系4件: メイカラ、AIビジネス活用講座、Neuro Dive、Python Winner
フリーランス系3件: フリーランスボード、TechClips ME、ミライフ
英語系3件: TEPPEN ENGLISH、スマイルゼミENGLISH、スピーク

---

## 6. 品質ガードレール（v9から大幅強化）

### 6.1 Stage4プロンプト5項目絶対ルール（Day19夕、最新）

`prompts/04_polish.md` 冒頭の META INSTRUCTION で以下5項目を絶対ルール化:

1. **構造ルール**: 1行目=`---`、`---`の出現は3回のみ（FM開始/FM終了/末尾メタ前）、MODEL_USED は最終行に1行のみ
2. **コードフェンス全面禁止**: バッククォート3つを出力中のどこにも含めない
3. **独白・自己進捗報告の禁止**: 「確認します」「作成します」等の作業説明文を一切含めない
4. **文字数厳守**: 2500-3500字、超過は quality gate で reject
5. **違反時の挙動明示**: gate_fail=1 で publish されないことを明示

### 6.2 review_helper.sh による quality gate

`scripts/review_helper.sh` を `.github/workflows/daily-article.yml` に統合（Day19朝）。5項目の品質チェック:

1. 誇大表現（最速・業界No.1等）
2. 一人称ペルソナ・架空ブランド
3. 本文末尾の途中切れ（HTML コメント・CTA・水平線は除外）
4. 出典URL数（3件以上必須）
5. AI開示（front-matter `ai_assisted: true` 優先）

Day19夕に SKIP_PATTERNS に `<!--` を追加し、`<!-- MODEL_USED: ... -->` を末尾切れ判定から除外する修正を実施。

### 6.3 publish.py による front-matter 変換ルール（Day19夕、新規）

`scripts/publish.py` 設計（A案: slug 未対応版）:

1. 冒頭の空行・独白を除去（最初の `---` までスキップ）→ Stage4 の冒頭空行を吸収
2. `editor_reviewed: false` → `true` に書き換え
3. 末尾の自動チェック結果ブロック（最終 `---` 以降のメタ情報）を削除
4. `<!-- MODEL_USED: ... -->` は最終行に保持
5. ファイル名は `<date>.md`、重複時 `-2`, `-3` 付与
6. ローカルで `drafts/2026-05-13/04_final.md` を変換し `src/articles/2026-05-13.md` を生成、11ty ビルド成功確認済

### 6.4 SKILL.md v2.0.0（v7から変更なし）

`~/.hermes/skills/affiliate-article/SKILL.md`（195行）

---

## 7. cron / 自動実行スケジュール（v7から変更なし）

GitHub Actions: 0 10 * * * UTC（=19:00 JST）= 主力
launchd: ai.tool.navigator.daily 19:00 JST = 並行稼働

---

## 8. 既存記事の状態（Day19夕時点）

### 8.1 src/articles/ 配下 計25記事

#### 公開中・collections に含まれる（20記事相当）

v7 §8.1 の19記事に加え、Day19夕に `2026-05-13.md`（publish.py テストで生成、文系AIエンジニアロードマップ）を追加。ただし `2026-05-13.md` は editor_reviewed:true で本番投入したが、まだ人手校閲は完全には経ていない（自動チェック exit 0 のみ）。

#### noindex（直リンクのみ、6記事）

2026-04-23 生成の6記事、`eleventyExcludeFromCollections: true` 付与済。Day20以降に drafts/withdrawn/ 退避を再判断。

### 8.2 drafts/ 配下

- `2026-05-13/`: テスト用に保持（publish.py の動作確認に使用）
- `2026-05-15/`, `2026-05-16/`, `2026-05-17/`, `2026-05-18/`: gate_fail=1 のドラフト、要 withdrawn 退避判断
- `withdrawn/2026-05-13-2-prelude-leak/`: Day18夜に退避
- `withdrawn/2026-05-14-stage1-input-missing/`: Day19朝に退避
- `withdrawn/articles/`: 既存退避ディレクトリ

### 8.3 既知の重複タイトル（v7から継続、未対処）

- 「LLMファインチューニング入門」(2026-04-28 + 2026-05-08)
- 「AI副業で月5万円を稼ぐロードマップ」(2026-05-02 + 2026-05-12)
- 「文系出身でもAIエンジニア」(2026-05-08 既存 + 2026-05-13 publish.pyテストで生成)

---

## 9. Day18〜19 の出来事

### Day18（2026-05-17 想定の前後）

- **タグページ自動生成**: 8タグの個別ページ `/tags/<tag>/` を Eleventy pagination で生成
- **SEO最適化**: OGP / Twitter Card / JSON-LD（BlogPosting）/ sitemap.xml / robots.txt
- **関連記事カード自動生成**: `relatedTo` フィルタで各記事末尾に4枚カード表示
- **Stage4プロンプト強化＋front-matter漏れgate**（コミット 7288ee4）
- **5/13-2 ドラフトを drafts/withdrawn/ へ退避**（コミット d8e6d35）
- **review_helper.sh の AI開示判定を front-matter優先に変更**（コミット d549de8）

### Day19 朝

- **Run #8 失敗原因の特定**: `scripts/build_topic_context.sh` の引数順バグ
  - 真因: bash 3.2.57 の `[[ … > … ]]` がリダイレクト解釈される + 引数順 `output_file → days → articles_dir` で `articles_dir=30` と誤解釈
  - macOS デフォルトの bash 3.2 と GitHub Actions の bash 5 で挙動が違うことが背景
- **build_topic_context を Python 化**: `scripts/build_topic_context.py` 新規、bash は薄いラッパーに（コミット 8290939）
- **review_helper.sh を workflow に quality gate として統合**（コミット 1e56a6d）
- **2026-05-14 draft を `drafts/withdrawn/2026-05-14-stage1-input-missing/` へ退避**（コミット c4ca9db）
- **handover-v9.md 作成**（コミット 42b9e7c）

### Day19 夕

- **publish-design.md 作成**（コミット c38f8dc、A案: 機械的publish、slug 未対応）
- **publish.py 実装**（コミット 6a30876）
  - ローカルで `drafts/2026-05-13/04_final.md` を変換、`src/articles/2026-05-13.md` 生成、11ty ビルド42ファイル成功
  - review_helper exit 0 確認
- **review_helper.sh の HTML コメント除外修正**（コミット 6a30876）
  - SKIP_PATTERNS に `<!--` を追加、`<!-- MODEL_USED: ... -->` を末尾切れ判定から除外
- **Stage4プロンプト5項目絶対ルール化**（コミット ecd0055）
  - Run #11 で発生したコードフェンス巻き・3500字超過・独白問題への対策
- **GitHub CLI 導入試行 → 失敗**: Homebrew の `/usr/local/` 所有権が壊れており `brew install gh` 不可
  - A案（sudo chown修復）試行→失敗、B案（バイナリ直配置）見送り、C案（諦め）採用
  - 当面はブラウザで GitHub Actions ログを確認

### Run #12（5/18 19:00 JST）効果検証

`drafts/2026-05-18/` の Stage4 出力（claude-haiku-4.5）を検証:

| 検証項目 | 結果 |
|---|---|
| Stage1 復活 | OK: 24件マッチで「働きながらAIを学ぶ時間術」を選定 |
| コードフェンス0回 | OK: ルール2 効果あり |
| 独白なし | OK: ルール3 効果あり |
| `---` 出現3回 | OK: 2行目/16行目/70行目 |
| MODEL_USED 最終行 | OK |
| **1行目=`---`** | NG: 冒頭空行1行（ルール1.1違反） |
| **3500字以内** | NG: 3679字（179字超過、ルール4違反） |

→ publish.py の `strip_leading_noise()` で冒頭空行は吸収可能。3500字超過は claude-haiku-4.5 の文字数制御の弱さが原因と推定。

### Day19 のコミット履歴

- 0820694 Daily draft: 2026-05-18 (gate_fail=1)
- ecd0055 fix(prompt): Stage4プロンプトの絶対ルールを5項目に再構成
- 6a30876 feat: publish自動化スクリプト追加 + review_helper.sh のHTMLコメント除外
- f6f4b81 Daily draft: 2026-05-17 (gate_fail=1)
- eb4a81d Daily draft: 2026-05-16 (gate_fail=1)
- f149d86 Daily draft: 2026-05-15 (gate_fail=1)
- c38f8dc docs: publish自動化の設計書を追加
- 42b9e7c docs: ハンドオーバー資料 v9 を追加
- c4ca9db chore: drafts/2026-05-14 の旧パスを片付け
- 1e56a6d feat: review_helper.sh をquality gateとして統合
- 8290939 fix: build_topic_context の引数順バグを修正（Python版へ書き換え）

---

## 10. 既知の未解決問題（v9から更新）

### 解決済（v10で削除）

- ~~freellmapi auto router 間欠タイムアウト~~ → Day30+ 据え置きで継続監視のみ
- ~~build_topic_context の引数順バグ~~ → Day19朝 解決
- ~~review_helper.sh の HTML コメント誤検出~~ → Day19夕 解決

### 継続中（v9から継続）

1. **CTA一括置換スクリプト未作成**（Day20+、校閲済記事10本溜まってから）
2. **slugify結果の不規則性**（publish.py は A案で `<date>.md` 固定、slug 対応は Stage4 プロンプト改修後 = Day21+）
3. **既存記事のmoshimo CTA**（校閲ワークフロー確立後に置換）
4. **Hermes Skills API 未実装**（upstream 待ち）
5. **Hermes Sessions ペインのプラグイン未提供**（Issue #262 待ち）
6. **`hermes doctor` が gemini 無効報告**（Day30+ トリアージ）
7. **Tailscale 等のリモート手段なし**（管理者権限なし）
8. **Firecrawl 未設定警告**（無害）
9. **既存重複タイトル**: LLMファインチューニング入門 / AI副業ロードマップ / 文系AIエンジニア（3件目はpublish.pyテストで生成）
10. **noindex 6記事の本文品質**（drafts/withdrawn/ 退避を Day20+ で再判断）
11. **04_final.md「使用モデル」表記の統一**（過去から継続、Stage4 で MODEL_USED コメントを末尾に置く運用は確立したが、本文中のテーブル形式表記は別途検討要）
12. **description 未設定の記事**（Day18 で一部対応、全件カバー要確認）
13. **`2026-05-10-2026799.md` の drafts/withdrawn/ 退避が未実施**（Day16 校閲で公開不可判定済）
14. **`2026-04-23-ai.md` が本文ほぼ空でCTAのみ**、退避候補

### v10 新規

15. **Stage4 の Haiku が3500字制御を苦手とする**（Run #11 5/16: 3735字、Run #12 5/18: 3679字）。対策案: Stage4 で Haiku を避けるよう `--model` を gpt系に明示固定、または publish.py 側で本文を自動圧縮する処理を入れる。後者はAI生成品質が劣化するため非推奨。
16. **Stage4 出力の冒頭に空行1行が混入する**（ルール1.1違反）。publish.py で吸収できるが、根本的にはプロンプトでより強く禁止する必要あり。
17. **publish.py が workflow に統合されていない**（ローカル動作確認のみ、Day20で workflow 統合予定）
18. **macOS Homebrew の `/usr/local/` 所有権破損**（gh CLI 等のbrew install が不可）。一度 `sudo chown -R common /usr/local/*` で修復が必要だが、運用ルール「sudo 不使用」と抵触するため棚上げ。
19. **scripts/normalize_tags.py の実行権限が外れている**（`-rw-r--r--`、他のスクリプトは `-rwxr-xr-x`）。再実行時は `chmod +x` が必要。
20. **当初の目的（収益化）からの乖離リスク**: Day18〜19 で技術整備に大量投資。Day20+ は A8審査確認・CTA置換・既存記事の人手校閲など、収益化に直結する作業へリソース配分を戻す必要あり。

---

## 11. 運用ルール（v7から継続）

- 4キャラ会議は明示要請時のみ
- Hermes修正は Day30以降にトリアージ
- XPS13作業は PowerShell構文、Claude Code 非使用
- **sudo 不使用**（管理者権限が必要なものはすべて代替案で対処、Day19の Homebrew修復もこのルールで見送り）
- 記事品質: 誇大表現NG、3000字以上、出典URL必須、AI開示二重化
- 校閲フロー必須: 生成 → 自動チェック → 人手校閲 → 公開
- 新ターミナルでは PATH 復旧: `export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.hermes/node/bin:$PATH"`
- `_site/` は git 管理外
- noindex記事は `eleventyExcludeFromCollections: true` と `noindex: true` を両方記載
- front-matter 終端 `---` の直後に必ず改行
- commit分割: chore / refactor / fix / feat / docs

---

## 12. 直近のTODO（v10更新、優先度順）

### 当初の目的（収益化）への回帰を最優先

Day18〜19 は技術整備に大きく振った。Day20+ は **収益化に直結する作業** を優先する。

### Day20 朝チェック

1. Run #13（5/19 19:00 JST）の確認
   - ブラウザ: https://github.com/kaneko-ai/ai-tool-navigator/actions
   - ローカル: `git pull origin main && git --no-pager log --oneline -5`
   - ドラフト確認: `ls drafts/2026-05-19/` および `head -5 drafts/2026-05-19/04_final.md`
2. プロンプト5項目強化の効果が継続しているか検証

### Day20 着手タスク（収益化優先）

1. **A8提携審査進捗の一括確認**（最優先、最後の確認から1か月以上経過）
   - 申請済10件の現状を A8.net 管理画面で確認
2. **publish.py の workflow 統合**
   - Run #13 が gate_fail=0 で出てくれば、即 workflow に組み込んで自動 publish 化
   - Run #13 も失敗なら Stage4 のプロンプト追加調整
3. **既存24記事から人手校閲対象の選定**
   - 品質基準を満たす記事を優先的に `editor_reviewed:true` 化
4. **重複タイトル3件の統合判断**

### Day20以降

1. CTA一括置換スクリプト作成
2. moshimo CTA → A8確定リンク置換（提携承認後）
3. noindex 6記事の drafts/withdrawn/ 退避
4. `2026-05-10-2026799.md` の退避
5. GA4流入データから記事ジャンル傾向分析

### Day21+

1. publish.py の slug 対応（Stage4 プロンプトに `slug` キー追加）
2. Stage4 の Haiku 文字数超過対策（モデル固定 or プロンプトで「3300字目標」を強調）

### Day30+

1. Hermes (B)/(C) triage
2. freellmapi auto router 根本修正
3. Homebrew 所有権修復（運用ルール再検討含む）

---

## 13. 主要コマンド集（v9から更新）

### PATH 復旧（毎回先頭）

    export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.hermes/node/bin:$PATH"

### Run #N 結果の朝チェック（gh CLI なし版）

    cd ~/ai-tool-navigator && git pull origin main
    git --no-pager log --oneline -5
    ls -la drafts/$(date +%Y-%m-%d)/
    head -5 drafts/$(date +%Y-%m-%d)/04_final.md
    tail -5 drafts/$(date +%Y-%m-%d)/04_final.md
    wc -m drafts/$(date +%Y-%m-%d)/04_final.md
    grep -n "^---" drafts/$(date +%Y-%m-%d)/04_final.md

ブラウザでログ確認: https://github.com/kaneko-ai/ai-tool-navigator/actions

### publish.py 使用法

    # ドライラン
    python3 scripts/publish.py 2026-05-18 --dry-run
    # 本番書き込み
    python3 scripts/publish.py 2026-05-18
    # 結果確認
    ls -la src/articles/2026-05-18*.md
    bash scripts/review_helper.sh src/articles/2026-05-18.md

### build_topic_context.sh 使用法

    # 引数: output_file [articles_dir] [days]
    ./scripts/build_topic_context.sh /tmp/recent_topics.txt src/articles 30
    cat /tmp/recent_topics.txt | head -40

### 11ty ビルド検証

    cd ~/ai-tool-navigator
    rm -rf _site && npx @11ty/eleventy
    ls _site/articles/ | wc -l

### 記事撤回フロー

    mv src/articles/<file>.md drafts/withdrawn/articles/<date>-<reason>.md
    git add -A && git commit -m "withdraw: <reason>" && git push origin main

### Stage4 プロンプトの差分確認

    diff prompts/04_polish.md.bak.20260518 prompts/04_polish.md

---

## 14. 重要なファイルパス（v9から更新）

### ai-tool-navigator 本体

- 旧主力スクリプト: `daily_article_generator.py`（585行、launchd 並行稼働）
- 環境変数: `~/ai-blog-config/.env`
- 記事保存: `src/articles/`
- ドラフト: `drafts/`
- ドラフト退避: `drafts/withdrawn/`
- ログ: `logs/daily.log`、`daily.err`
- launchd plist: `~/Library/LaunchAgents/ai.tool.navigator.daily.plist`

### GitHub Actions / サイト構築

- ワークフロー: `.github/workflows/daily-article.yml`（review_helper.sh 統合済）
- バックアップ: `.github/workflows/daily-article.yml.bak.20260514`
- プロンプト: `prompts/01_topic_select.md` 〜 `04_polish.md`
- プロンプトバックアップ: `prompts/04_polish.md.bak.20260514`, `.bak.20260518`
- 重複防止スクリプト: `scripts/build_topic_context.py` + `scripts/build_topic_context.sh`（ラッパー）
- タグ正規化: `scripts/normalize_tags.py`（実行権限注意）
- 品質チェック: `scripts/review_helper.sh`
- publish 自動化: `scripts/publish.py`
- Eleventy 設定: `eleventy.config.js`
- レイアウト: `_includes/base.njk`, `_includes/post.njk`
- ディレクトリデータ: `src/articles/articles.json`
- 外部CSS: `src/assets/css/style.css`（約430行 + Day18でSEO/カード追記）

### docs/

- `docs/handover-v9.md`（Day19朝版、参照用に保持）
- `docs/handover-v10.md`（本ドキュメント）
- `docs/publish-design.md`（publish 自動化設計書）

### Hermes Agent（v7から変更なし、参考のみ）

- 本体: `~/.hermes/`
- 設定: `~/.hermes/config.yaml`（backup あり）
- スキル: `~/.hermes/skills/affiliate-article/SKILL.md`（v2.0.0）

---

## 15. 次回チャット開始時の最初のアクション

1. このドキュメント v10 を共有
2. ユーザーから Day20 朝の状態確認結果を受け取る:
   - 最新コミット（`git log --oneline -5`）
   - Run #13 の結果（gate_fail=0/1、Stage4 出力の品質）
   - drafts/2026-05-19/ の確認
3. **当初の目的（収益化）に立ち戻り、優先タスクを再評価**:
   - a) A8提携審査進捗の一括確認（最優先）
   - b) publish.py の workflow 統合
   - c) 既存24記事から人手校閲対象の選定
   - d) 重複タイトル3件の統合判断
4. 技術整備は §10 の未解決問題15〜20を優先度低として扱う

---

## v9 → v10 の差分サマリ

- **当初の目的を §1 冒頭に再掲**（技術整備への過剰投資への警告を明示）
- Day18 の作業（タグページ・SEO・関連記事カード・review_helper.sh AI開示改修）を §9 に統合
- Day19朝の作業（build_topic_context Python化・review_helper workflow統合）を §9 に統合
- Day19夕の作業（publish.py・review_helper HTMLコメント除外・Stage4プロンプト5項目化・GitHub CLI 見送り）を §9 に追加
- Run #12 効果検証結果を §9 に追加（コードフェンス・独白・区切り線は解消、冒頭空行・3500字超過は残課題）
- §10 未解決問題に v10新規6件（15〜20）を追加、収益化への回帰を最重要課題として明示
- §12 直近TODOで「収益化に直結する作業」を最優先に再構成（A8審査確認を最上位）
