# publish自動化 設計書

## 目的

GitHub Actions 4段パイプラインで生成された `drafts/<date>/04_final.md` を、quality gate を通過した場合に自動で `src/articles/<date>-<slug>.md` として公開する。

## 設計方針

- 完全自動publish（人手承認なし、ロールバックは退避コマンドで対応）
- gate_fail=0 かつ review_helper exit ≤ 1 を満たすときのみ実行
- slugはAIがStage4で生成、ファイル名は `<date>-<slug>.md`

## front-matter変換ルール

1. 冒頭の空行・独白を除去（最初の `---` までスキップ）
2. `editor_reviewed: false` → `editor_reviewed: true`
3. 末尾の自動チェック結果ブロックを削除
4. `<!-- MODEL_USED: ... -->` コメントは保持
5. front-matter終端の改行保証
6. 文末の句点・記号チェック

## 実装ステップ

### Step 1: Stage4プロンプト拡張
`prompts/04_polish.md` の front-matter仕様に `slug` キーを追加。

### Step 2: scripts/publish.py 作成
front-matter変換と src/articles/ への配置を行うPythonスクリプト。約100行。

### Step 3: workflow に publish ステップ追加
quality gate 通過後に `python3 scripts/publish.py` を呼ぶ。約15行。

### Step 4: ローカルテスト
既存の drafts/2026-05-13/04_final.md でドライランしてから本番投入。

## slugフォールバック

- slug無し → `<date>.md`
- 同名重複 → `<date>-<slug>-2.md`

## 撤回フロー

\`\`\`bash
mv src/articles/<file>.md drafts/withdrawn/articles/<date>-<reason>.md
git add -A && git commit -m "withdraw: <reason>" && git push
\`\`\`

## 実装着手予定

Day20朝（Run #9 結果確認後）。
