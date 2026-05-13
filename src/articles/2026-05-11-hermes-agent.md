---
layout: post.njk
title: "Hermes Agent 完全セットアップガイド"
date: 2026-05-11
description: "Hermes Agent 完全セットアップガイドの最新情報と活用ガイド。"
ai_generated: true
tags: ["agent", "tutorial"]
---

# Hermes Agent 完全セットアップガイド：Discord自動化の未来を今、手にする

皆さん、こんにちは！AIツール専門ブロガー「Navigator X」です。

現代社会において、AI技術の進化は私たちの働き方、生き方に革命をもたらしています。特に、ルーティンワークの自動化や情報処理の高速化は、生産性向上と創造性解放の鍵となります。今回ご紹介するのは、Discordをインターフェースとして強力なAIエージェントを稼働させる「Hermes Agent」です。

Hermes Agentは、自然言語での指示に基づき、様々なタスクを自動実行できる画期的なツールです。Discordと連携することで、チームコラボレーションのハブとして、あるいは個人的なアシスタントとして、その真価を発揮します。情報検索、コンテンツ生成、データ分析支援など、多岐にわたる機能をAIが24時間365日サポートしてくれるのです。

この記事では、Hermes Agentをゼロからセットアップし、安定して自動起動させるまでの完全な手順を、具体的なコマンド例や設定ファイルの記述例を交えながら徹底解説します。初心者の方でも安心して導入できるよう、一つ一つのステップを丁寧に追っていきましょう。

## 1. はじめに：Hermes Agentとは何か、なぜ今導入すべきなのか

Hermes Agentは、OpenAIの強力な言語モデルをDiscord環境に統合し、ユーザーの指示に応じて様々な自動化タスクを実行するAIエージェントです。その名の通り、ギリシャ神話のヘルメスのように、情報伝達とタスク実行の使者として機能します。

**Hermes Agentの主要な特徴:**

*   **Discord連携:** 最も日常的に利用されるコミュニケーションプラットフォームの一つであるDiscordを操作インターフェースとすることで、直感的かつ手軽にAIエージェントと対話できます。
*   **高度なタスク自動化:** ウェブ検索、画像生成、コード生成など、プラグインを通じて多様なタスクを実行できます。これにより、単なるチャットボットを超えた実用的なアシスタントとして機能します。
*   **24時間365日稼働:** サーバー上で稼働させることで、常にあなたの指示を待ち、必要な時にタスクを実行します。
*   **カスタマイズ性:** `config.yaml`ファイルを編集することで、使用するAIモデル、プロンプト、有効にするプラグインなどを細かく調整できます。

**Hermes Agentを今すぐ導入すべき理由:**

1.  **生産性の飛躍的向上:** 定型的な情報収集、報告書のドラフト作成、アイデア出しなど、時間のかかる作業をAIに任せることで、あなたはより重要な意思決定や創造的な活動に集中できます。
2.  **情報アクセスの高速化:** 必要な情報を瞬時に検索・要約し、Discord上で提供してくれるため、調査にかかる時間を大幅に短縮できます。
3.  **チームコラボレーションの強化:** チームメンバー全員がAIアシスタントを活用することで、情報共有がスムーズになり、プロジェクトの進行が加速します。
4.  **コスト効率の改善:** 人手による作業をAIが代替することで、長期的に見て運用コストの削減に繋がる可能性があります。

この記事を読み終える頃には、あなたはHermes Agentを完全にセットアップし、自身のDiscordサーバーで稼働させ、その無限の可能性を探求できるようになっているでしょう。

## 2. ステップ1：環境準備と依存関係のインストール

Hermes Agentを稼働させるには、いくつかの基本的な環境構築が必要です。ここでは、Pythonの準備から必要なライブラリのインストールまでを解説します。

### 2.1. 必要なものリスト

*   **Python 3.9以上:** PythonはHermes Agentの基盤言語です。推奨バージョンは3.10または3.11です。
*   **Git:** Hermes Agentのリポジトリをクローンするために使用します。
*   **安定したインターネット接続:** OpenAI APIやDiscord APIとの通信に必要です。
*   **OpenAI APIキー:** AIモデルを利用するための認証キーです。
*   **Discordアカウントとサーバー:** Botを稼働させるための環境です。

### 2.2. Pythonの準備

Pythonがインストールされていない、または古いバージョンの場合は、最新版をインストールしてください。複数のPythonプロジェクトを管理する場合、`pyenv` (macOS/Linux) や `Anaconda`/`Miniconda` (全OS) のようなバージョン管理ツールを使うことを強くお勧めします。

**pyenvを使ったPythonのインストール例 (macOS/Linux):**

```bash
# pyenvのインストール (Homebrewの場合)
brew install pyenv

# 利用可能なPythonバージョンを確認
pyenv install --list

# Python 3.11.8をインストール
pyenv install 3.11.8

# このプロジェクトでPython 3.11.8を使用するよう設定
pyenv local 3.11.8

# グローバルに設定する場合は
# pyenv global 3.11.8
```

Windowsの場合は、Python公式サイトからインストーラーをダウンロードし、「Add Python to PATH」にチェックを入れてインストールしてください。

### 2.3. 仮想環境の作成とアクティベート

プロジェクトごとにPythonの依存関係を分離するために、仮想環境（Virtual Environment）の利用は必須です。

```bash
# プロジェクトディレクトリを作成し、移動
mkdir hermes-agent
cd hermes-agent

# 仮想環境を作成 (hermes_envという名前で)
python -m venv hermes_env

# 仮想環境をアクティベート
# Linux/macOSの場合:
source hermes_env/bin/activate

# Windowsの場合:
.\hermes_env\Scripts\activate
```
仮想環境がアクティベートされると、ターミナルのプロンプトの前に `(hermes_env)` のような表示が追加されます。

### 2.4. Hermes Agentのリポジトリクローンと依存パッケージのインストール

次に、Hermes AgentのソースコードをGitHubからクローンし、必要なPythonライブラリをインストールします。

```bash
# Hermes Agentのリポジトリをクローン
git clone https://github.com/your-repo/hermes-agent.git . # . をつけると現在のディレクトリにクローン

# クローンしたディレクトリに移動 (既にhermes-agentディレクトリ内にいる場合は不要)
# cd hermes-agent

# 依存パッケージをインストール
pip install -r requirements.txt
```
この`requirements.txt`には、`discord.py`、`openai`、`PyYAML`など、Hermes Agentが動作するために必要な全てのライブラリが記述されています。

## 3. ステップ2：APIキーと設定ファイルの準備

Hermes Agentを機能させるには、OpenAIのAPIキーとDiscord Botのトークンが必要です。これらを`config.yaml`ファイルに設定します。

### 3.1. OpenAI APIキーの取得

1.  **OpenAIアカウントの作成:** [https://platform.openai.com/](https://platform.openai.com/) にアクセスし、アカウントを作成またはログインします。
2.  **APIキーの発行:** ダッシュボードの左側メニューから「API keys」を選択し、「Create new secret key」をクリックします。生成されたキーは**一度しか表示されない**ため、必ずコピーして安全な場所に保管してください。`sk-`で始まる文字列です。

### 3.2. Discord Botの作成とトークンの取得

Hermes AgentをDiscordで稼働させるには、専用のBotを作成し、そのトークンを取得する必要があります。

1.  **Discord Developer Portalにアクセス:** [https://discord.com/developers/applications](https://discord.com/developers/applications) にアクセスし、ログインします。
2.  **新しいアプリケーションの作成:** 「New Application」をクリックし、Botの名前（例: Hermes Agent）を入力して作成します。
3.  **Botの追加:** 作成したアプリケーションのページで、左側メニューの「Bot」タブを選択し、「Add Bot」→「Yes, Do It!」をクリックします。
4.  **トークンの取得:** 「Token」セクションにある「Reset Token」をクリックし、表示されたトークンをコピーします。**このトークンはBotの「パスワード」に相当するため、絶対に他人に教えたり、公開リポジトリにアップロードしたりしないでください。**
5.  **権限設定（最重要）:**
    *   同じ「Bot」タブ内で、「**Privileged Gateway Intents**」セクションを見つけます。
    *   「**Message Content Intent**」を**必ず有効化**してください。これを有効にしないと、Botはユーザーのメッセージ内容を読み取ることができず、ほとんどの機能が動作しません。
6.  **Botをサーバーに招待:**
    *   左側メニューの「OAuth2」→「URL Generator」を選択します。
    *   「SCOPES」で`bot`にチェックを入れます。
    *   「BOT PERMISSIONS」で、`Send Messages`, `Read Message History`, `Embed Links`など、Botに必要な権限にチェックを入れます。最低限、メッセージを送信・受信できる権限が必要です。
    *   生成されたURLをコピーし、ウェブブラウザで開きます。Botを招待したいサーバーを選択し、「認証」をクリックします。

### 3.3. `config.yaml`の記述例と解説

Hermes Agentの設定は、プロジェクトルートにある`config.yaml`ファイルで行います。`config.example.yaml`をコピーして`config.yaml`を作成し、編集してください。

```yaml
# config.yaml (記述例)
# ==============================================================================
# 必須設定: APIキーとトークン
# ==============================================================================
openai_api_key: "sk-YOUR_OPENAI_API_KEY_HERE" # ここに取得したOpenAI APIキーを記述
discord_bot_token: "YOUR_DISCORD_BOT_TOKEN_HERE" # ここに取得したDiscord Botトークンを記述

# ==============================================================================
# Discord Bot 設定
# ==============================================================================
discord:
  # 管理者として許可するDiscordユーザーID。Botの全機能にアクセスできます。
  # 自身のDiscordユーザーIDをコピーして設定してください。
  # (Discord開発者モードを有効にし、自分のユーザー名を右クリックで「IDをコピー」)
  admin_user_id: "123456789012345678" # 例: 自身のDiscordユーザーID

  # Botが監視する特定のチャンネルID。指定しない場合は、Botがアクセスできる全てのチャンネルで動作します。
  # 特定のチャンネルに限定する場合に設定してください。
  # (Discord開発者モードを有効にし、チャンネル名を右クリックで「IDをコピー」)
  # channel_id: "987654321098765432" # オプション: 特定のチャンネルID

  # コマンドプレフィックス。Botに話しかける際に使用します。
  prefix: "!" # 例: !ask, !search

# ==============================================================================
# OpenAI モデル設定
# ==============================================================================
openai:
  # 使用するAIモデル名。gpt-4oが推奨されますが、コストと速度を考慮して選択してください。
  # gpt-4o, gpt-3.5-turbo など。
  model_name: "gpt-4o"

  # 応答のランダム性 (0.0-2.0)。
  # 高い値ほど創造的で多様な応答、低い値ほど予測可能で集中的な応答になります。
  temperature: 0.7

  # 生成される応答の最大トークン数。
  # 長すぎるとコストが増え、短すぎると情報が不足する可能性があります。
  max_tokens: 1024

  # AIエージェントの役割、振る舞い、制約を定義するシステムプロンプト。
  # ここでAIのパーソナリティと基本的なルールを設定します。
  system_prompt: |
    You are Hermes, a helpful AI assistant connected to Discord.
    Your goal is to assist users by answering questions, providing information, and executing tasks using the available tools.
    You should always be polite, concise, and accurate.

    # Important Rules:
    # 1. Always indicate when you are using a tool by mentioning the tool name.
    # 2. If a tool fails, explain why and suggest an alternative or a retry.
    # 3. Prioritize factual accuracy when answering questions.
    # 4. Do not make up information. If you don't know, state that.
    # 5. Respond in Japanese when the user asks in Japanese, and in English when the user asks in English.

# ==============================================================================
# プラグイン (ツール) 設定
# ==============================================================================
plugins:
  # ウェブ検索プラグイン
  web_search:
    enabled: true # ウェブ検索を有効にするか (true/false)
    # より良い検索結果のためにSerper APIを使用する場合、ここにキーを記述
    # serper_api_key: "YOUR_SERPER_API_KEY_HERE" # オプション

  # 画像生成プラグイン
  image_generation:
    enabled: true # 画像生成を有効にするか (true/false)
    model: "dall-e-3" # dall-e-2 または dall-e-3 を選択

  # その他のプラグイン (必要に応じて追加)
  # file_io:
  #   enabled: false
  # ...
```
**`admin_user_id`と`channel_id`の取得方法:**
Discordアプリで「ユーザー設定」→「詳細設定」→「開発者モード」を有効にします。
*   **ユーザーID:** 自分のユーザー名を右クリックし、「IDをコピー」を選択します。
*   **チャンネルID:** 対象のチャンネル名を右クリックし、「IDをコピー」を選択します。

### 3.4. 比較表：主要なAIモデル設定パラメータとその影響

`config.yaml`で設定するAIモデルのパラメータは、Hermes Agentの応答に大きく影響します。以下の表で、主要なパラメータとその特性を理解しましょう。

| パラメータ名       | 範囲         | 説明                                                                                                 | 影響                                                                                                                               | 推奨値 (初期) |
| :----------------- | :----------- | :--------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- | :------------ |
| `openai.model_name`| モデル名     | 使用するOpenAIモデルの識別子 (例: `gpt-4o`, `gpt-3.5-turbo`)                                         | **性能とコストに直結。** `gpt-4o`は最も高性能で複雑なタスクに適するが、高コスト。`gpt-3.5-turbo`は低コストで高速、汎用タスク向け。 | `gpt-4o`      |
| `openai.temperature`| 0.0 - 2.0    | 応答のランダム性、創造性を示す数値。高いほど多様な、低いほど集中的な応答になる。                       | **高い値:** より創造的で多様な、予測しにくい応答。ブレインストーミングやアイデア生成に。**低い値:** より予測可能で集中的な、事実に基づいた応答。情報検索や要約に。 | 0.7           |
| `openai.max_tokens` | 1 - 4096 (モデルによる) | 生成される応答の最大トークン数。1トークンは約0.75単語に相当。                                        | 応答の長さを制限。長すぎるとコストが増大し、不必要な情報が含まれる可能性。短すぎると情報が不足する可能性。                         | 1024          |
| `openai.system_prompt`| テキスト     | AIエージェントの役割、振る舞い、制約を定義する指示。AIの「性格」を設定する。                           | AIのパーソナリティと性能の基盤。詳細かつ明確な指示を与えることで、期待通りの応答を引き出しやすくなる。                         | カスタマイズ  |

これらのパラメータを調整することで、Hermes Agentをあなたのニーズに合わせて最適化できます。

## 4. ステップ3：Hermes Agentの初回起動と動作確認

設定ファイルが準備できたら、いよいよHermes Agentを起動し、Discord上で動作を確認しましょう。

### 4.1. 起動コマンド

仮想環境がアクティブな状態で、Hermes Agentのルートディレクトリから`main.py`スクリプトを実行します。

```bash
# 仮想環境がアクティブであることを確認 (プロンプトに (hermes_env) が表示されているか)
(hermes_env) python main.py
```
起動に成功すると、ターミナルにBotがDiscordにログインしたことを示すメッセージが表示され、Botがオンラインになります。

### 4.2. Discordでの動作確認

1.  **Botのオンライン状態を確認:** Discordサーバーで、あなたのBotがオンライン（緑色の丸アイコン）になっていることを確認します。
2.  **簡単なコマンドを送信:** `config.yaml`で設定した`prefix`（デフォルトは`!`）を使って、Botが参加しているチャンネル（または`channel_id`で指定したチャンネル）にメッセージを送信します。

    *   **Pingテスト:**
        ```
        !ping
        ```
        Botが「Pong!」と応答すれば、Discordとの接続は正常です。

    *   **基本的な質問:**
        ```
        !ask What is the capital of Japan?
        ```
        Botが「The capital of Japan is Tokyo.」のように応答すれば、OpenAI APIとの連携も正常です。

    *   **プラグインの動作確認 (ウェブ検索):**
        ```
        !search current weather in Tokyo
        ```
        Botがウェブ検索ツールを使用して、現在の東京の天気情報を返せば、プラグインも正常に機能しています。

    *   **プラグインの動作確認 (画像生成):**
        ```
        !imagine a futuristic city at sunset
        ```
        BotがDALL-Eを使って画像を生成し、Discordに投稿すれば、画像生成プラグインも正常です。

### 4.3. トラブルシューティングのヒント

もしBotが期待通りに動作しない場合は、以下の点を確認してください。

*   **ターミナルのログ:** `python main.py`を実行しているターミナルにエラーメッセージが表示されていないか確認します。エラーメッセージは問題解決の重要な手がかりです。
*   **`config.yaml`の再確認:**
    *   `openai_api_key`と`discord_bot_token`が正しく、かつダブルクォーテーションで囲まれているか。
    *   `admin_user_id`と`channel_id`が正しいDiscord IDであるか。
    *   `discord.prefix`が意図したプレフィックスになっているか。
*   **Discord Botの権限:**
    *   Discord Developer Portalで、Botの「Message Content Intent」が有効になっているか。
    *   Botがサーバーに招待されており、必要な権限（`Send Messages`、`Read Message History`など）が付与されているか。
    *   Botが参加しているチャンネルで、Botにメッセージ送信権限があるか。
*   **インターネット接続:** サーバーが安定してインターネットに接続されているか確認します。
*   **仮想環境:** 必ず仮想環境がアクティベートされた状態でスクリプトを実行しているか確認します。

## 5. ステップ4：永続的な運用と自動起動の設定

Hermes Agentを常に稼働させ、サーバー再起動時にも自動的に起動するように設定することで、永続的な運用が可能になります。

### 5.1. バックグラウンド実行 (`screen`または`tmux`)

SSHセッションを切断してもBotが稼働し続けるように、`screen`や`tmux`といったターミナルマルチプレクサを使用できます。

**`screen`の基本的な使い方 (Linux/macOS):**

1.  `screen`コマンドを実行して新しいセッションを開始します。
    ```bash
    screen
    ```
2.  セッション内でHermes Agentを起動します。
    ```bash
    (hermes_env) python main.py
    ```
3.  `Ctrl+A`の後に`D`


---

## AIブログを始めるなら

AIツールの知識を活かしてブログで発信してみませんか？当サイトも使用している**ConoHa WING**なら、月額687円〜で高速サーバーが使えます。

[ConoHa WINGでブログを始める](//af.moshimo.com/af/c/click?a_id=5506692&p_id=2312&pc_id=4967&pl_id=38395)

*※上記リンクはアフィリエイトリンクです。*

