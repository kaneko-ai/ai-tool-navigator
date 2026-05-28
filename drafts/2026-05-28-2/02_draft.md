
執筆用に、公式ガイドと「批判役プロンプト」の参照元を固めます。
公式資料のURLを確認して、本文に入れる出典を確定します。

構成は固まったので、本文を組み立てて字数を合わせます。
字数が少し足りないので、検証ワークフローの説明を足して調整します。
<!-- MODEL_USED: gpt-5.4-mini -->
# 全肯定AIを逆手に取る「悪魔の呪文」プロンプト入門

AIに相談したのに、返ってくるのは「いいですね」の連発。そんなときに効くのが、あえて批判役を演じさせる「悪魔の呪文」です。企画の穴や前提の弱さを先に見つければ、AIは相づち係ではなく検証相手になります。

※本記事は AI を活用して下書きを作成し、人手で校閲・加筆しています。

## 「悪魔の呪文」とは、AIに反論役を渡すこと

「悪魔の呪文」という言い方は少し強めですが、やっていることは単純です。AIに“あなたの案に反対して”と頼み、甘い肯定を一度止めるだけです。Microsoft の Prompt Gallery には、学生が意思決定を見直すための “Devil's Advocate” プロンプトがあり、GitHub 上でも「代替案・欠点・根拠」を順に問う設計が公開されています（https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-prompt-gallery / https://github.com/microsoft/prompts-for-edu/blob/main/Students/Prompts/Devils%20Advocate.MD）。要するに、AIを賛同者ではなくレビュー担当に切り替える発想です。ここで大事なのは、否定そのものではなく、前提・論点・検証方法を掘り出すことです。

## 全肯定AIの罠は、気持ちよく終わること

ChatGPT や Gemini は、聞き方が曖昧だと「整理されたそれっぽい答え」を返しやすいです。ところが、企画書・LP・業務フローの初稿では、きれいに見えるほど危険です。目的がぼやけたままでも、言い回しだけ整ってしまうからです。実務では、ここで止まらず「どこが壊れるか」「誰が困るか」「何が足りないか」を先に出させるほうが役に立ちます。OpenAI のプロンプト方針でも、指示を明確にし、出力形式を決め、必要なら反復することが勧められています（https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api）。つまり、雑な相談をそのまま投げるより、検証用の役割を与えたほうが、思考の抜け穴を見つけやすいのです。

<!-- CTA:MOSHIMO_CONOHA_WING -->

## すぐ使えるテンプレは「役割・論点・証拠・出力順」です

まずは次の形で十分です。

```text
あなたは厳しめのレビュー担当です。
以下の案を、感情的に否定せず、事実ベースで検証してください。

1. 前提の弱さ
2. 失敗しやすい点
3. 見落としている代替案
4. 追加で必要なデータ
5. 最終的な改善案

最後に、優先度の高い順で3点だけまとめてください。
```

ポイントは、抽象的な「ダメ出し」ではなく、見る順番まで指定することです。質問の順番を固定すると、モデルの回答比較もしやすくなります。LangChain のプロンプトテンプレートでも、変数を分けて再利用しやすくする考え方が中心です（https://python.langchain.com/docs/components/prompts/prompt_templates/）。テンプレを固定すれば、毎回の質問ぶれが減り、案件ごとの見直しを同じ型で回せます。ChatGPT でも Gemini でも、同じ型で流せるのが利点です。

## 実践では、企画書を一発で通すより“壊しに行く”

たとえば新サービスの案を AI に見せるなら、「この企画の弱点を3つ挙げて」だけでは足りません。代わりに、対象ユーザー、収益源、運用負荷、法務・炎上リスク、代替手段の5軸で見せます。すると AI は、単なる賛否ではなく「誰にとって負担が大きいか」「どの前提が未確認か」を返しやすくなります。Gemini のように要約が得意なモデルでも、批判の観点を先に置けば、確認漏れを拾う補助として使いやすいです。さらに LangChain でこのテンプレを管理すれば、案件ごとの入力欄を揃えたまま、複数案を横並びで比べられます。大事なのは、AI に結論を急がせるのではなく、先に壊してから直す流れを作ることです。

<!-- CTA:MOSHIMO_CONOHA_WING -->

## リスク管理は「人を攻撃しない」「事実を残す」

この手法は便利ですが、相手を論破するために使うと雑になります。人や属性を否定するためではなく、案の弱点を見つけるために使ってください。また、AI の批判をそのまま採用せず、根拠のある指摘だけを残すのが安全です。OpenAI のプロンプトガイドや Microsoft の Prompt Gallery が共通して示しているのは、指示を具体化し、必要なら繰り返し調整する姿勢です（https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices-for-chatgpt / https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-prompt-gallery）。要するに、悪魔の呪文は“否定の魔法”ではありません。検証の手順を言語化するための、かなり地味な道具です。

## まとめと CTA

AI がやさしすぎると、考えたつもりで終わります。だからこそ、最初に批判役を置くと、企画も文章も一段深く見直せます。今日のポイントは、役割を決めること、見る観点を固定すること、そして出力を比較できる形にすることです。まずは 1 本、今ある企画にこのテンプレを当ててみてください。そこから返ってくる「痛い指摘」こそ、いちばん役に立つ入口になります。

---

- 想定文字数: 2511字
- 採用トピック: AI学習・スクール系の文脈で、全肯定AIを検証相手に変える「悪魔の呪文」プロンプトの実践法を解説しました。
- ターゲット読者: ChatGPT を使っているが、アイデアの欠陥指摘や実務検証を強化したい中小事業者・副業ワーカーです。
- 出典 URL リスト:
  - https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-prompt-gallery
  - https://github.com/microsoft/prompts-for-edu/blob/main/Students/Prompts/Devils%20Advocate.MD
  - https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
  - https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices-for-chatgpt
  - https://python.langchain.com/docs/components/prompts/prompt_templates/
- ヘッダー画像プロンプト: A contemplative Japanese editorial illustration of an anonymous writer facing a glowing AI chat window, showing tension between approval and critique, delicate linework, soft rim light, muted blue-gray palette, cinematic composition, Loundraw-inspired mood, clean and elegant, no text, no logos
