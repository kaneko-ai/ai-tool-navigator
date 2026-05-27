# handover-v13 補遺（2026-05-27 夜時点）

## Day24 で Stage 0 実装まで完了

### 実装済み
- `scripts/stage0_trend_fetch.py` (229行、commit cba57ca)
- Hermes Agent v0.13.0 + xai-oauth provider で X Premium OAuth 認証成功
- x_search ツール有効化
- ローカル動作確認：3回連続で 6件 valid trends を JSON 取得
- `drafts/2026-05-27/00_trends.json` を初コミット

### 課金確認
- X Premium ¥980/月のクォータ内で動作
- API spend 発生なし（OAuth bearer token 経由）
- 1日1回呼び出しで月コスト ¥0

### 残課題（v14 で扱う）
1. CI/launchd 統合方針の確定（選択肢A/B/C のうち A→C 推奨）
2. Stage 1 プロンプトに 00_trends_summary.md を読み込ませる改修
3. retry logic 導入（v13 #24）
4. Phase A 連続稼働の検証（5/28 以降）
5. Hermes Desktop インストール判断（任意）

### 重要メモ
- `~/.hermes/auth.json` に xai-oauth トークン保存済（自動 refresh される）
- `hermes auth status xai-oauth` で `logged in` 確認可能
- `hermes -z "..." --provider xai-oauth -m grok-4.3 -t x_search` が動作確認済の呼び出し方
- `--provider` を指定する場合は **必ず `-m` も併記** が必要（hermes の仕様）
