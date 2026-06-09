# ai-tool-navigator プロジェクト引き継ぎドキュメント v14

**最終更新**: 2026-06-02（Day28 午後時点）
**前回（v13）からの主要更新**:
- **Phase A 自動公開が5日連続成功**（5/29, 5/30, 5/31, 6/1扱い→6/2, 6/2自身）🎉🎉
- **Stage 0 timeout の真因を解明**：x_search の応答時間は通常 119〜121秒、TIMEOUT=120s ではほぼ毎日失敗していた。300s に拡張で復活
- **GitHub Actions cron の最大遅延が5時間51分**であることを実測。19:00 JST 規定だと日付境界を跨ぐ事故が発生（6/1分が6/2扱いに）→ 16:00 JST 規定に前倒しで日付内収容を確保
- **5/29 duplicate content（neuro-dive-check.md）を解明・noindex化**
- 6/1 19:00 cron 遅延による「6/1 記事欠番」が事実上発生（commit上は6/2分として記録）
- 総記事数：33→**40本**（公開 22→30、noindex 11→10、Day24での再整理含む）

---

## 1. プロジェクト概要

- **サイト名**: ai-tool-navigator
- **目的**: AI関連ツールの比較・解説サイトで月5万円のアフィリエイト収益を目指す
- **運営方針**: kanekichi匿名運用、誇大表現NG、データ・実例ベース記事、自動化により人手介入を最小化（v13方針継続）
- **GitHubリポジトリ**: https://github.com/kaneko-ai/ai-tool-navigator
- **公開URL**: https://kaneko-ai.github.io/ai-tool-navigator/
- **公開**: GitHub Pages（11ty/Eleventy v3.1.5）
- **GA4**: 設置済み（測定ID: G-8J2LVW54HE）
- **記事数**: **40本**（src/articles/）
  - 公開対象（collections.articles）: **30本**
  - noindex: **10本**
- **収益構造（Day28時点）**:
  - 記事内CTA: A8_NEURODIVE（多数）、A8_FREELANCEBOARD（複数）、MOSHIMO_CONOHA_WING（URL未配置）
  - 全ページ右サイドバー: 300×250 のA8広告（タグでクリエイティブ自動切替、PC追従）

### v13 → v14 で起きた歴史的瞬間（連発）

**「労力 0.1% 化」が連続稼働で実証された**。

- v13 で初稼働した Phase A 自動公開が、**5/29 〜 6/2 まで5日連続成功**（5/29朝の wokflow 修正の効果も実証）
- Stage 0 → Stage 1 統合は **5/28 の手動成功1回のみ**で、その後 5/29-6/1 は連続失敗していたが、**6/2 朝に真因（TIMEOUT 1秒不足）を解明し復活**
- **6/1 cron が5時間51分遅延して6/2 00:51 JST に動いた**ことで、6/1 分が「実体は存在するが日付は6/2」というハイブリッドな欠番に。GitHub Actions free tier の混雑遅延を実測する貴重なデータ
- v14 では retry logic（v15予定）、JSON-LD schema、AdSense 申請を次フェーズの中核に

---

## 2. 技術スタック

### 自動化パイプライン（v13 から Stage 0 が正式稼働開始）

GitHub Actions: daily-article.yml (cron 07:00 UTC = 16:00 JST、v13 では 10:00 UTC)
  ↓
【Stage 0】 launchd で 15:55 JST に X Premium OAuth + Grok でトレンド上位5-6件取得
  ↓ drafts/YYYY-MM-DD/00_trends.json + 00_trends_summary.md
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
Quality gate (CTA-タグ整合性チェック + review_helper.sh v13修正版)
  ↓
【Phase A】 Auto-publish (gate_fail=0 + src/articles/${DRAFT_DATE_BASE}.md が未存在 のとき publish.py 実行)
  ↓
Commit drafts + src/articles (auto_published=yes/skipped/failed タグ付き)
  ↓
push origin main → GitHub Pages デプロイ

GitHub Actions: weekly-summary.yml (cron 月曜 9:00 JST)
  ↓
weekly_summary.py で過去7日のコミット解析
  ↓
GitHub Issues に投稿（ラベル: weekly-summary, auto-generated）

### Day24-28 で追加/修正したファイル

| ファイル | 役割 | 変更時期 |
|---|---|---|
| `scripts/stage0_trend_fetch.py` | TIMEOUT デフォルト 120s → 300s | Day28 (6/2) |
| `.github/workflows/daily-article.yml` | (1) Stage0空dir再利用 (2) Auto-publish を DRAFT_DATE_BASE で保護 (3) cron 10 UTC → 7 UTC | Day24, Day28 |
| `scripts/review_helper.sh` | メタブロック境界検出を範囲指定方式に書き換え | Day25 (5/28) |
| `scripts/stage0_cron.sh` | launchd 用 cron ラッパー新規作成 | Day25 (5/28) |
| `~/Library/LaunchAgents/ai.tool.navigator.stage0.plist` | Stage 0 用 LaunchAgent（git 管理外） | Day25, Day28 |
| `scripts/watch_daily_cron.sh` | 日次cron監視スクリプト | Day27 (5/29) |
| `prompts/01_topic_select.md` | Xトレンドコンテキスト取扱いルール追加 | Day26 (5/28) |
| `src/articles/2026-05-28.md` | 5/27-2 ドラフトを手動 publish (review_helper 修正と同時) | Day25 |
| `src/articles/2026-05-29-neuro-dive-check.md` | noindex 化（duplicate content 対処） | Day28 |
| `drafts/.archive/` | gate_fail/publish_failed ドラフトの永久保管庫を新設 | Day27 |
| `docs/handover-v14.md` | 本ドキュメント | Day28 |

---

## 3. 自動化パイプライン詳細

### 3.1 Phase A: Auto-publish（5日連続稼働実証）

**実証データ**:

| 日付 | run id | 起動 (UTC→JST) | 遅延 | commit | 公開記事 |
|---|---|---|---|---|---|
| 5/29 | 26638010810 | 12:45→21:45 | 2h45m | 4edd152 | 2026-05-29.md + (手動コピーで) -neuro-dive-check.md |
| 5/30 | 26682430411 | 11:16→20:16 | 1h16m | b98e86b | 2026-05-30.md |
| 5/31 | 26711576328 | 11:39→20:39 | 1h39m | 5bffa84 | 2026-05-31.md |
| **6/1** | **26765895895** | **15:51→6/2 00:51** | **5h51m** | a93f2a2 | **2026-06-02.md（6/1分が6/2扱いに）** |
| 6/2 | (次回 16:00 JST 規定) | - | - | - | - |

**5/29 朝に入れた修正 (`e4f2564`) の効果**:
- `while [ -d "drafts/$DRAFT_DATE" ] && [ -f "drafts/$DRAFT_DATE/01_topic.md" ]; do` で Stage 0 が作る空ディレクトリを再利用
- `ARTICLE_PATH="src/articles/${DRAFT_DATE_BASE}.md"` で base date 側を保護
- `publish.py "$DRAFT_DATE_BASE"` で base date を渡す
- → サフィックス付き draft date による正規表現エラーは完全に解消

### 3.2 Phase B-1〜Phase D（変更なし、v13 § 3.2-3.4 を参照）

### 3.5 Stage 0: X Premium OAuth + Grok でトレンド取得（v14 で真因解明と復活）

**設計**:
- launchd `ai.tool.navigator.stage0` が毎日 15:55 JST に起動（v13 は 18:55、v14 で前倒し）
- `scripts/stage0_cron.sh` が `scripts/stage0_trend_fetch.py` を呼ぶ
- Grok 4.3 + x_search ツールで日本のAI/フリーランス/英語学習関連トレンド上位 5-6 件を JSON 取得
- `drafts/YYYY-MM-DD/00_trends.json` + `_summary.md` を commit & push
- Stage 1 がプロンプト末尾に summary を埋め込み → トピック選定の3軸目として活用

**v13 → v14 で判明した真因**:

| 観測事実 | 当初の推測 | 真因 |
|---|---|---|
| 5/29, 5/30, 5/31 が全て timeout | xAI 側の不調か OAuth 切れ | **TIMEOUT=120s と応答時間 119-121s の差が1〜2秒しかなく、確率的に毎日 timeout** |
| 「30分後・2時間後」に ERROR ログが出る | Hermes の retry ループが回ってる | python の `subprocess.run(..., timeout=TIMEOUT)` は効いていたが、ラッパー側 `git pull` などの後続処理込みで遅延ログが出ていた（仮説） |
| auth.json の exp が既に過ぎている | トークン切れで Hermes が応答しない | Hermes は refresh_token で実通信時に自動更新。auth.json はキャッシュなので exp 経過は無関係。**実際 6/2 12:07-12:09 の手動実行で `1+1は?` も `x_search` も応答**確認 |

**対処（6/2 commit `3064c65`）**:
- `STAGE0_TIMEOUT` デフォルト 120 → 300 秒
- launchd plist の Hour を 18 → 15（cron 前倒しに合わせる）

**復活実証**: 6/2 12:07-12:09 JST に手動実行で 119秒で成功、6 件取得、`drafts/2026-06-02/00_trends.json` (3946 bytes) 作成。commit `6e1f852` で記録用に保管。

### 3.6 review_helper.sh（v13 で根本修正済、変更なし）

5/28 に範囲指定方式に書き換え済（commit `7e25631`）。frontmatter 後の `---` または `文字数:` `採用トピック:` `出典 URL リスト:` `自動チェック結果:` `ヘッダー画像プロンプト:` 以降を一括スキップ。SKIP_PATTERNS 個別追加方式の限界（メタブロック書式変更ごとに壊れる）を解消。

---

## 4. A8アフィリエイト導入詳細（v13 から変更なし、§ 4 参照）

審査中（5/7申請）の Speak、TEPPEN English、TechClips ME、メイカラは**未だ結果待ち**。

---

## 5〜6. プロバイダ・TOPICS配列（v13 から変更なし、本書では省略）

---

## 7. 品質ガードレール（v13 § 7 を踏襲、v14 で 3 件追記）

v13 のルールに加え:

- **【v14新規】 cron 遅延による日付境界跨ぎリスク**: GitHub Actions free tier の scheduled cron は最大5時間51分遅延した実績あり。`0 7 * * *` (UTC 7 = JST 16:00) を採用することで、最大遅延でも JST 21:51 で日付内に収容可能。`0 10 * * *` (JST 19:00) のままだと 24:00 を跨いで翌日扱いの記事になる事故が起きる
- **【v14新規】 Stage 0 TIMEOUT のマージン確保**: x_search の応答時間は 119-121 秒の範囲で揺れる。TIMEOUT は **2.5倍以上のマージン**を確保（120s → 300s）。これは「平均応答時間 + 2σ」を超える値として安全
- **【v14新規】 publish.py の duplicate file 生成リスク**: `resolve_output_path()` は同名重複時 `-2, -3...` を機械的に付ける仕様。slug 付きファイル名（`-neuro-dive-check.md` のような意味ある文字列）は publish.py 由来ではなく**手動コピー or 別経路の介在を疑うべき**。重複検知時は両方を読んで差分を取り、正規版 (publish.py 正規化済) と非正規版を識別する

---

## 8. cron / 自動実行スケジュール（v14 で時刻変更）

| ジョブ | 時刻 | 動作 |
|---|---|---|
| **launchd: ai.tool.navigator.stage0** | **毎日 15:55 JST**（v13: 18:55） | Stage 0 X Premium OAuth + Grok でトレンド取得 |
| **GitHub Actions: daily-article.yml** | **毎日 16:00 JST 規定**（v13: 19:00 規定。実際は最大 5h51m 遅延） | Stage 1〜4 + Phase B-1 + Quality gate + Phase A |
| GitHub Actions: weekly-summary.yml | 月曜 9:00 JST | Phase D 週次サマリ Issue 投稿 |
| launchd: ai.tool.navigator.daily | 毎日 19:00 JST | 旧主力スクリプト（v12 から並行稼働、launchctl 未ロードのため実質停止中） |
| launchd: ai.tool.navigator.gitpull | 6:00-18:59 JST 5分間隔 | git pull 常駐（push なし、Stage 0 と時刻衝突なし） |
| launchd: ai.hermes.gateway | 常駐 (PID 動的) | Hermes Agent gateway |

**時刻設計の背景**:
- Stage 0 → Actions cron 順番が重要。Stage 0 が trends を commit & push してから Actions が checkout する流れ
- 15:55 (Stage 0) → 16:00 (Actions 起動) → 16:05〜16:10 (実際のジョブ start) で5〜10分のバッファ確保
- Mac がスリープしていると launchd 15:55 トリガーを逃すため、Mac は 15:55 時点で稼働している必要あり
- LaunchAgent の `RunAtLoad: false` のため、スリープ復帰後の自動キャッチアップは無い（v14 #課題）

---

## 9. 既存記事の状態（Day28時点・40本）

### 9.1 公開中（collections.articles）30記事

v13 時点の 22 記事から +8（5/22, 5/23, 5/24, 5/26欠番, 5/28〜6/2扱い記事の追加）。

### 9.2 noindex（10記事）

v13 時点の 11 記事から実質 +1 (5/29-neuro-dive-check.md)、ただし v13 で「2026-05-10-2026799.md」の drafts/withdrawn/ 退避がさらに進んだか、または計算基準のぶれで -1 されており、結果として **11 → 10** で着地。

**現状 noindex 記事一覧（10件）**:
- 2026-04-23-2026-ai-api-nvidia-nim-google-ai-etc.md
- 2026-04-23-ai-5.md
- 2026-04-23-ai.md
- 2026-04-23-hermes-agent-vs-openclaw.md
- 2026-04-23-hermes-agent.md
- 2026-04-23-nvidia-nim-api.md
- 2026-05-08-llmai.md
- 2026-05-11-hermes-agent.md
- 2026-05-20.md
- **2026-05-29-neuro-dive-check.md**（v14 で追加）

### 9.3 Day24-28 で publish した記事（自動・手動含む）

| 日付 | 状態 | タイトル | CTA | 経緯 |
|---|---|---|---|---|
| 2026-05-28 | 手動 publish | 給付金・助成金で選ぶAI学習先 | なし | 5/27-2 ドラフトを review_helper 修正と同時に手動公開 |
| 2026-05-29 | **Phase A 自動** | (Neuro Dive 給付金対象コース解説) | A8_NEURODIVE | 自動公開 |
| 2026-05-29-neuro-dive-check | 手動コピー（**duplicate**） | Neuro Diveを選ぶ前に知るべきこと | (同上) | 04_final.md からの slug 付きコピーと推測 → **v14 で noindex 化** |
| 2026-05-30 | **Phase A 自動** | (記事タイトル要確認) | (要確認) | 自動公開 |
| 2026-05-31 | **Phase A 自動** | (記事タイトル要確認) | (要確認) | 自動公開 |
| 2026-06-02 | **Phase A 自動** | (記事タイトル要確認、本来は6/1分が遅延で6/2扱いに) | (要確認) | 自動公開、cron 5h51m 遅延 |

---

## 10. Day24-28 の出来事（時系列）

### Day24 (2026-05-27) — Phase A 連続稼働の検証開始

- 19:00 JST cron 失敗 → 5/26 と 5/27 が欠番リスク
- 手動 rerun でリカバリ、5/27 分の Phase A 初成功（v13 で記録済）
- handover-v13 起稿

### Day25 (2026-05-28) — review_helper 根本修正 + Stage 0 launchd 化

**午前**:
- 5/27-2 draft の gate_fail=1 を解析 → SKIP_PATTERNS の全角/半角スペース不一致と判明
- `scripts/review_helper.sh` を範囲指定方式に書き換え（commit `7e25631`）
- 5/28.md を手動 publish

**午後**:
- Stage 0 launchd 設計確定（A 案: ローカル Mac で launchd、CI とは独立）
- `scripts/stage0_cron.sh` 作成（commit `99da8f1`）
- LaunchAgent plist 配置・bootstrap
- 初回テスト実行 → 2分5秒で 6 トレンド取得成功（commit `e581b06`）

### Day26 (2026-05-28 夕方) — Stage 1 トレンド統合

- `.github/workflows/daily-article.yml` 改修（commit `9344ea2`）:
  - `draft_date_base` 出力追加
  - Stage 1 に `00_trends_summary.md` 存在チェック分岐追加
  - 存在すれば Xトレンドセクションをプロンプト末尾に付加、無ければ従来通り
- `prompts/01_topic_select.md` に「Xトレンドコンテキストの取り扱い (優先ルール)」追加
- ローカルドライランで 221 行 / 13235 バイトのプロンプトを検証

### Day27 (2026-05-29) — Phase A 修正 + 観察スクリプト

**朝**:
- 前日 5/28 cron の commit メッセージ確認: `Daily draft: 2026-05-28-2 (gate_fail=0 auto_published=failed)` を発見
- 真因究明: publish.py の正規表現 `^\d{4}-\d{2}-\d{2}$` がサフィックス付き `2026-05-28-2` を弾いていた
- ワークフロー修正（commit `e4f2564`）:
  - while 条件に `01_topic.md` 存在チェック追加
  - ARTICLE_PATH を DRAFT_DATE_BASE に変更
  - publish.py 引数も DRAFT_DATE_BASE に変更
- `drafts/2026-05-27-2` と `drafts/2026-05-28-2` を `drafts/.archive/` に退避（commit `0170f60`）
- `scripts/watch_daily_cron.sh` 作成（commit `6b2eccf`）
- zsh 設定改善（`interactive_comments`, `no_nomatch` を `~/.zshrc` に追加）

**夕方〜夜**:
- 18:55 launchd で Stage 0 が起動 → **120s timeout で失敗**（このとき真因は未解明）
- 19:00 cron は workflow 修正後の初稼働を控えていた

### Day27.5 (2026-05-29 〜 2026-06-01) — Phase A 静かなる連続稼働

- 5/29, 5/30, 5/31 と Phase A が連続成功（毎日 1-3 時間の cron 遅延あり）
- **Stage 0 は 3日連続失敗**（TIMEOUT 真因は未解明）
- Stage 1 は fallback で固定30トピックから選定 → 5/29-31 の記事には「採用Xトレンド」行なし
- 5/30 朝のどこかで誰かが `2026-05-29-neuro-dive-check.md` を手動コピー（仮説）
- 6/1 cron が大遅延（UTC 15:51 = JST 6/2 00:51）→ 6/2 扱いの記事として a93f2a2 commit

### Day28 (2026-06-02) — 真因解明デー

**午前**:
- 不在中の3日分を確認 → Phase A 連続成功、Stage 0 連続失敗、6/1 欠番（実は6/2扱い）の3点を把握
- JWT 解析でトークン期限切れと iat/exp/refresh の関係を理解 → トークンは問題ないと判明
- **手動 Stage 0 実行で 119秒成功**を確認 → TIMEOUT 1秒不足が真因と確定
- 修正実施（commit `3064c65`）:
  - `STAGE0_TIMEOUT` デフォルト 120 → 300 秒
  - workflow cron 10 UTC → 7 UTC（19:00 JST → 16:00 JST 規定）
  - launchd plist Hour 18 → 15（git 管理外）
  - launchd 再ロード
- 6/2 trends を記録用に commit（`6e1f852`）
- 6/1 空ディレクトリ削除
- 5/29 duplicate content を noindex 化（commit `4c0d9bd`）
- handover-v14 起稿

---

## 11. 既知の未解決問題（v14更新）

### v13 から継続

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
12. description 未設定の記事の一括補完
13. `2026-05-10-2026799.md` の drafts/withdrawn/ 退避未実施
14. publish.py が末尾メタブロックの出典URLを削除する（プロンプト側で本文インライン必須化で回避済）
20. Node.js 20非推奨警告（GitHub Actions、2026年9月以降に対応必要）
21. gh CLI が macOS再起動後に PATH から外れる可能性（要観察継続）
23. noindex 化チェックリストの徹底（`noindex: true` + `eleventyExcludeFromCollections: true` セット必須）
25. 5/26 補填記事が未作成（任意・優先度低）
26. `<!-- MODEL_USED: ... -->` 末尾 `>` の review_helper 警告（v13 で範囲指定方式に変更したため実質解消）
29. `~/.hermes/config.yaml.bak*` が 4 ファイル堆積（整理候補）
30. `ai.tool.navigator.gitpull` の挙動詳細未確認（低優先）

### v13 で解消

- ~~17. 2026-05-20.md が字数・出典下限割れ~~ → v13 で noindex 化
- ~~19. 5/19, 5/20 の MOSHIMO_CONOHA_WING~~ → v13 で削除完了
- ~~22. Phase A の初稼働未確認~~ → v13 で 5/27 初稼働、v14 で5日連続稼働実証
- ~~24. 19:00 JST 定時 cron に retry logic が無い~~ → 部分的に v14 で対処（cron 時刻を早めて遅延耐性を確保）。本格 retry は v15 課題
- ~~27. x_search ツールが disabled~~ → v13 で有効化済
- ~~28. xAI OAuth 未ログイン~~ → v13 で完了、v14 で refresh も自動動作確認

### v14 新規

31. **GitHub Actions free tier cron の最大遅延が5時間51分**（実測）。`0 7 * * *` (16:00 JST 規定) で日付内収容を確保したが、さらに遅延がひどくなる可能性は残る。完全な対策は launchd で `gh workflow run` を叩く方式（v15 候補）
32. **launchd の `RunAtLoad: false` + Mac スリープ復帰時のキャッチアップなし**: Mac が 15:55 時点でスリープしていると Stage 0 はその日スキップされる。`RunAtLoad: true` + 起動時刻判定をスクリプト側に持つ案を検討
33. **5/29 duplicate content の根本原因が未確定**: `2026-05-29-neuro-dive-check.md` が誰の手で作られたかが不明。publish.py の `resolve_output_path()` は `-数字` のみ生成するので機械由来ではない。**仮説1**: 手動で `cp drafts/2026-05-29/04_final.md src/articles/2026-05-29-neuro-dive-check.md` を実行した。**仮説2**: 別の slug 生成スクリプトが過去存在した。再発防止のため scripts/ 全体を grep する必要あり
34. **6/1 のような cron 大遅延時の挙動**: 現在の workflow は `TZ=Asia/Tokyo date +%Y-%m-%d` で実行時点の日付を取るので、cron 起動時刻が日付を跨ぐと「実行日」になる。理想は「schedule 起動 datetime → そこから JST date を計算」だが、Actions の `github.event.schedule` 経由で取得すれば事故防止可能（v15 候補）
35. **`drafts/2026-06-01/` のような空ディレクトリ自然発生**: Stage 0 ラッパーが mkdir -p するため、Stage 0 失敗時に空ディレクトリだけ残る。git 管理外なので clean だが、launchd skip 判定の誤動作リスクあり。ラッパーに「失敗時は mkdir した空ディレクトリを削除する」trap を追加検討

---

## 12. 運用ルール（v13 § 12 を踏襲、v14 で 4 件追記）

v13 のルールに加え:

- **【v14新規】 GitHub Actions cron 時刻設計**: 規定時刻は **必ず JST 17:00 より前**にする。free tier の遅延は最大 6時間程度を見込み、JST 24:00 を跨がない範囲で設定。記事生成後の確認時間も考慮すると、JST 16:00 規定 / 実行 16:00-22:00 のレンジが理想
- **【v14新規】 Stage 0 TIMEOUT 設計**: 外部API（x_search 等）の応答時間は揺らぐので、**実測平均の 2.5倍以上**のマージンを TIMEOUT に設定。120s 設定で 119s 応答という危険な綱渡りは絶対に避ける
- **【v14新規】 duplicate content 検知時の対処手順**:
  1. 両方の front-matter を比較 → editor_reviewed の値、末尾メタブロック有無で「正規版」と「非正規版」を識別
  2. 正規版は触らず、非正規版に `noindex: true` + `eleventyExcludeFromCollections: true` を追加
  3. handover に経緯と根本原因の仮説を記録
  4. 再発防止策を考える（scripts grep、運用フロー見直し）
- **【v14新規】 launchd plist と git 管理の分離**: `~/Library/LaunchAgents/*.plist` は **Mac ローカル設定のため git 管理外**。handover の `## 8. cron スケジュール` でカバーし、変更時は plist の Hour/Minute と workflow cron 時刻の整合性を必ず確認

---

## 13. 直近のTODO（v14更新、優先度順）

### A群（完了・Day28終）

1. ~~5/29 朝の Phase A 修正~~ ✅
2. ~~drafts/.archive/ 設計と退避~~ ✅
3. ~~watch_daily_cron.sh 作成~~ ✅
4. ~~Stage 0 timeout 真因究明と修正~~ ✅
5. ~~workflow cron 時刻前倒し~~ ✅
6. ~~5/29 duplicate content 対処~~ ✅
7. ~~handover-v14.md 起稿~~ ✅（本ドキュメント）

### B群（今週末・Day29-30）— 観察 + 軽い改善

8. 新時刻 cron の初稼働観察: 6/2 16:00 JST の Actions と 15:55 launchd の動作確認
9. Stage 0 の連続稼働実証: 6/3, 6/4, 6/5 の3日連続成功で Stage 0 → Stage 1 統合の付加価値が初めて実現
10. 5/30, 5/31, 6/2 公開記事の品質ザッと確認
11. 5/29 duplicate 再発防止: scripts/ 全体を grep で検索、不審なスクリプトの存在確認
12. drafts/2026-06-01/ のような空ディレクトリ自動掃除: stage0_cron.sh の trap 追加
13. drafts/2026-05-26 が無い件の判断

### C群（来週・Day31-35）— 構造改善とSEO

14. GitHub Actions retry logic 導入（nick-fields/retry@v3）
15. launchd の RunAtLoad: true 化検討
16. JSON-LD Article schema 追加
17. FAQ schema 自動生成
18. トピッククラスター再編成（4 pillar pages）
19. 内部リンク自動化
20. Node.js 24 移行

### D群（再来週以降・Day36+）— 集客とマネタイズ

21. Core Web Vitals 最適化
22. Google AdSense 申請（40記事達成、最適タイミング）
23. X 連携: トレンド記事を自動投稿
24. GA4 流入データ分析、CTA配置の最適化
25. A/Bテスト導入
26. publish.py のバグ修正
27. メールマガジン導入

### E群（低優先・任意）

28. ~/.hermes/config.yaml.bak* 4 ファイル整理
29. ai.tool.navigator.gitpull の挙動詳細確認
30. Nous Portal / Qwen OAuth ログイン
31. description 未設定の記事一括補完
32. 重複「AI副業ロードマップ」2記事の統合判断

### F群（v15 で扱う設計判断）

33. cron 大遅延への根本対策（launchd で gh workflow run 案）
34. schedule 起動時刻ベースの日付計算
35. publish.py の slug 対応

---

## 14. 主要コマンド集（v13 § 14 から v14 用を追記）

### PATH 復旧（毎回先頭）

export PATH="$HOME/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.hermes/node/bin:/Users/common/.local/bin:$PATH"

### Day29 朝チェック

cd ~/ai-tool-navigator
tail -20 ~/Library/Logs/ai-tool-navigator/stage0.log
gh run list --workflow=daily-article.yml --limit 5
git --no-pager log --oneline --grep="auto_published=yes" -10
TODAY=$(TZ=Asia/Tokyo date +%Y-%m-%d)
ls -la src/articles/${TODAY}.md 2>/dev/null
grep -A1 "採用Xトレンド" drafts/${TODAY}/01_topic.md 2>/dev/null

### Stage 0 手動実行（緊急対応用）

STAGE0_TIMEOUT=300 python3 scripts/stage0_trend_fetch.py $(TZ=Asia/Tokyo date +%Y-%m-%d)

### 監視

./scripts/watch_daily_cron.sh

### Stage 0 launchd 再ロード

launchctl bootout gui/$(id -u)/ai.tool.navigator.stage0
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.tool.navigator.stage0.plist
launchctl print gui/$(id -u)/ai.tool.navigator.stage0 | grep -E "state|runs|exit"

### duplicate content 検知（運用）

for d in $(ls src/articles/ | sed 's/\.md$//' | sed 's/-[a-z].*$//' | sort -u); do
  count=$(ls src/articles/${d}*.md 2>/dev/null | wc -l | tr -d ' ')
  [ "$count" -gt 1 ] && echo "DUP: $d ($count files)" && ls src/articles/${d}*.md
done

---

## 15. 重要なファイルパス（v13 から差分のみ）

### v14 新規・修正

- docs/handover-v14.md: 本ドキュメント
- scripts/stage0_trend_fetch.py: TIMEOUT 120s → 300s（commit 3064c65）
- .github/workflows/daily-article.yml: cron 0 10 → 0 7、while 条件 + DRAFT_DATE_BASE
- ~/Library/LaunchAgents/ai.tool.navigator.stage0.plist: Hour 18 → 15（git 管理外）
- drafts/.archive/: gate_fail/publish_failed ドラフト保管庫
- scripts/watch_daily_cron.sh: 日次監視
- src/articles/2026-05-29-neuro-dive-check.md: noindex 化
- drafts/2026-06-02/00_trends.json + _summary.md: Stage 0 復活初成功

### ~/.zshrc 追記内容（git 管理外）

setopt interactive_comments
setopt no_nomatch

---

## 16. 完成形のビジョン（v13 § 16 を踏襲、Stage 0 復活効果を反映）

### 短期完成形（Day35時点、約1週間後）

- 記事数: 45〜55本（v14 で 40 達成済、毎日 +1 で順調）
- A8提携: 10プログラム
- 自動化: Phase A〜D 完成 + Stage 0 復活 + retry logic
- GA4: 月間PV 5,000〜10,000 目標
- 月間収益: 1万円〜3万円目標

### 中期完成形（Day65時点、約1ヶ月後）

- 記事数: 80〜100本
- カテゴリハブページ: AI学習 / フリーランス / 英語学習 / ブログ運営
- Stage 0 のXトレンドが Stage 1 で実際に採用される率 30-50%
- メールマガジン: 100〜300登録者
- 月間PV: 20,000〜30,000
- 月間収益: 3万円〜5万円（目標達成）

### 長期完成形（Day120+）

- 記事数: 200本+
- 派生サイト: 英語学習特化、フリーランス特化
- 自社プロダクト: AI比較診断ツール

---

## 17. 次回チャット開始時の最初のアクション

1. このドキュメント v14 を共有する
2. Day29 朝の状態確認結果を受け取る:
   - 6/2 15:55 launchd の Stage 0 が成功したか
   - 6/2 16:00 規定の Actions cron が日付内に動いたか
   - drafts/2026-06-02/01_topic.md に 採用Xトレンド 行が含まれるか
3. Stage 0 → Stage 1 統合の本番初稼働を見届ける
4. B群着手: scripts/ grep で duplicate 真因究明 + 空ディレクトリ自動掃除
5. C群展望: retry logic, JSON-LD, トピッククラスター
6. AdSense 申請のタイミング相談

---

## v13 → v14 の差分サマリ

| 項目 | v13 | v14 |
|---|---|---|
| Phase A 稼働状況 | 5/27 初稼働、連続稼働未確認 | 5日連続成功（5/29-6/2）実証 |
| Stage 0 稼働状況 | 5/28 手動成功 1 回のみ | 5/29-5/31 失敗 → 6/2 真因解明 → 復活 |
| Stage 0 TIMEOUT | 120s（応答時間と綱渡り） | 300s（2.5倍マージン） |
| GitHub Actions cron | 0 10 UTC = 19:00 JST 規定 | 0 7 UTC = 16:00 JST 規定 |
| cron 遅延の実態 | 把握なし | 最大 5h51m を実測 |
| Stage 0 launchd 時刻 | 18:55 JST | 15:55 JST |
| publish.py 正規表現バグ | 未認識 | base date 渡しで対処済 |
| drafts/.archive/ | なし | 新設 |
| watch_daily_cron.sh | なし | 新規追加 |
| duplicate content | 未認識 | 5/29 noindex 化、根本原因は仮説段階 |
| 記事数 | 33本 | 40本（公開 30 / noindex 10） |
| zsh 運用環境 | デフォルト | interactive_comments + no_nomatch |
| 労力0.1%化 | 実証完了 | 5日連続稼働で安定稼働を実証 |

---

handover-v14.md 作成日: 2026-06-02（Day28 午後）
Phase A 連続稼働実証 + Stage 0 復活記念ドキュメント


---

## 補遺: 6/4 朝の rescue 作業メモ (2026-06-03 追記)

### 背景

- `drafts/2026-06-02-2/` は Stage 0 → Stage 1 統合の初の歴史的成果ドラフト
  - 採用Xトレンド: 「副業収入1.5倍 / 6h前 / freelance」
  - タイトル: 「AI副業で新卒年収1.5倍へ〜独立判断と資産戦略」
  - 3187字、出典6本 (金融庁NISA等)、CTAプレースホルダ2箇所配置済み
  - quality_gate 全通過 (gate_fail=0)
- ただし 6/2 当日は既に正記事 `src/articles/2026-06-02.md` が存在し `auto_published=skipped` でコミットのみ
- 6/2 正記事「AI副業で独立を試す実践ロードマップ」と隣接させると重複感が出るため、6/3 を挟んで 6/4 に rescue 配置する判断

### 準備済み状態 (2026-06-03 朝)

- `drafts/2026-06-04-rescued/` 作成済み (untracked)
- `04_final.md` の date を 2026-06-04 に書き換え済み
- publish.py の仕様確認済み: 引数 YYYY-MM-DD 厳格、`drafts/<date>/04_final.md` 決め打ち
- stage0 skip ロジック確認済み: `00_trends.json` の存在のみで判定
- → 6/4 朝に `drafts/2026-06-04-rescued/` → `drafts/2026-06-04/` リネームすれば衝突なし

### 6/4 朝の実行手順 (15:00 JST までに完了させる)

1. `mv drafts/2026-06-04-rescued drafts/2026-06-04`
2. `python3 scripts/publish.py 2026-06-04 --dry-run`
3. `python3 scripts/publish.py 2026-06-04`
4. `ls -la src/articles/2026-06-04.md` で確認
5. `git add drafts/2026-06-04 src/articles/2026-06-04.md`
6. `git commit -m "rescue: drafts/2026-06-02-2 を 6/4 記事として救出公開"`
7. `git push origin main`

### 6/4 cron との衝突予測

- 15:55 launchd Stage 0: `drafts/2026-06-04/00_trends.json` 既存 → skip OK
- 16:00 GitHub Actions cron:
  - workflow while 条件で `drafts/2026-06-04/01_topic.md` 既存検出 → `drafts/2026-06-04-2/` で Stage 1-4 走行
  - Phase A は `src/articles/2026-06-04.md` 既存 → skip OK
  - `auto_published=skipped` で `drafts/2026-06-04-2/` のみコミットされる予想
- 6/4-2 ドラフトは後日 archive 行きか、また rescue 候補かで判断

### 仮説と懸念

- 仮説: rescue 記事の date が 2026-06-04 に書き換わっても character_count や本文内の日付参照が古いままの可能性
  - 確認コマンド: `grep -n "2026-06-02\|6/2\|6月2日" drafts/2026-06-04-rescued/04_final.md`
  - 必要に応じて本文も書き換える
- 懸念: A8アフィリエイト CTA タグが freelance ジャンルで適切に展開されるか
  - `<!-- CTA:A8_FREELANCEBOARD -->` プレースホルダの実体化は Eleventy ビルド時に行われる想定
  - 既存記事 (5/23, 5/30, 5/31) のレンダリング結果と比較確認推奨



---

## 補遺 B: 2026-06-04 達成記録（Healthchecks.io 統合 + SEO 強化 + Rescue 公開）

**作業日時**: 2026-06-04 (06:00 - 12:15 JST)
**ステータス**: ✅ 全タスク完了、本番運用中

### B-1. 6/3 の Stage 0 → Stage 1 統合初成功（前夜の振り返り）

- 6/3 15:58 JST: launchd Stage 0 自動起動（予定 15:55 から 3 分遅れ、許容範囲内）
- トレンド 6 件取得 → `drafts/2026-06-03/00_trends.json` (3683 bytes) 生成
- commit `68e032f` で push 成功
- 6/3 20:55 JST: GitHub Actions Stage 1〜4 起動（cron 予定 19:00 から 4h 55m 遅延）
- Phase A 自動公開成功 → `src/articles/2026-06-03.md` (6001 bytes) 生成
- commit `b3ee392` (`auto_published=yes`)
- **意義**: Stage 0 取得 → Stage 1 利用の完全連携を初実証

### B-2. 6/4 Rescue 記事公開（drafts/2026-06-02-2 救出）

**背景**: 6/2 に Stage 0→Stage 1 連携の初成果として `drafts/2026-06-02-2/` が生成されたが、当日既に正規 6/2 記事 (`src/articles/2026-06-02.md`) が存在したため `auto_published=skipped`。歴史的価値のあるドラフトを救うため 6/4 へ配置（6/3 を挟んで重複回避）。

**手順実行ログ**:
1. `cp -r drafts/2026-06-02-2 drafts/2026-06-04-rescued`（6/3 朝、事前準備）
2. `sed -i '' 's|^date: 2026-06-02$|date: 2026-06-04|'` で front-matter 修正
3. 6/4 朝 `mv drafts/2026-06-04-rescued drafts/2026-06-04`
4. `python3 scripts/publish.py 2026-06-04 --dry-run` で検証
5. 本番 publish → `src/articles/2026-06-04.md` (7127 bytes, 3187 字)
6. commit `b4d4b08` push

**記事**: 「AI副業で新卒年収1.5倍へ〜独立判断と資産戦略」
- tags: ai-tools, freelance, ai-engineer-income
- 主要数値: 平均月単価 79.9 万円、目標月収 37.5 万円、時給換算 5000 円
- 段階的収入モデル（0-3 / 3-9 / 9-18 ヶ月）

**事後検証**: 16:00 JST の GitHub Actions が `drafts/2026-06-04/01_topic.md` 存在を検知し `drafts/2026-06-04-2/` を生成、Phase A は `src/articles/2026-06-04.md` 存在で skipped → 想定通り。

### B-3. JSON-LD BlogPosting を E-E-A-T 強化版に更新

**ファイル**: `_includes/post.njk`（commit `a13b6f6`）

**変更点**:
- `author.@type` を `Organization` → `Person`（個人運営の透明性向上）
- `publisher.logo` を追加（Google リッチスニペット要件）
- `image` プロパティを追加（front-matter `image` または `assets/images/ogp-default.png`）
- `wordCount` を `character_count` から自動設定（古い記事はスキップ）
- `articleSection` を最初のタグから自動設定

**検証結果**:
- 全記事で JSON 構文 valid
- 5/31 記事: wordCount 2738, articleSection "ai-tools"
- 6/2 記事: wordCount 2627, articleSection "ai-tools"
- 6/4 記事: wordCount 3187, articleSection "ai-tools"
- 4/23 旧記事（character_count 無し）: wordCount スキップ動作確認、articleSection は出力 ✅

**残課題**: `assets/images/ogp-default.png` と `logo.png` の実体ファイル未作成（現状 404）。リッチスニペット完全対応のため近日中に作成予定。

### B-4. Healthchecks.io 監視統合（3 check 体制）

**アカウント**: ai-tool-navigator プロジェクト
**プラン**: 無料（20 check まで、現在 3 使用）

**Check 一覧**:

| Check 名 | Schedule | Grace | Tags | 用途 |
|---|---|---|---|---|
| Stage 0 - launchd trend fetch | 55 15 * * * (JST) | 30 min | stage0, launchd, daily | Mac ローカル launchd 監視 |
| GitHub Actions daily-article | 0 7 * * * (UTC) | 6 h | stage1, github-actions, daily | Stage 1〜4 全体監視 |
| Phase A - auto-publish success | 0 7 * * * (UTC) | 7 h | phase-a, publish, daily | 自動公開成否監視 |

**Ping URL 管理方針**:
- Stage 0: launchd plist `~/Library/LaunchAgents/ai.tool.navigator.stage0.plist` の `EnvironmentVariables` に `HC_STAGE0` を直接埋め込み（ローカルのみ、git 管理外）
- Stage 1, Phase A: GitHub repository secrets `HC_STAGE1` / `HC_PHASE_A` として登録
- `~/.zshrc` にも export 設定（手動テスト用）

**実装**:

**Stage 0 (`scripts/stage0_cron.sh`)** — commit `04724b5`
- `hc_ping()` ヘルパー関数追加（`HC_STAGE0` 未設定なら no-op）
- start ping: 起動直後
- success ping: 正常終了（skip 含む）
- fail ping: 各エラー箇所（cd 失敗、python 失敗、JSON 不在、サイズ 0 等）

**Stage 1 / Phase A (`.github/workflows/daily-article.yml`)** — commit `a36f67f`
- Notify Healthchecks (Stage 1 start): Checkout 前に挿入
- Notify Healthchecks (Phase A result): Phase A 直後、`published` 出力で分岐
  - `yes` or `skipped` → success ping（skipped は正常運用なので success 扱い）
  - `failed` → /fail ping
  - その他（quality gate fail 等）→ /fail ping
- Notify Healthchecks (Stage 1 success): `if: success()` で job 末尾
- Notify Healthchecks (Stage 1 fail): `if: failure()` で job 末尾
- 全 ping は `continue-on-error: true` で Healthchecks 障害が workflow を落とさない設計

**本番検証ログ**:
- 6/3 18:22 JST: 手動実行 → Stage 0 start/success ping 確認、ダッシュボード反映 OK
- 6/4 09:44 JST (00:44 UTC): workflow_dispatch 手動実行（run ID 26922602046）
  - 実行時間 3 m 36 s、全 stage success、Phase A skipped → success ping ✅
  - Healthchecks ダッシュボードで "GitHub Actions daily-article" "Phase A auto-publish" 両方が緑 ✓
- 6/4 12:12 JST: `launchctl kickstart` で Stage 0 launchd 経由テスト → start ping 送信確認

### B-5. その他の整備

- `.gitignore` に `*.bak`, `*.bak.*`, `*.bak-*` を追加（commit `04724b5` の一部）
  - 既存の 26 個の bak ファイルは untracked のまま残置（将来一括削除予定）
- handover-v14.md に Rescue 作業メモを追記（commit `5d5935c`）

### B-6. 残課題（v14 完了に向けて）

**短期（1 週間以内）**:
1. **OGP デフォルト画像作成**: `assets/images/ogp-default.png`（1200×630）と `logo.png`（512×512 程度）。JSON-LD `image` / `publisher.logo` の 404 解消、Twitter/Facebook シェア時の見栄え向上
2. **AdSense 申請準備**: `/about/` `/privacy/` ページ内容の充実、`ads.txt` 雛形作成、申請手続き開始
3. **Twitter Card を `summary_large_image` に変更**: OGP 画像準備後
4. **bak ファイル一括削除**: 26 個の旧バックアップを `find -name "*.bak*" -delete` で整理

**中期（1 ヶ月以内）**:
5. **Person/Author schema 追加**: about ページに JSON-LD Person で運営者情報構造化
6. **IndexNow 通知**: 記事公開時に Bing/Yandex へ即座通知（publish.py 拡張）
7. **GitHub Actions retry logic**: `nick-fields/retry@v3` で Copilot API 一時障害に耐性
8. **`<time datetime>` を ISO-8601 化**: 現在 `Date.toString()` 出力で `Thu Apr 23 2026 09:00:00 GMT+0900 (日本標準時)` 形式

**長期（2 ヶ月以内）**:
9. Lighthouse CI / Core Web Vitals 自動測定
10. eleventy-img プラグインでサムネイル自動生成
11. Cloudflare Pages プレビュー環境（PR ベース）
12. Hermes Agent 自己学習結果の品質ゲート連動

### B-7. 主要コミット履歴（6/2 〜 6/4）

```
9e9c43b Daily draft: 2026-06-04-2 (gate_fail=0 auto_published=skipped, ...)
a36f67f feat(ops): GitHub Actions に Healthchecks.io ping を組み込み
b4d4b08 rescue: drafts/2026-06-02-2 を 6/4 記事として救出公開
04724b5 feat(ops): Stage 0 cron に Healthchecks.io ping を組み込み
b3ee392 Daily draft: 2026-06-03 (gate_fail=0 auto_published=yes, ...)
68e032f stage0: 2026-06-03 のXトレンド取得
a13b6f6 feat(seo): JSON-LD BlogPosting を E-E-A-T 強化版に更新
5d5935c docs(handover-v14): 6/4 rescue 作業メモを補遺に追記
c169eb6 docs: handover-v14.md を追加 - Phase A 連続稼働実証 + Stage 0 復活記念版
a053982 Daily draft: 2026-06-02-2 (Stage 0→Stage 1 統合初成果)
```

### B-8. 運用所感

- **Stage 0 launchd は安定**: 6/2 の TIMEOUT=300s 修正以降、3 日連続成功
- **GitHub Actions cron 遅延は常態化**: 6/3 は 4h 55m 遅延、Healthchecks の Grace 6h は妥当
- **Phase A の skipped を success 扱いにする判断**: 手動 rescue や複数本生成の運用パターンを許容する設計、誤通知抑制に寄与
- **記事品質**: 末尾切れ・文字数オーバー等の warning は時折出るが gate_fail には至らず、自動公開は許容範囲

---

*補遺 B 追記: 2026-06-04 12:15 JST*

補遺 C: 2026-06-05 SEO短期項目スプリント（OGP/Twitter Card/bak削除/AdSense/time/IndexNow）
作業日時: 2026-06-05 (09:00 - 12:30 JST 頃)。補遺 B-6「残課題（短期）」の優先4項目 + 追加でB-6短期8番・6番（第1段階）・5番確認を実施。

C-1. OGP デフォルト画像・ロゴ作成（B-6 短期1）完了
Nano Banana Pro (Gemini 3 Pro Image) で生成、トリミングして配置。
src/assets/images/ogp-default.png (1200x630) — JSON-LD image / og:image 用
src/assets/images/logo.png (512x512) — JSON-LD publisher.logo 用
配色: ダークネイビー(#0F172A)×シアン(#22D3EE)、コンパス+サーキットノードのアイコン+「AI Tool Navigator」ワードマーク。
サイズ調整は macOS の sips を使用（ImageMagick不使用）。
これまで404だった assets/images/ogp-default.png / logo.png を解消。本番200確認済み。
C-2. og:image / twitter:image 追加 + Twitter Card large_image化（B-6 短期3 + B-3取りこぼし）完了
重大な取りこぼし発覚: _includes/base.njk に og:image / twitter:image メタタグがそもそも存在していなかった（B-3でJSON-LD側のみ実装、HTMLメタタグ側が未実装）。画像を置いてもSNS/LINE/Slack等でサムネが出ない状態だった。
_includes/base.njk を編集:
og:image 追加（ogpImage変数 or デフォルト画像URLのフォールバック付き）
twitter:card を summary → summary_large_image に変更
twitter:image 追加（同フォールバック）
注意: 当初の手編集で {{ }} を改行+全角スペース混入させてビルドエラー（expected variable end）。Python置換で1行化して解決。njkの {{ }} は改行不可・全角スペース厳禁。
commit fa8c57f。本番HTMLで3タグとも反映確認済み。
C-3. bak ファイル一括削除（B-6 短期4）完了
find . -name "*.bak*" -not -path "./node_modules/*" -delete で23個削除（補遺では26個想定、base.njk.bak先行削除と数え方の差）。
全て .gitignore(*.bak)で除外済みのGit管理外ファイルだったため、git status は clean。コミット不要。
_includes/base.njk.bak（過去に誤コミットされていた1個）は C-2作業中に削除済み（commit fa8c57f に含む）。
C-4. AdSense 申請準備 + 申請実行（B-6 短期2）
src/privacy.njk に「Google AdSense について」セクション追加（Google第三者Cookie使用 + adssettings.google.com / aboutads.info でのオプトアウト導線）。AdSense審査の定番必須記載に対応。commit 30ac49c。
src/about.njk は既存内容が審査要件を概ね満たしていたため変更なし。
AdSense申請を実行済み（2026-06-05 午前）。ただし注意点あり:
サイトが kaneko-ai.github.io/ai-tool-navigator/（GitHub Pages共有ドメイン・サブディレクトリ）のため、AdSense登録画面で「有効なTLDを指定してください」エラー。kaneko-ai.github.io で申請。
共有ドメイン(*.github.io)はAdSense審査で却下されやすい。 本気で収益化するなら独自ドメイン取得+GitHub Pagesカスタムドメイン設定が推奨。今回は「ダメ元で申請して評価を見る」方針。却下されたら記事増やして(目安40本)再申請。
ads.txt は承認後にパブリッシャーID発行されてから作成（現時点では作れない）。
審査用コードがAdSenseから案内されたら base.njk の <head> に貼る作業が別途必要。
C-5. time datetime ISO-8601化（B-6 短期8）完了
問題: _includes/post.njk の <time datetime="{{ date }}">{{ date }}</time> が Date.toString() 出力（Thu Jun 04 2026 00:00:00 GMT+0000 ...）になっていた。仕様違反 + UTC表記。
eleventy.config.js に luxon ベースのフィルタ2つ追加（Asia/Tokyo 固定）:
isoDate → yyyy-MM-dd（datetime属性用）
jpDate → yyyy年M月d日（表示用）
post.njk を <time datetime="{{ date | isoDate }}">{{ date | jpDate }}</time> に変更。
本番確認: <time datetime="2026-06-04">2026年6月4日</time>。commit 7d120b0。
一覧側（index.njk / articles.njk）は post.date.toISOString().slice(0,10) で既にISO形式・実害なしのため今回は未変更（任意の改善余地として残す）。
C-6. IndexNow（B-6 短期6）— 第1段階のみ完了
設計判断: 補遺B-6は「publish.pyに組み込む」想定だったが、publish.py実行時点ではまだデプロイ前でURLが実在しない（404空振りリスク）。通知はデプロイ完了後にGitHub Actions側で行うべきと判断。第2段階に回す。
第1段階（所有権証明・完了）:
キー生成: 55c9cc041af994b35488f082cf7ec8ec（openssl rand -hex 16）
src/55c9cc041af994b35488f082cf7ec8ec.txt（中身=キー）配置
eleventy.config.js に addPassthroughCopy("src/*.txt") 追加（src直下txtをルートへ）
commit edbae36。本番 https://kaneko-ai.github.io/ai-tool-navigator/55c9cc041af994b35488f082cf7ec8ec.txt が200・中身一致を確認。
注: 公開リポジトリ上にキーが露出するが、IndexNowキーは秘密情報でなく公開前提のため実害なし。
サブディレクトリ配置のため、第2段階の通知時は keyLocation を明示する必要あり。
C-7. Person/Author schema（B-6 短期5）— 確認の結果ほぼ完了済み
本番JSON-LD確認: author は既に @type: Person, name: "ai-tool-navigator 編集部", url: (aboutページ) を実装済み（B-3時点で実装されていた）。
追加強化（sameAs等）の余地はあるが、基本要件は満たしているため実質完了扱い。
C-8. 今日のコミット（6/5）
Copyedbae36 feat(seo): IndexNow キーファイル配置 + passthrough設定（第1段階・所有権証明）
7d120b0 fix(seo): <time>のdatetimeをISO-8601化、表示を和暦に
30ac49c feat(seo): プライバシーポリシーにGoogle AdSenseのCookie・オプトアウト記載を追加
fa8c57f feat(seo): OGPデフォルト画像・ロゴ追加 + og:image/twitter:image出力 + Twitter Card summary_large_image化
C-9. 残タスク（次回・ワークフロー編集が必要なため自動投稿後に実施）
IndexNow 第2段階（B-6 短期6の続き）: deploy成功後にIndexNow APIへ更新URLをPOST。keyLocation 明示必須。GitHub Actions（deploy.yml or daily-article.yml）への組み込み。
GitHub Actions retry logic（B-6 短期7）: nick-fields/retry@v3 でCopilot API呼び出し等をリトライ可能に。Stage 0タイムアウト/API一時エラー対策の本命。
AdSense 審査用コード貼付: AdSenseから案内され次第 base.njk の <head> に設置。
AdSense ads.txt: 承認・パブリッシャーID発行後に作成。
（任意）独自ドメイン取得 + GitHub Pagesカスタムドメイン設定（AdSense本格運用の前提）。
（任意）一覧ページの日付を <time>+和暦に統一。
補遺 C 追記: 2026-06-05 12:30 JST

以下が補遺Dの全文です。ダウンロードフォルダの `handover-v14.md` の末尾にそのまま貼り付けてください。

---

## 補遺 D: 2026-06-08〜09 Copilotクレジット枯渇とgrok手動記事生成への暫定移行

### D-1. 障害の経緯（2つの別問題）
6/5〜6/9にかけて記事自動生成が停止したが、原因は2系統あった。

1. **Stage 0 タイムアウト（6/5〜6/7）**: ローカルlaunchdのトレンド取得(x_search)が300秒タイムアウト。xAI側の一時的不調が原因。→ 補遺Cで対応済み（リトライ機構を実装、commit 872d21e）。
2. **GitHub Actions ステージ1〜4 の空応答（6/8〜）**: Stage 0復旧後も6/8記事が生成されず。draftの01〜04が全て0バイト、commit 6a99f88 で gate_fail=1・全ステージ model=unknown。

### D-2. 根本原因の特定
6/8の問題は認証エラーではなく **GitHub Copilot の月間AIクレジット枯渇**。
Copilot設定画面に「You've run out of your included AI credits for the month. Limit resets on Jul 1.」（200/200使用済み、リセットは7/1）と表示。
このため `copilot -p` が認証は通るが何も生成せず約3秒で即終了し、全ステージが空応答となった。COPILOT_PAT等のトークンは有効期限内で問題なし。

### D-3. 暫定対応：hermes(grok-4.3)による手動記事生成フロー
Copilotクレジットが7/1まで使えないため、Stage 0で実績のある hermes(grok-4.3) を記事生成にも転用する暫定フローを確立。

- **方式**: A案（半自動）。Stage 0でトレンド取得 → 人がトピックを1件選定 → grokで `04_final.md` を生成 → 人が確認 → publish.py で公開。
- **スクリプト化**: `scripts/generate_article.sh` を新規作成（commit de7a55e）。
  - 引数なし実行: Stage 0トレンド取得＋サマリ表示（トピック選定用、既存なら取得スキップ）。
  - 引数にトピック指定: grok-4.3で記事生成し、行数/H2数/CTA位置/末尾を自動チェック表示。
  - 公開(publish.py)は誤公開防止のため意図的に人手で実行する設計。
  - 調整: PROVIDER=xai-oauth, MODEL=grok-4.3。front-matterはプロンプト内に埋め込み。
- **注意点**: grok生成時の `-t web_search` はエラー（正しいツールセット名は未確定）。現状はweb検索なしで生成し、出典URLは手動確認する運用。出典付き生成が必要なら `-t web`（要検証）。

### D-4. 6/9 記事の初公開（暫定フローの実証）
本フローで初の記事を公開完了。

- トピック: 「副業初心者が信頼できる案件を見つける現実的な方法」（フリーランス/副業カテゴリ）。
- 生成: grok-4.3で約49秒、7,477バイト、H2×6、CTA×2。
- 公開: publish.py → eleventyビルド → push（commit 8c6868f）。本番反映済み（Deploy to GitHub Pages #133 緑）。
- OGP/Twitter Card確認済み（og:image=ogp-default.png, twitter:card=summary_large_image）。

### D-5. 日々の運用手順（7/1まで）

```
cd ~/ai-tool-navigator
./scripts/generate_article.sh                 # トレンド取得＋一覧表示
./scripts/generate_article.sh "カテゴリ: ... / テーマ: ..."   # 記事生成
# 内容確認後:
python3 scripts/publish.py <YYYY-MM-DD>
npx @11ty/eleventy
git add src/articles/<date>.md drafts/<date>/00_trends.json drafts/<date>/00_trends_summary.md drafts/<date>/04_final.md
git commit -m "feat(article): <date> 記事公開（hermes/grok手動生成）"
git push origin main
```

※ GitHub Actions の Daily Article Generation は7/1までクレジット枯渇で空振りし続ける。失敗通知が煩わしい場合は daily-article.yml の schedule を一時コメントアウトする選択肢あり（未実施）。

### D-6. 7/1以降の判断ポイント
- **クレジット復活後（7/1〜）**: 元のActions(copilot)フローに戻すか、grok手動フローを継続するか要判断。grokフローは安定・追加費用なしだが手動トピック選定の手間がある。
- **完全自動化の検討**: generate_article.shをlaunchdに登録すれば自走可能。ただしトピックの質を人が担保できる利点が失われるため、数日の手動運用で安定を確認してから判断する。
- **未着手**: IndexNow第2段階、Actions側リトライ（ステージ1〜4）、AdSense審査結果確認、記事数40本到達、OGP画像のリサイズ・配置（magickコマンド未検出で滞留中）。

---

*補遺 D 追記: 2026-06-09 15:50 JST*

---

