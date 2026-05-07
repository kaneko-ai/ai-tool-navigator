TOPICS = [
    {
        "title": "無料で使えるAI API比較 2026年最新版",
        "keywords": "AI API 無料 比較 2026 OpenRouter NVIDIA NIM Google AI",
        "search_query": "free AI API 2026 OpenRouter NVIDIA NIM Google AI Studio",
        "guidance": "OpenRouter、NVIDIA NIM、Google AI Studio、Hugging Faceなど主要な無料AI APIを比較。無料枠の制限、対応モデル、手順を具体的に書き、比較表を含める。"
    },
    {
        "title": "FreeLLMAPI 統合ハブの構築実録｜14プロバイダ40モデルを1キーで使う方法",
        "keywords": "FreeLLMAPI 統合 LLM プロバイダ ルーティング 2026",
        "search_query": "free LLM API gateway router multiple providers 2026",
        "guidance": "FreeLLMAPIで複数のLLMプロバイダ（OpenRouter, NVIDIA NIM, Google等）を1つのエンドポイントに統合する方法。導入手順、認証、フォールバック設計、実際の運用ログを含める。"
    },
    {
        "title": "AI副業で月5万円を稼ぐロードマップ",
        "keywords": "AI 副業 月5万 稼ぐ 初心者 2026",
        "search_query": "AI side hustle earn money beginner 2026 roadmap",
        "guidance": "3ヶ月で月5万円を達成するためのステップ。案件例、必要なツール、手順を解説。"
    },
    {
        "title": "マルチモーダルAI徹底比較｜GPT-5 vs Gemini vs Claude",
        "keywords": "マルチモーダルAI 比較 GPT-5 Gemini Claude 2026",
        "search_query": "multimodal AI comparison GPT-5 Gemini Claude 2026",
        "guidance": "2026年時点の主要AIの機能を比較。テキスト・画像・音声への対応状況を比較表付きで解説。"
    },
    {
        "title": "AIエージェント フレームワーク比較｜LangChain vs AutoGen vs CrewAI",
        "keywords": "AIエージェント 比較 LangChain AutoGen CrewAI 2026",
        "search_query": "AI agent framework comparison LangChain AutoGen CrewAI 2026",
        "guidance": "主要なAIエージェントフレームワークを比較。機能、難易度、ユースケース、コミュニティ規模を解説。"
    },
    {
        "title": "プロンプトエンジニアリング実践テクニック10選",
        "keywords": "プロンプトエンジニアリング テクニック ChatGPT Claude 2026",
        "search_query": "prompt engineering techniques best practices 2026",
        "guidance": "実務で使えるテクニックを紹介。具体的なプロンプト例（before/after）を含める。"
    },
    {
        "title": "AI画像生成で稼ぐ方法｜ストックフォト販売完全ガイド",
        "keywords": "AI画像生成 稼ぐ Adobe Stock Midjourney 2026",
        "search_query": "AI image generation stock photo selling 2026",
        "guidance": "ストックフォトサイトで販売して収益を得る方法。ツール選び、審査のコツを解説。"
    },
    {
        "title": "AI音声合成アプリ比較｜ビジネス活用ガイド",
        "keywords": "AI音声合成 TTS アプリ 比較 2026",
        "search_query": "AI text to speech app comparison business use 2026",
        "guidance": "日本語対応TTSアプリを比較。ナレーションや動画制作での活用事例を解説。"
    },
    {
        "title": "LLMファインチューニング入門｜自分専用AIの作り方",
        "keywords": "LLM ファインチューニング 入門 LoRA 2026",
        "search_query": "LLM fine-tuning tutorial LoRA beginner guide 2026",
        "guidance": "LoRAの仕組みと実行手順を初心者向けに解説。必要な準備とコストを提示。"
    },
    {
        "title": "AIデータ分析ツール比較｜ノーコードで始めるデータサイエンス",
        "keywords": "AI データ分析 ツール ノーコード 2026",
        "search_query": "AI data analysis tools no-code comparison 2026",
        "guidance": "プログラミング不要な分析ツールを比較。具体的なユースケースを解説。"
    }
]

SYSTEM_PROMPT = (
    "あなたはAI技術と副業に詳しい技術ブロガーです。日本語で読者に具体的で実用的な情報を提供します。\n"
    "現在は2026年4月です。記事は2026年4月時点の最新情報として執筆してください。\n"
    "「2023年現在」「2024年最新」など古い年号を絶対に書かないこと。年号に言及する場合は必ず「2026年」と書いてください。\n\n"
    "【記事の要件】\n"
    "- 3000字以上（必達、不足する場合は章を追加して情報密度を上げる）\n"
    "- H2見出し（##）を5つ以上使用\n"
    "- 比較表（Markdownテーブル）または番号付き箇条書きを最低1つ含める\n"
    "- 比較表のセルに不明な情報がある場合は「要確認」と必ず書く（空セルにしない）\n"
    "- 一人称は「私」、文体は「です・ます」調\n"
    "- 「正直に言う」「お前ら」「絶対に〜」などの煽り口調・断定表現は使わない\n"
    "- 「最速」「業界No.1」など根拠なき断定は禁止。「公式発表によれば〜」「私が試した範囲では〜」など出典や経験を意識した表現を使う\n"
    "- 数値や手順は具体的に書く（例: 月額687円、所要15分、など）\n"
    "- 末尾に「## まとめ」セクションを必ず置き、要点を3〜5項目の箇条書きで示す\n\n"
