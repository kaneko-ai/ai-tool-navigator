#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
daily_article_generator.py
ai-tool-navigator 日次記事自動生成スクリプト

3段フォールバック:
  1. FreeLLMAPI (localhost:3001)
  2. Google Gemini API direct
  3. NVIDIA NIM direct

依存: 標準ライブラリのみ (Python 3.9+)
"""

import os
import re
import json
import time
import datetime
import subprocess
import urllib.request
import urllib.error
from datetime import timezone


# ============================================================
# 設定
# ============================================================
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(REPO_DIR, "src/articles")
ENV_FILE = os.path.expanduser("~/ai-blog-config/.env")

AFFILIATE_CTA = """
---

## AIブログを始めるなら

AIツールの知識を活かしてブログで発信してみませんか？当サイトも使用している**ConoHa WING**なら、月額687円〜で高速サーバーが使えます。

[ConoHa WINGでブログを始める](//af.moshimo.com/af/c/click?a_id=5506692&p_id=2312&pc_id=4967&pl_id=38395)

*※上記リンクはアフィリエイトリンクです。*
"""

TOPICS = [
    # ===== 軸1: AI学習・スクール系（10トピック） =====
    {
        "title": "【2026年最新】AIスクール補助金完全ガイド｜最大70%OFFで受講できる8校",
        "keywords": "AIスクール 補助金 リスキリング 給付金 2026",
        "search_query": "AIスクール 補助金 教育訓練給付金 2026",
        "guidance": "経産省リスキリング補助金（最大70%・56万円）、教育訓練給付金（最大80%OFF）の適用条件を整理。主要AIスクール8校の補助金適用可否を比較表化。受給フロー（申請→受講→還付）も解説。CTA候補: メイカラ、AIビジネス活用講座、Neuro Dive。"
    },
    {
        "title": "生成AIスクールおすすめ7校徹底比較2026｜DMM・SAMURAI・デジハクと中堅校の違い",
        "keywords": "生成AIスクール おすすめ 比較 2026 社会人",
        "search_query": "生成AIスクール おすすめ 比較 社会人",
        "guidance": "DMM生成AI CAMP（月14,800円リニューアル）、デジハク、SAMURAI ENGINEER等の大手と、メイカラ・AIビジネス活用講座等の中堅校を料金/期間/サポート/補助金対応の4軸で比較。「大手 vs 中堅」の選び方フレームを提示。比較表必須。CTA候補: メイカラ、AIビジネス活用講座。"
    },
    {
        "title": "未経験からAIエンジニア転職｜2026年版ロードマップと現実的な学習期間",
        "keywords": "AIエンジニア 未経験 転職 ロードマップ 2026",
        "search_query": "AIエンジニア 未経験 転職 ロードマップ",
        "guidance": "Python基礎→機械学習→深層学習→ポートフォリオの4段階。各段階の学習時間目安（合計600〜1000時間）。求人ボックス調べAIエンジニア平均年収595万円、シニア600〜900万円のデータ引用。Neuro Dive、Python Winnerをスクール選択肢として紹介。CTA候補: Neuro Dive、Python Winner。"
    },
    {
        "title": "Pythonスクールおすすめ5校2026｜独学挫折者が選ぶべき条件",
        "keywords": "Python スクール おすすめ 未経験 挫折",
        "search_query": "Python スクール 比較 未経験 挫折",
        "guidance": "独学挫折の典型3パターン（環境構築、エラー対応、モチベ維持）を提示し、それを解決するスクール選びの基準を解説。RUNTEQ、Dpro等と比較しつつPython Winnerを推薦。CTA候補: Python Winner。"
    },
    {
        "title": "G検定・E資格の難易度と勉強時間2026｜独学 vs スクールどちらが効率的？",
        "keywords": "G検定 E資格 難易度 勉強時間 2026",
        "search_query": "G検定 E資格 違い 難易度 勉強時間",
        "guidance": "G検定（15〜70時間、独学可能）、E資格（100〜200時間+JDLA認定講座必須）の違いを表で解説。E資格はJDLA認定講座必須のため、対応スクール（Neuro Dive、AIビジネス活用講座のJDLA対応コース等）への誘導が自然。CTA候補: Neuro Dive、AIビジネス活用講座。"
    },
    {
        "title": "2026年AI副業のリアル｜ノーコードAIで月5万円は可能か？案件単価の実勢データ",
        "keywords": "AI 副業 月5万 ノーコード 案件単価 2026",
        "search_query": "AI 副業 始め方 単価 ノーコード",
        "guidance": "コエテコ調査『生成AI案件は他案件比1.8倍』、侍エンジニア『ノーコード案件平均5〜30万円』の実勢データを引用。月5万円達成の現実的なルートを提示し、『誰でも稼げる』表現は避ける。スキル習得段階でメイカラ・Python Winnerに誘導。CTA候補: メイカラ、Python Winner。"
    },
    {
        "title": "ChatGPT業務活用の学習ロードマップ｜プロンプトエンジニアリングから業務自動化まで",
        "keywords": "ChatGPT 業務活用 プロンプトエンジニアリング 学習",
        "search_query": "ChatGPT 仕事 使い方 学習 プロンプト",
        "guidance": "3段階構成（プロンプト基礎→業務適用→自動化）。法人導入の失敗5パターン（目的不在、現場不在、全社一斉、効果測定ゼロ、セキュリティ後回し）を反面教師として活用。AIビジネス活用講座を実務寄り学習として紹介。CTA候補: AIビジネス活用講座。"
    },
    {
        "title": "データサイエンティスト需要は本当に高い？2026年の年収・キャリアパスを実データで検証",
        "keywords": "データサイエンティスト 需要 2026 年収 キャリア",
        "search_query": "データサイエンティスト 将来性 年収",
        "guidance": "Renue『年収400〜1,800万円』、Levtech『人材不足が継続』等のデータを整理。生成AI時代に役割がどう変化するか（単なる分析→『問いを立てる人材』へ）を解説。Neuro Dive、メイカラを学習選択肢として紹介。CTA候補: Neuro Dive、メイカラ。"
    },
    {
        "title": "文系出身でもAIエンジニアになれる？数学が苦手な人の学習順序",
        "keywords": "文系 AIエンジニア 数学 苦手 学習",
        "search_query": "文系 AIエンジニア 数学",
        "guidance": "線形代数→微積分→確率統計の必要レベルを『文系でも追いつける』基準で解説。実例（文系出身AIエンジニア体験談の引用）。スクールでの学習が独学より効率的な理由を提示。CTA候補: AI CONNECT、メイカラ。"
    },
    {
        "title": "【2026年】AI資格おすすめ5選｜G検定・E資格・統計検定・Python資格・生成AI検定の使い分け",
        "keywords": "AI 資格 おすすめ G検定 E資格 統計検定",
        "search_query": "AI 資格 おすすめ 比較",
        "guidance": "5資格を難易度・勉強時間・取得後のキャリアメリットで比較。『資格単体では転職に不十分→スクール+資格の組み合わせ』を結論に置き、Neuro Dive、メイカラに誘導。CTA候補: Neuro Dive、メイカラ。"
    },
    # ===== 軸2: フリーランス・転職系（10トピック） =====
    {
        "title": "【2026年最新】フリーランスエンジニア平均月単価79.9万円｜実勢データから見る独立可能ライン",
        "keywords": "フリーランスエンジニア 単価 相場 2026 月額",
        "search_query": "フリーランスエンジニア 単価 相場 2026",
        "guidance": "en-japan・PR TIMES の2026年2月調査（平均79.9万円、最高320万円、職種別ランキング）を引用。職種別単価の表必須。フリーランスボード等の案件検索サービスを『市場価値を知る第一歩』として紹介。CTA候補: フリーランスボード、IT求人ナビフリーランス。"
    },
    {
        "title": "AIエンジニア年収2026｜求人ボックス調査で595万円、シニアは900万円超の実態",
        "keywords": "AIエンジニア 年収 2026 平均 求人",
        "search_query": "AIエンジニア 年収 平均",
        "guidance": "求人ボックス（595万円）、Studio Tale（600〜900万円、最上位2000万円超）の数値を整理。年収レンジ別に必要スキル（ジュニア=Python基礎、シニア=MLOps/LLM運用）を提示。スカウト型サービスへ自然誘導。CTA候補: TechClips ME、ミライフ。"
    },
    {
        "title": "IT転職エージェントおすすめ7社徹底比較2026｜SaaS・AI特化型の選び方",
        "keywords": "IT転職エージェント おすすめ 比較 2026 SaaS",
        "search_query": "IT転職エージェント おすすめ 比較",
        "guidance": "レバテックキャリア、マイナビIT AGENT、Geekly等の大手と、SaaS/AI特化のミライフ、TechClips MEを比較。『総合型 vs 特化型』の選び方フレーム。SaaS業界年収（IS 400〜700万円等）も提示。CTA候補: ミライフ、TechClips ME。"
    },
    {
        "title": "未経験からフリーランスエンジニアへの最短ルート｜独立前にやるべき3つの準備",
        "keywords": "フリーランスエンジニア 未経験 独立 準備",
        "search_query": "フリーランス 未経験 独立",
        "guidance": "『実務経験浅めでも平均単価63万円』（レバテックフリーランス）のデータを根拠に、現実的な独立ハードルを提示。準備3ステップ（実務2年→案件サイト登録→初案件獲得）。フリーランスボードを案件検索の入口として紹介。CTA候補: フリーランスボード、IT求人ナビフリーランス。"
    },
    {
        "title": "【失敗回避】フリーランスエンジニア独立で多い5つの落とし穴｜先輩の失敗例から学ぶ",
        "keywords": "フリーランスエンジニア 独立 失敗 原因",
        "search_query": "フリーランス 独立 失敗",
        "guidance": "tech-stock、Levtech、note等の複数ソースで一致する失敗5パターン（スキル偏り、営業力不足、資金管理、タスク管理、単価設定ミス）を実例ベースで解説。各失敗の『先回り対策』として案件検索サービス・エージェント活用を紹介。CTA候補: フリーランスボード、TechClips ME。"
    },
    {
        "title": "SaaS×AI業界転職ガイド2026｜年収400〜1,500万円の市場で勝つ方法",
        "keywords": "SaaS 転職 AI 2026 年収",
        "search_query": "SaaS AI 転職 年収",
        "guidance": "Geekly『SaaS 2026年3大トレンド: AIエージェント・バーティカル・コンパウンド』を起点に、年収レンジを職種別に整理。SaaS/AI特化のミライフ（EPC 853.75）を強く推薦。CTA候補: ミライフ。"
    },
    {
        "title": "副業エンジニアの始め方2026｜週2日で月5万円から始める現実的ステップ",
        "keywords": "副業エンジニア 始め方 月5万 週2",
        "search_query": "副業エンジニア 始め方",
        "guidance": "x-hours『週2日副業の7ステップ』、侍エンジニア『月1万円ロードマップ』のフレームを参考に、現実的な収入レンジ（最初は月1〜5万円、慣れて月10〜20万円）を提示。誇大表現は避ける。エージェント・案件サイト登録を最初の一歩として紹介。CTA候補: フリーランスボード、Agent Kikkake。"
    },
    {
        "title": "スカウト型転職サービス比較｜年収アップ実績平均160万円の活用法",
        "keywords": "スカウト型 転職サービス ITエンジニア おすすめ",
        "search_query": "スカウト型 転職 エンジニア",
        "guidance": "Findy、レバテックダイレクト、Direct type、Green等を比較。『スカウト型+エージェント併用で平均160万円アップ』（onamae調査）データを活用。TechClips ME（年収提示型スカウト）を独自ポジションとして強く紹介。CTA候補: TechClips ME。"
    },
    {
        "title": "30代未経験からのITエンジニア転職｜年齢別現実的なキャリア戦略",
        "keywords": "30代 未経験 ITエンジニア 転職",
        "search_query": "30代 未経験 エンジニア 転職",
        "guidance": "30代未経験の現実的なハードル（実務経験ない時の年収レンジ300〜400万円台）を率直に提示。スクール+エージェント併用が成功パターン。Agent Kikkake、ミライフを年齢層別に紹介。CTA候補: Agent Kikkake、ミライフ。"
    },
    {
        "title": "フリーランス案件検索サイト比較2026｜単価・案件数・サポートで選ぶ7社",
        "keywords": "フリーランス 案件検索サイト 比較 2026",
        "search_query": "フリーランス 案件サイト 比較",
        "guidance": "レバテックフリーランス、Pe-bank、フリーランスボード、IT求人ナビ等を平均単価・案件数・福利厚生で比較。『平均月単価79.9万円市場で自分に合う案件サイトを選ぶ基準』を提示。CTA候補: フリーランスボード、IT求人ナビフリーランス。"
    },
    # ===== 軸3: AI英語学習系（10トピック） =====
    {
        "title": "AI英会話アプリおすすめ7選2026｜スピーク・スピークバディ・fondiを徹底比較",
        "keywords": "AI英会話 アプリ おすすめ 比較 2026",
        "search_query": "AI英会話 アプリ おすすめ 比較",
        "guidance": "スピーク（EPC 358.02）、スピークバディ、fondi、パタプライングリッシュ等を料金/AI性能/学習機能/口コミで比較。スピークの確定率100%・口コミ高評価を強調しつつ訴求。CTA候補: スピーク。"
    },
    {
        "title": "AI英会話とオンライン英会話どっちが効果的？併用するベストな組み合わせ方",
        "keywords": "AI英会話 オンライン英会話 比較 効果",
        "search_query": "AI英会話 オンライン 違い",
        "guidance": "『AIで毎日アウトプット練習→週1回オンラインで実践』の併用パターンを推奨。スピーク（AI側）+ベストティーチャー（オンライン×Writing側）の組み合わせを具体例として提示。CTA候補: スピーク、ベストティーチャー。"
    },
    {
        "title": "【2026年最新】英語コーチングおすすめ7社｜短期で結果を出すサービス比較",
        "keywords": "英語コーチング おすすめ 比較 2026 ビジネス",
        "search_query": "英語コーチング おすすめ 比較",
        "guidance": "PROGRIT、Bizmates Coaching、レアジョブコーチング等の大手と、TEPPEN ENGLISHを比較。料金（月30,000〜80,000円相場）・期間・サポート体制で表化。完全没入型のTEPPEN ENGLISHを独自ポジで強く推薦。CTA候補: TEPPEN ENGLISH。"
    },
    {
        "title": "ChatGPTで英語学習｜シャドーイング教材を自作する5つのプロンプト",
        "keywords": "ChatGPT 英語学習 シャドーイング プロンプト",
        "search_query": "ChatGPT 英語 シャドーイング",
        "guidance": "シャドーイング教材作成の5プロンプト例（モノローグ生成、レベル別調整、ビジネス英語特化等）を提示。『独学派には強力だが、添削や発音指導が必要な人にはコーチング型が有効』として自然にTEPPEN ENGLISH・ベストティーチャーへ誘導。CTA候補: TEPPEN ENGLISH、ベストティーチャー。"
    },
    {
        "title": "TOEIC600点→800点を目指す社会人の最短ルート｜AI活用で効率化する勉強法",
        "keywords": "TOEIC 600点 800点 勉強法 社会人",
        "search_query": "TOEIC スコアアップ 勉強法",
        "guidance": "コエテコ『シャドーイング有効』を起点に、目標スコア別学習時間（600→730→800で各150〜250時間）を提示。AIアプリでスピーキング、オンライン英会話で実践、コーチングで全体管理という3段構成。CTA候補: スピーク、TEPPEN ENGLISH。"
    },
    {
        "title": "英会話が続かない7つの理由と対策｜AIアプリで習慣化する方法",
        "keywords": "英会話 続かない 原因 対策 習慣化",
        "search_query": "英会話 続かない 対策",
        "guidance": "複数ソースで一致する継続失敗7パターン（モチベ依存、目的曖昧、目標過大、時間管理、効果実感不足、講師相性、孤独）を解説。AI英会話の『24時間×低コスト×進捗可視化』が継続に有利な点を提示。CTA候補: スピーク、スマイルゼミENGLISH。"
    },
    {
        "title": "子ども向けオンライン英会話おすすめ5選2026｜AI教材×ネイティブ講師で選ぶ",
        "keywords": "子ども オンライン英会話 おすすめ 2026 AI",
        "search_query": "子ども 英語 オンライン",
        "guidance": "kimini、ネイティブキャンプ、hanaso kids等の大手と、Global Step Academy（4歳〜中学生対応）、スマイルゼミENGLISH（AIタブレット型）を比較。年齢別の選び方フレームを提示。CTA候補: Global Step Academy、スマイルゼミENGLISH。"
    },
    {
        "title": "ビジネス英語コーチングの選び方｜PROGRIT・TEPPEN ENGLISH・Bizmatesを徹底比較",
        "keywords": "ビジネス英語 コーチング 比較 PROGRIT TEPPEN",
        "search_query": "ビジネス英語 コーチング",
        "guidance": "料金・期間・自習時間管理・コーチ体制で4社を比較。『短期集中で結果を出したい層』にTEPPEN ENGLISH（完全没入型）を推薦。法人受講事例も紹介。CTA候補: TEPPEN ENGLISH。"
    },
    {
        "title": "英語Writing力を伸ばす3つの方法｜添削サービス vs ChatGPT校正の使い分け",
        "keywords": "英語 ライティング 上達 添削 ChatGPT",
        "search_query": "英語 ライティング 上達",
        "guidance": "ChatGPT校正の限界（細かなニュアンス、ビジネスフォーマルな表現）を指摘し、人間講師によるWriting添削（ベストティーチャー独自ポジ）の価値を提示。『ChatGPT下書き→ベストティーチャー添削』の併用フローを推薦。CTA候補: ベストティーチャー。"
    },
    {
        "title": "AIタブレット教材で子どもの英語力は伸びる？スマイルゼミENGLISH実態レビュー",
        "keywords": "AIタブレット 英語 子ども スマイルゼミ",
        "search_query": "スマイルゼミ 英語 効果",
        "guidance": "AIタブレット型学習のメリット（個別最適化、進捗可視化、保護者の負担軽減）と限界（実践会話量、講師との対話）を整理。スマイルゼミENGLISH（EPC 311.11、確定率75%）を中心に、Global Step Academyとの併用案も提示。CTA候補: スマイルゼミENGLISH、Global Step Academy。"
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
    "【出力形式】\n"
    "- Markdown形式で記事本文のみを出力\n"
    "- frontmatter（YAML）は出力しない（呼び出し側で付与する）\n"
    "- 記事冒頭にH1見出し（# タイトル）は不要、H2（##）から始めてよい\n"
    "- 出力の冒頭・末尾に「以下が記事です」のような前置き・後置きを書かないこと、Markdown本文のみ\n"
)


# ============================================================
# ユーティリティ
# ============================================================
def load_env():
    env = {}
    # 1. .env file (local Mac execution)
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env[key.strip()] = val.strip().strip('"').strip("'")
    # 2. OS environment variables (CI/Actions execution, also used as fallback/override-source)
    for key in ("GOOGLE_API_KEY", "NVIDIA_API_KEY", "NVIDIA_BASE_URL",
                "FREELLMAPI_KEY", "OPENAI_API_KEY", "OPENAI_API_BASE",
                "GITHUB_TOKEN", "TAVILY_API_KEY"):
        os_val = os.environ.get(key, "")
        if os_val and not env.get(key):
            env[key] = os_val
    return env


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = text.strip("-")
    return text[:60]


def get_jst_now():
    return datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=9)


def get_today_topic():
    jst_now = get_jst_now()
    day_of_year = jst_now.timetuple().tm_yday
    idx = day_of_year % len(TOPICS)
    return TOPICS[idx]


def fetch_search_context(query):
    """TODO: Tavily APIで実装予定（Day7以降）"""
    return ""


def build_prompt(topic, search_context):
    parts = [
        "テーマ: " + topic["title"],
        "キーワード: " + topic["keywords"],
        "方向性: " + topic["guidance"],
    ]
    if search_context:
        parts.append("参考情報:\n" + search_context)
    parts.append("")
    parts.append("上記に基づき、3000字以上の詳細なブログ記事をMarkdown形式で書いてください。比較表を含め、各セクションには具体例や数値を必ず入れてください。")
    return "\n\n".join(parts)


# ============================================================
# LLM API呼び出し（3段フォールバック）
# ============================================================
def _http_post_json(url, headers, body, timeout):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def call_freellmapi(prompt, env, max_tokens=6000):
    api_key = env.get("FREELLMAPI_KEY", "")
    if not api_key:
        raise ValueError("FREELLMAPI_KEY not found in env")

    url = "http://localhost:3001/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    base_body = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    last_error = None
    for model_name in ["llama-3.3-70b-versatile", "qwen3-235b", "gemini-2.5-flash", "auto"]:
        try:
            body = dict(base_body)
            body["model"] = model_name
            data = _http_post_json(url, headers, body, timeout=90)
            content = data["choices"][0]["message"]["content"]
            if content and content.strip():
                return content
            last_error = "empty content from model " + model_name
        except Exception as e:
            last_error = "model " + model_name + ": " + str(e)
            continue

    raise RuntimeError("FreeLLMAPI failed: " + str(last_error))


def call_gemini_direct(prompt, env, max_tokens=6000):
    api_key = env.get("GOOGLE_API_KEY", "")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in env")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent?key=" + api_key
    )
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT + "\n\n" + prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.7,
        },
    }

    data = _http_post_json(url, headers, body, timeout=90)
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini returned no candidates: " + json.dumps(data)[:300])
    parts = candidates[0].get("content", {}).get("parts", [])
    texts = [p.get("text", "") for p in parts if p.get("text")]
    text = "\n".join(texts).strip()
    if not text:
        raise RuntimeError("Gemini returned empty text")
    return text


def call_nvidia_nim(prompt, env, max_tokens=6000):
    api_key = env.get("NVIDIA_API_KEY", "")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY not found in env")

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    body = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    data = _http_post_json(url, headers, body, timeout=90)
    content = data["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise RuntimeError("NVIDIA NIM returned empty content")
    return content


def generate_article_with_fallback(prompt, env):
    providers = [
        ("freellmapi", call_freellmapi),
        ("gemini_direct", call_gemini_direct),
        ("nvidia_nim", call_nvidia_nim),
    ]

    last_error = None
    for name, func in providers:
        print("[INFO] Trying provider: " + name)
        try:
            text = func(prompt, env)
            print("[INFO] Provider " + name + " succeeded (" + str(len(text)) + " chars)")
            return text, name
        except Exception as e:
            last_error = str(e)
            print("[WARN] " + name + " failed: " + last_error)
            time.sleep(3)

    raise RuntimeError("All 3 LLM providers failed. Last error: " + str(last_error))


def generate_description(article_text, env):
    snippet = article_text[:2000]
    prompt = (
        "以下の記事を、SEO用メタディスクリプションとして100〜120字の日本語で要約してください。"
        "記号や改行を含めず、純粋な要約文のみを出力してください。\n\n"
        + snippet
    )
    try:
        text, _ = generate_article_with_fallback(prompt, env)
        text = text.strip().replace("\n", " ").replace("\r", " ")
        if len(text) > 130:
            cut = text[:120]
            for sep in ["。", "．", ".", "！", "!", "？", "?"]:
                last = cut.rfind(sep)
                if last >= 60:
                    cut = cut[:last + len(sep)]
                    break
            text = cut
        return text
    except Exception as e:
        print("[WARN] description generation failed, using fallback: " + str(e))
        return ""


# ============================================================
# 記事ファイル書き出し
# ============================================================
def write_article_file(filepath, topic, article_body, description, provider, today):
    title_escaped = topic["title"].replace('"', '\\"')
    desc_escaped = description.replace('"', '\\"').replace("\n", " ")
    first_keyword = topic["keywords"].split()[0] if topic["keywords"] else "AI"

    frontmatter_lines = [
        "---",
        "layout: post.njk",
        'title: "' + title_escaped + '"',
        "date: " + today,
        "tags: [AI, " + first_keyword + "]",
        'description: "' + desc_escaped + '"',
        "ai_generated: true",
        'generated_via: "' + provider + '"',
        "---",
        "",
    ]
    frontmatter = "\n".join(frontmatter_lines)

    content = frontmatter + "\n" + article_body + "\n" + AFFILIATE_CTA + "\n"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# Git操作
# ============================================================
def git_commit_and_push(repo_dir, commit_message):
    try:
        subprocess.run(
            ["git", "add", "src/articles/"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )
        return True, "ok"
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
        return False, stderr
    except Exception as e:
        return False, str(e)


# ============================================================
# メイン処理
# ============================================================
def main():
    print("[INFO] === daily_article_generator.py start ===")
    print("[INFO] Started at (JST): " + get_jst_now().isoformat())
    env = load_env()
    if not env:
        print("[ERROR] env file empty or not found: " + ENV_FILE)
        return 1

    topic = get_today_topic()
    jst_now = get_jst_now()
    today = jst_now.date().isoformat()

    slug = slugify(topic["title"])
    filename = today + "-" + slug + ".md"
    filepath = os.path.join(ARTICLES_DIR, filename)

    print("[INFO] Topic: " + topic["title"])
    print("[INFO] Filepath: " + filepath)

    if os.path.exists(filepath):
        print("[SKIP] Already exists: " + filename)
        return 0

    search_context = fetch_search_context(topic["search_query"])
    prompt = build_prompt(topic, search_context)

    try:
        article_body, provider = generate_article_with_fallback(prompt, env)
    except Exception as e:
        print("[ERROR] Article generation failed: " + str(e))
        return 1

    print("[INFO] Generating description...")
    description = generate_description(article_body, env)
    if not description:
        description = topic["title"] + "について、最新情報と実践的な手順を解説します。"
    print("[INFO] Description: " + description)

    write_article_file(filepath, topic, article_body, description, provider, today)
    print("[INFO] Article written: " + filepath)

    commit_message = "Add daily article: " + topic["title"] + " (via " + provider + ")"
    push_ok, push_msg = git_commit_and_push(REPO_DIR, commit_message)
    if push_ok:
        print("[INFO] Git push succeeded")
    else:
        print("[WARN] Git push failed: " + push_msg)

    print("[INFO] === daily_article_generator.py done ===")
    return 0


if __name__ == "__main__":
    exit_code = main()
    raise SystemExit(exit_code)
