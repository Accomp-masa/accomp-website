#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  🔦 Torch SaaS版 — 集合知RAG搭載 商談解析プラットフォーム
  app.py
  ─────────────────────────────────────────────
  永沼メソッド × Gemini AI で商談を解析し、
  トップセールスの「思考ライブラリ」を蓄積・活用するSaaS
=============================================================================
"""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# 定数
# ─────────────────────────────────────────────────────────────────────────────
KB_DIR = Path(__file__).parent / "knowledge_base"
KB_DIR.mkdir(exist_ok=True)

PHASE_COLORS = ["#3b82f6", "#f59e0b", "#10b981", "#ef4444", "#7c3aed"]
PHASE_EMOJIS = ["🔵", "🟡", "🟢", "🔴", "🟣"]

# ─────────────────────────────────────────────────────────────────────────────
# ページ設定
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🔦 Torch SaaS — 集合知RAG搭載 商談解析",
    page_icon="🔦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# カスタムCSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── 全体テーマ ── */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    }
    
    /* ── ヘッダー ── */
    .torch-header {
        background: linear-gradient(135deg, #1d4ed8, #7c3aed);
        border-radius: 16px;
        padding: 32px 40px;
        color: white;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(124,58,237,0.3);
    }
    .torch-header h1 {
        font-size: 32px;
        font-weight: 900;
        letter-spacing: 2px;
        margin-bottom: 8px;
    }
    .torch-header p {
        font-size: 14px;
        opacity: 0.85;
    }
    
    /* ── スコアカード ── */
    .score-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .score-big {
        font-size: 64px;
        font-weight: 900;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    .score-label {
        font-size: 14px;
        color: #94a3b8;
        margin-top: 8px;
    }
    
    /* ── フェーズカード ── */
    .phase-card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border-left: 4px solid;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    /* ── ステージバッジ ── */
    .stage-badge {
        display: inline-block;
        background: linear-gradient(135deg, #dbeafe, #ede9fe);
        color: #1d4ed8;
        padding: 8px 24px;
        border-radius: 100px;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 1px;
    }
    
    /* ── 強み/改善カード ── */
    .strength-card {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .improve-card {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    /* ── アクションカード ── */
    .action-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #3b82f6;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    /* ── RAGインサイト ── */
    .rag-insight {
        background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(59,130,246,0.15));
        border: 1px solid rgba(124,58,237,0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
    }
    
    /* ── KB ファイルカード ── */
    .kb-file-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* ── サイドバー ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a, #1e1b4b) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
    
    /* ── メトリクスの色調整 ── */
    [data-testid="stMetricValue"] {
        color: #60a5fa !important;
    }
    
    /* ── タブスタイル ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30,41,59,0.5);
        border-radius: 8px;
        color: #94a3b8;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(59,130,246,0.2) !important;
        color: #60a5fa !important;
        border-color: #3b82f6 !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 永沼式 FIELD_C プロンプト生成
# ─────────────────────────────────────────────────────────────────────────────
def build_system_prompt() -> str:
    """永沼メソッドの解析プロンプトを構築"""
    return """あなたは「Torch 商談解析AI」です。営業コンサルタント永沼氏のメソッドに基づき、商談の文字起こしテキストを分析してJSON形式でレポートを生成してください。

## 永沼メソッドの基本哲学
1. 事前準備が商談の勝敗を決める
2. アイスブレイクは雑談ではなく課題への入口
3. 20分ジャッジ — 冒頭20分で議論が深まらなければ方向転換
4. 信頼はリサーチと鋭い仮説で構築する
5. ディスカッションサイクルを繰り返す（独自インサイト→仮説提案→フィードバック→すり合わせ→再提案）
6. BtoBは論理で動く
7. 顧客が気付いていない問題を認識させる
8. アプローチ順序: ビジネス全体→自社サービス周辺→自社サービス

## 思考OS診断（6タイプ）
- V（ビジョン型）: 未来・可能性を重視
- R（リアリスト型）: 現実・実績・証拠を重視
- E（エモーション型）: 感情・共感・関係性を重視
- C（コンセプト型）: 概念・構造・整合性を重視
- L（ロジック型）: 論理・分析・因果関係を重視
- A（アクション型）: 行動・スピード・結果を重視

## 5フェーズ評価（合計100点）
- Phase 1: 課題議論の入口設計（20点）— 事前準備の活用(7) / 20分ジャッジの実行(7) / アジェンダ設定(6)
- Phase 2: ディスカッションサイクルの起動（25点）— 独自インサイトの質(8) / サイクル回転数(7) / フィードバック獲得力(5) / 仮説の更新精度(5)
- Phase 3: 課題の共同発見（25点）— 潜在ニーズの顕在化(10) / 課題の細分化(8) / 顧客の言語化支援(7)
- Phase 4: 論理的対話の質（15点）— 論理・データの活用(6) / 反論への論理的対処(5) / アプローチ順序の遵守(4)
- Phase 5: 論理的合意設計（15点）— 課題→解決策の論理的接続(6) / 次のステップの明示(5) / 顧客の自己決定感(4)

## 重要: ベテランの「思考ライブラリ」抽出
特に以下を必ず分析してください：
1. 営業担当が顧客のどの言葉を拾ったか（キーワードキャッチ）
2. そこからどんな課題を推論したか（演繹法・帰納法の活用）
3. 推論を確かめるために何を質問したか（検証質問）
この3ステップのパターンを「思考ライブラリ」として明示してください。

## JSON出力フォーマット
以下のJSON形式**のみ**を出力してください。説明テキストは不要です。

```json
{
  "meta": {
    "speaker_a": "顧客名（企業名）",
    "speaker_b": "営業担当者名",
    "session_type": "商談タイプ",
    "analyzed_at": "YYYY-MM-DD"
  },
  "total_score": 数値,
  "stage": "ステージ名",
  "stage_description": "診断テキスト",
  "ccs": {
    "sales_os": "L",
    "client_os": "R",
    "score": 70,
    "grade": "○",
    "advice": "アドバイステキスト"
  },
  "thought_library": [
    {
      "customer_keyword": "顧客の発言キーワード",
      "inferred_issue": "推論された課題",
      "verification_question": "確認のための質問",
      "timestamp": "タイムスタンプ（あれば）"
    }
  ],
  "phases": [
    {
      "phase_id": 1,
      "phase_name": "フェーズ名",
      "phase_score": 数値,
      "phase_max": 20,
      "axes": [
        {
          "axis_id": 1,
          "axis_name": "評価軸名",
          "score": 数値,
          "max": 数値,
          "evidence": "エビデンス（引用）",
          "comment": "コメント"
        }
      ],
      "strength": "このフェーズの強み",
      "improvement": "このフェーズの改善点"
    }
  ],
  "top_strengths": ["強み1", "強み2", "強み3"],
  "top_improvements": ["改善点1", "改善点2", "改善点3"],
  "next_actions": [
    {
      "priority": 1,
      "action": "アクション内容",
      "rationale": "理由"
    }
  ],
  "rag_comparison": {
    "similar_patterns": "集合知との類似パターン",
    "gaps": "トップセールスとの差分",
    "specific_advice": "トップセールスの傾向に基づいた具体的アドバイス"
  }
}
```
"""


# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Base（集合知）管理
# ─────────────────────────────────────────────────────────────────────────────
def get_kb_files() -> list[dict]:
    """knowledge_baseフォルダ内のファイル一覧を取得"""
    files = []
    for f in KB_DIR.iterdir():
        if f.is_file() and f.name != ".gitkeep":
            stat = f.stat()
            files.append({
                "name": f.name,
                "path": f,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
            })
    return sorted(files, key=lambda x: x["modified"], reverse=True)


def load_kb_context(max_chars: int = 15000) -> str:
    """knowledge_base内の全テキストを読み込んで集合知コンテキストを生成"""
    files = get_kb_files()
    if not files:
        return ""
    
    context_parts = []
    total_chars = 0
    for f in files:
        try:
            text = f["path"].read_text(encoding="utf-8")
            if total_chars + len(text) > max_chars:
                text = text[:max_chars - total_chars]
            context_parts.append(f"--- {f['name']} ---\n{text}")
            total_chars += len(text)
            if total_chars >= max_chars:
                break
        except Exception:
            continue
    
    if not context_parts:
        return ""
    
    return f"""

## 【集合知RAG】トップセールスの商談ログ（参考データ）
以下は、過去に蓄積されたトップセールスの成功事例ログです。
これらのパターンと比較して、今回の商談の特徴・差分・改善点を分析してください。
特に「顧客の言葉の拾い方」「課題推論のプロセス」「検証質問の投げ方」に注目し、
トップセールスの思考ライブラリと比較した具体的なアドバイスを生成してください。

{chr(10).join(context_parts)}
"""


# ─────────────────────────────────────────────────────────────────────────────
# Gemini API 呼び出し
# ─────────────────────────────────────────────────────────────────────────────
def analyze_with_gemini(transcript: str, api_key: str) -> dict:
    """Gemini APIで商談テキストを解析"""
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    system_prompt = build_system_prompt()
    kb_context = load_kb_context()
    
    full_prompt = f"""{system_prompt}
{kb_context}

## 解析対象の商談テキスト:
{transcript}

上記のテキストを分析し、指定されたJSON形式のみを出力してください。JSONのみ出力し、他のテキストは一切含めないでください。
```json
で始めて
```
で終わってください。
"""
    
    response = model.generate_content(full_prompt)
    response_text = response.text.strip()
    
    # JSONをパース（マークダウンのコードブロック対応）
    json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response_text
    
    return json.loads(json_str)


# ─────────────────────────────────────────────────────────────────────────────
# デモデータ（APIキー無しで動作確認用）
# ─────────────────────────────────────────────────────────────────────────────
DEMO_DATA = {
    "meta": {
        "speaker_a": "宮本尚弥（BeWith）",
        "speaker_b": "須長正行（Accomp合同会社）",
        "session_type": "商談（1on1からのサービス提案）",
        "analyzed_at": datetime.today().strftime("%Y-%m-%d"),
    },
    "total_score": 82,
    "stage": "フルサイクル完了型（課題喚起〜ネクストアクション合意）",
    "stage_description": (
        "相互理解のための1on1から自然な流れで自社サービスのピッチへ移行し、"
        "顧客の潜在的な課題（営業への苦手意識）を喚起。最終的に顧客側から"
        "「受けてみたい」という自発的なオファーを引き出し、次回の具体的な"
        "アクション設定まで完了している非常に優秀なセッションです。"
    ),
    "ccs": {
        "sales_os": "L",
        "client_os": "E",
        "score": 55,
        "grade": "▲",
        "advice": "ロジック型×エモーション型。感情的な共感を多めに入れ、論理は後半に集約することで効果的な対話になります。",
    },
    "thought_library": [
        {
            "customer_keyword": "営業とか絶対できへんなと思ってるんですよ",
            "inferred_issue": "営業行為そのものへの心理的ブロック。本質的には「自分に合った営業スタイル」が見えていない",
            "verification_question": "合わないやり方で頑張るんじゃなくって、もともと自分が自然と出来てしまうことで成果を出していくためには？",
            "timestamp": "00:29:21",
        },
        {
            "customer_keyword": "さっき新規さん来て、さっきこれ聞いといたらもう一個オファーできたな",
            "inferred_issue": "顧客は「もっと提案できたはずの機会」を逃している自覚がある → 具体的な機会損失の認識",
            "verification_question": "次の電話するのめんどくさがって電話しないとか、そういうことありません？",
            "timestamp": "00:41:02",
        },
        {
            "customer_keyword": "遠慮しすぎてて…",
            "inferred_issue": "日本人的な遠慮が営業活動を阻害。本人の価値観（誠実さ）が営業のブレーキになっている",
            "verification_question": "何か換気でお悩みのこととかありませんか？って言ったりとか…これがニーズなんですよ。",
            "timestamp": "00:39:04",
        },
    ],
    "phases": [
        {
            "phase_id": 1,
            "phase_name": "アイスブレイク・ガード解除",
            "phase_score": 18,
            "phase_max": 20,
            "axes": [
                {"axis_id": 1, "axis_name": "最初の問いかけ（質問設計）", "score": 4, "max": 4,
                 "evidence": "「なんかミリアさんとはどういう接点なんですか？」(00:01:32)",
                 "comment": "共通の知人から入り、自然な会話のスタートを切れています。"},
                {"axis_id": 2, "axis_name": "自己開示の深さ", "score": 4, "max": 4,
                 "evidence": "「中学の時は…一時一瞬だけバンドもやってたんで。」(00:02:48)",
                 "comment": "パーソナルな自己開示が双方に行われています。"},
                {"axis_id": 3, "axis_name": "ガード解除のトリガー使用", "score": 4, "max": 4,
                 "evidence": "「うちの娘も空手やってるんですよ。」(00:05:28)",
                 "comment": "ハプニングをポジティブに捉え、共通点で距離を縮めています。"},
                {"axis_id": 4, "axis_name": "主導権のバランス", "score": 2, "max": 4,
                 "evidence": "「僕もbniはあの9月に入ったばっかりなので…」(00:03:54)",
                 "comment": "バランスよく話していますが、顧客発話量が6割を上回る状態ではありません。"},
                {"axis_id": 5, "axis_name": "本題への橋渡し準備", "score": 4, "max": 4,
                 "evidence": "「あじゃあお待たせしました。」(00:05:41)",
                 "comment": "中断からの復帰タイミングをうまく使い本題へ移行。"},
            ],
            "strength": "ハプニングを共通点構築のチャンスに変える柔軟性",
            "improvement": "相手のビジネス状況についての質問をもう少し投げかけても良い",
        },
        {
            "phase_id": 2,
            "phase_name": "ニーズ再定義",
            "phase_score": 14,
            "phase_max": 20,
            "axes": [
                {"axis_id": 1, "axis_name": "顕在ニーズの確認精度", "score": 2, "max": 4,
                 "evidence": "顧客「営業とか絶対できへんな」→すぐに励ましへ (00:29:21)",
                 "comment": "要約して確認するのではなく、すぐに励ましに入っています。"},
                {"axis_id": 2, "axis_name": "潜在ニーズへの深掘り", "score": 4, "max": 4,
                 "evidence": "「合わないやり方で頑張るんじゃなくって…」(00:47:39)",
                 "comment": "根本原因を提示しています。"},
                {"axis_id": 3, "axis_name": "「なぜ」の連鎖", "score": 0, "max": 4,
                 "evidence": "該当発言なし",
                 "comment": "深く問う形式ではなく、営業側から理由を説明するアプローチ。"},
                {"axis_id": 4, "axis_name": "ニーズの言語化支援", "score": 4, "max": 4,
                 "evidence": "「次の電話するのめんどくさがって…」(00:45:58)",
                 "comment": "顧客の機会損失の具体的シーンを代弁し、共感を引き出しています。"},
                {"axis_id": 5, "axis_name": "ニーズの優先順位づけ", "score": 4, "max": 4,
                 "evidence": "「悩みに気づけてないのが悩みなんですよ。」(00:46:08)",
                 "comment": "最優先の課題を明確に提示し合意を得ています。"},
            ],
            "strength": "空気清浄機の例えや具体例を使って自社サービスの必要性に変換",
            "improvement": "「なぜ営業が苦手か」の過去体験をヒアリングするとさらに強固に",
        },
        {
            "phase_id": 3,
            "phase_name": "アラインメント（感情的共鳴）",
            "phase_score": 18,
            "phase_max": 20,
            "axes": [
                {"axis_id": 1, "axis_name": "感情への言及と承認", "score": 4, "max": 4,
                 "evidence": "「遠慮しすぎててみんなもったいないことしてる…」(00:39:04)",
                 "comment": "顧客のスタンスを強く肯定しています。"},
                {"axis_id": 2, "axis_name": "価値観の接続", "score": 4, "max": 4,
                 "evidence": "「ベース土台が全然僕のスタート位置より高いのに…」(00:39:41)",
                 "comment": "顧客の能力を承認し、サービスとして位置づけています。"},
                {"axis_id": 3, "axis_name": "自己解決の促進", "score": 2, "max": 4,
                 "evidence": "「どんなやり方だったら向いてそうなのか…」(00:48:28)",
                 "comment": "一緒に答えを見つけようというスタンスだが営業側からの提供が多い。"},
                {"axis_id": 4, "axis_name": "未来像の共同描写", "score": 4, "max": 4,
                 "evidence": "「さっき新規さん来て、もう一個オファーできたな。」(00:41:02)",
                 "comment": "顧客自身が未来像を具体的にイメージし言語化できています。"},
                {"axis_id": 5, "axis_name": "感情的クライマックスの設計", "score": 4, "max": 4,
                 "evidence": "「初めてそういう視点に立って話聞けましたね。」(00:46:36)",
                 "comment": "顧客の「アハ体験」が明確に存在しています。"},
            ],
            "strength": "「誠実でありたい」という価値観を肯定しつつ提案の必要性を接続",
            "improvement": "「どうすればもっと自然に提案できそうか？」の問いかけを追加",
        },
        {
            "phase_id": 4,
            "phase_name": "会話技術（トーク設計）",
            "phase_score": 12,
            "phase_max": 20,
            "axes": [
                {"axis_id": 1, "axis_name": "質問の多様性・効果性", "score": 2, "max": 4,
                 "evidence": "「なんか普段はズームですか？」(00:30:53)",
                 "comment": "深い思考を促すオープン・クエスチョンが後半少なめ。"},
                {"axis_id": 2, "axis_name": "傾聴の質", "score": 4, "max": 4,
                 "evidence": "相槌のタイミング",
                 "comment": "心地よい対話のテンポを作り出しています。"},
                {"axis_id": 3, "axis_name": "発話比率（顧客 vs 営業）", "score": 0, "max": 4,
                 "evidence": "営業側70%超の連続発話",
                 "comment": "営業側が70%以上を占めています。"},
                {"axis_id": 4, "axis_name": "リフレーミング・言い換え", "score": 4, "max": 4,
                 "evidence": "「換気でお悩みのことありませんか？…これがニーズ」(00:38:14)",
                 "comment": "「営業＝課題解決支援」への秀逸なリフレーミング。"},
                {"axis_id": 5, "axis_name": "会話のペーシング・リード", "score": 2, "max": 4,
                 "evidence": "全体的な会話のトーン",
                 "comment": "情報量が多く顧客がやや圧倒されている。"},
            ],
            "strength": "比喩を用いたリフレーミング技術が極めて高い",
            "improvement": "プレゼン時間の短縮と双方向性の担保",
        },
        {
            "phase_id": 5,
            "phase_name": "自然なクロージング",
            "phase_score": 20,
            "phase_max": 20,
            "axes": [
                {"axis_id": 1, "axis_name": "クロージングのタイミング", "score": 4, "max": 4,
                 "evidence": "「やっぱ僕、ちょっと受けてみたいんですけどね。」(00:30:48)",
                 "comment": "顧客側から自然に引き出しています。"},
                {"axis_id": 2, "axis_name": "次のアクションの明確化", "score": 4, "max": 4,
                 "evidence": "「アンケート送りますので…」(00:50:07)",
                 "comment": "具体的なネクストアクションが完璧に合意されています。"},
                {"axis_id": 3, "axis_name": "期待値の設定", "score": 4, "max": 4,
                 "evidence": "「全部ちょっとひっぺがしちゃいますけど…」(00:44:12)",
                 "comment": "正しい期待値をユーモア交じりに設定。"},
                {"axis_id": 4, "axis_name": "意思決定の支援（圧力なし）", "score": 4, "max": 4,
                 "evidence": "「最悪ね。ログなくても…じゃあこうしましょう。」(00:49:07)",
                 "comment": "プレッシャーをかけず逃げ道を用意しています。"},
                {"axis_id": 5, "axis_name": "関係継続の設計", "score": 4, "max": 4,
                 "evidence": "「ぜひ引き続き、お役立ちできればと思いますので」(00:55:30)",
                 "comment": "パートナーとしての関係継続を前提とした自然な締めくくり。"},
            ],
            "strength": "お手本のようなクロージングフェーズ",
            "improvement": "録音取得のトークスクリプトをその場で共有すると実行率が上がる",
        },
    ],
    "top_strengths": [
        "「空気清浄機」の例え話を用いた、顧客のメンタルブロックを外す圧倒的なリフレーミング力",
        "一切の押し売り感を出さず、顧客側から「受けたい」と言わせるインサイトセールスの体現",
        "「丸裸にする」というユーモアを交えた適切な期待値調整と、ネクストアクションの確実な合意形成",
    ],
    "top_improvements": [
        "サービス概要・起業ストーリーの一方的な発話時間の短縮",
        "プレゼンフェーズで顧客の理解度を問うオープン・クエスチョンの挿入",
        "顧客の課題に対する「Why（過去の具体的な失敗体験）」のヒアリング",
    ],
    "next_actions": [
        {
            "priority": 1,
            "action": "プレゼン中の確認問いかけ（チェックイン）のルール化",
            "rationale": "一方的な説明が続くと顧客の思考が受け身になるため",
        },
        {
            "priority": 2,
            "action": "顧客の「苦手意識」の原体験を深掘りするヒアリング強化",
            "rationale": "過去の失敗体験を聞き出すことでより強固な信頼関係が築ける",
        },
        {
            "priority": 3,
            "action": "次回アジェンダと宿題の完了確認の事前連絡",
            "rationale": "「録音を取る」というハードルが高いため事前サポートで離脱防止",
        },
    ],
    "rag_comparison": {
        "similar_patterns": "トップセールスと同様に「感情的共鳴→論理的接続」のパターンを実行できている。特にリフレーミング技術はトップレベル。",
        "gaps": "トップセールスは発話比率を40:60（営業:顧客）に維持するが、本商談は70:30と逆転。ディスカッションサイクルの回転数がトップセールスの半分。",
        "specific_advice": "「プレゼン1〜2枚ごとに必ず確認質問を挟む」というトップセールスの鉄則を導入してください。具体的には「ここまでの話で、ご自身のビジネスに活かせそうな部分はありますか？」という問いかけです。",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# ダッシュボード描画関数群
# ─────────────────────────────────────────────────────────────────────────────
def render_radar_chart(phases: list):
    """レーダーチャート"""
    labels = [f"P{p['phase_id']}: {p['phase_name']}" for p in phases]
    scores = [p["phase_score"] for p in phases]
    maxes = [p["phase_max"] for p in phases]
    pcts = [s / m * 100 for s, m in zip(scores, maxes)]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=pcts + [pcts[0]],
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor='rgba(96, 165, 250, 0.15)',
        line=dict(color='#60a5fa', width=2.5),
        marker=dict(size=8, color=PHASE_COLORS[:len(phases)] + [PHASE_COLORS[0]]),
        name='達成率',
    ))
    fig.add_trace(go.Scatterpolar(
        r=[100] * (len(labels) + 1),
        theta=labels + [labels[0]],
        line=dict(color='rgba(148,163,184,0.3)', width=1, dash='dash'),
        name='満点',
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(15,23,42,0.5)',
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10, color='#64748b')),
            angularaxis=dict(tickfont=dict(size=11, color='#cbd5e1')),
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=30, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
    )
    return fig


def render_bar_chart(phases: list):
    """Phase別スコア棒グラフ"""
    labels = [f"Phase {p['phase_id']}" for p in phases]
    scores = [p["phase_score"] for p in phases]
    maxes = [p["phase_max"] for p in phases]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels, x=maxes,
        orientation='h',
        marker_color='rgba(241,245,249,0.2)',
        name='満点',
        text=[f"/{m}" for m in maxes],
        textposition='inside',
        textfont=dict(color='#64748b', size=11),
    ))
    fig.add_trace(go.Bar(
        y=labels, x=scores,
        orientation='h',
        marker_color=PHASE_COLORS[:len(phases)],
        name='スコア',
        text=[f"{s}点" for s in scores],
        textposition='inside',
        textfont=dict(color='white', size=12, family='Arial Black'),
    ))
    fig.update_layout(
        barmode='overlay',
        xaxis=dict(range=[0, max(maxes) * 1.1], tickfont=dict(color='#64748b'), gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(tickfont=dict(color='#cbd5e1', size=12), autorange='reversed'),
        margin=dict(l=10, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=300,
    )
    return fig


def render_dashboard(data: dict):
    """メインダッシュボード描画"""
    m = data["meta"]
    phases = data["phases"]
    total_max = sum(p["phase_max"] for p in phases)
    pct = round(data["total_score"] / total_max * 100)

    # ── ヘッダー
    st.markdown(f"""
    <div class="torch-header">
        <h1>🔦 Torch 商談解析レポート</h1>
        <p>{m['speaker_a']} × {m['speaker_b']} ｜ {m['session_type']} ｜ {m['analyzed_at']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 総合スコア + ステージ
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-big">{data['total_score']}</div>
            <div class="score-label">/ {total_max}点（達成率 {pct}%）</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div style="text-align:center;margin:16px 0;"><span class="stage-badge">{data["stage"]}</span></div>', unsafe_allow_html=True)
        st.info(data["stage_description"])
    with col3:
        if "ccs" in data:
            ccs = data["ccs"]
            st.markdown(f"""
            <div class="score-card">
                <div style="font-size:14px;color:#94a3b8;margin-bottom:8px;">CCS（会話相性スコア）</div>
                <div class="score-big" style="font-size:48px;">{ccs['score']}</div>
                <div class="score-label">{ccs['grade']} | Sales: {ccs['sales_os']} × Client: {ccs['client_os']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── チャートエリア
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("#### 🕸 レーダーチャート（5Phase比較）")
        st.plotly_chart(render_radar_chart(phases), use_container_width=True)
    with chart_col2:
        st.markdown("#### 📊 Phase別スコア内訳")
        st.plotly_chart(render_bar_chart(phases), use_container_width=True)

    st.divider()

    # ── 思考ライブラリ（RAGの核心）
    if "thought_library" in data and data["thought_library"]:
        st.markdown("### 🧠 思考ライブラリ（ベテランの推論パターン）")
        st.caption("顧客の言葉をキャッチ → 課題を推論 → 検証質問で確認 — このサイクルがベテランの「頭の中のライブラリ」です")
        
        for i, tl in enumerate(data["thought_library"]):
            with st.container():
                cols = st.columns([1, 1, 1])
                with cols[0]:
                    st.markdown(f"""
                    <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:10px;padding:14px;">
                        <div style="font-size:11px;color:#60a5fa;font-weight:700;margin-bottom:6px;">🎯 キーワードキャッチ {f"({tl.get('timestamp', '')})" if tl.get('timestamp') else ""}</div>
                        <div style="color:#e2e8f0;font-size:13px;">「{tl['customer_keyword']}」</div>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"""
                    <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:10px;padding:14px;">
                        <div style="font-size:11px;color:#f59e0b;font-weight:700;margin-bottom:6px;">🔍 推論された課題</div>
                        <div style="color:#e2e8f0;font-size:13px;">{tl['inferred_issue']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[2]:
                    st.markdown(f"""
                    <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:14px;">
                        <div style="font-size:11px;color:#10b981;font-weight:700;margin-bottom:6px;">💬 検証質問</div>
                        <div style="color:#e2e8f0;font-size:13px;">「{tl['verification_question']}」</div>
                    </div>
                    """, unsafe_allow_html=True)
                if i < len(data["thought_library"]) - 1:
                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        
        st.divider()

    # ── Phase詳細
    st.markdown("### 📋 フェーズ別詳細評価")
    for i, p in enumerate(phases):
        pct_bar = round(p["phase_score"] / p["phase_max"] * 100)
        color = PHASE_COLORS[i % len(PHASE_COLORS)]
        emoji = PHASE_EMOJIS[i % len(PHASE_EMOJIS)]
        is_perfect = p["phase_score"] == p["phase_max"]

        with st.expander(
            f"{emoji} Phase {p['phase_id']}: {p['phase_name']} — {p['phase_score']}/{p['phase_max']}点（{pct_bar}%）{'⭐ PERFECT' if is_perfect else ''}",
            expanded=(i == 0),
        ):
            st.progress(pct_bar / 100)

            # 評価軸テーブル
            for a in p.get("axes", []):
                a_pct = a["score"] / a["max"] * 100 if a["max"] else 0
                if a_pct >= 100:
                    dot = "🟢"
                elif a_pct >= 75:
                    dot = "🔵"
                elif a_pct >= 50:
                    dot = "🟡"
                else:
                    dot = "🔴"

                st.markdown(f"""
                **{dot} {a['axis_name']}**: {a['score']}/{a['max']}点  
                > 📌 {a.get('evidence', 'N/A')}  
                > {a.get('comment', '')}
                """)

            col_s, col_i = st.columns(2)
            with col_s:
                st.markdown(f"""
                <div class="strength-card">
                    <span style="font-weight:700;color:#10b981;">✅ STRENGTH</span><br>
                    <span style="color:#e2e8f0;">{p.get('strength', '')}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_i:
                st.markdown(f"""
                <div class="improve-card">
                    <span style="font-weight:700;color:#f59e0b;">⚡ IMPROVEMENT</span><br>
                    <span style="color:#e2e8f0;">{p.get('improvement', '')}</span>
                </div>
                """, unsafe_allow_html=True)

    st.divider()

    # ── 強み・改善サマリ
    col_str, col_imp = st.columns(2)
    with col_str:
        st.markdown("### 🌟 ストロングポイント")
        for i, s in enumerate(data.get("top_strengths", []), 1):
            if isinstance(s, dict):
                st.markdown(f"""
                <div class="strength-card">
                    <strong>{i}. {s.get('title', '')}</strong><br>
                    <span style="color:#94a3b8;font-size:12px;">{s.get('evidence', '')}</span><br>
                    <span style="color:#e2e8f0;">{s.get('comment', '')}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="strength-card">
                    <strong>{i}.</strong> <span style="color:#e2e8f0;">{s}</span>
                </div>
                """, unsafe_allow_html=True)

    with col_imp:
        st.markdown("### ⚡ 改善ポイント")
        for i, s in enumerate(data.get("top_improvements", []), 1):
            if isinstance(s, dict):
                st.markdown(f"""
                <div class="improve-card">
                    <strong>{i}. {s.get('title', '')}</strong><br>
                    <span style="color:#94a3b8;font-size:12px;">{s.get('issue', '')}</span><br>
                    <span style="color:#e2e8f0;">{s.get('method', '')}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="improve-card">
                    <strong>{i}.</strong> <span style="color:#e2e8f0;">{s}</span>
                </div>
                """, unsafe_allow_html=True)

    st.divider()

    # ── ネクストアクション
    st.markdown("### 🎯 ネクストアクション")
    for a in data.get("next_actions", []):
        priority = a.get("priority", "")
        if isinstance(priority, int):
            priority_label = ["🔴 URGENT", "🟡 HIGH", "🟢 NORMAL"][min(priority - 1, 2)] if priority <= 3 else f"#{priority}"
        else:
            priority_label = f"{'🔴' if priority == 'URGENT' else '🟡' if priority == 'HIGH' else '🟢'} {priority}"
        
        st.markdown(f"""
        <div class="action-card">
            <span style="font-size:11px;color:#60a5fa;font-weight:700;">{priority_label}</span><br>
            <strong style="color:#e2e8f0;">{a['action']}</strong><br>
            <span style="color:#94a3b8;font-size:13px;">{a.get('rationale', a.get('deadline', ''))}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── RAG比較結果
    if "rag_comparison" in data and data["rag_comparison"]:
        st.divider()
        st.markdown("### 🧬 集合知RAG — トップセールスとの比較分析")
        rag = data["rag_comparison"]
        st.markdown(f"""
        <div class="rag-insight">
            <div style="margin-bottom:16px;">
                <span style="font-weight:700;color:#a78bfa;font-size:14px;">📊 類似パターン</span><br>
                <span style="color:#e2e8f0;">{rag.get('similar_patterns', 'データ不足')}</span>
            </div>
            <div style="margin-bottom:16px;">
                <span style="font-weight:700;color:#f59e0b;font-size:14px;">⚡ トップセールスとの差分</span><br>
                <span style="color:#e2e8f0;">{rag.get('gaps', 'データ不足')}</span>
            </div>
            <div>
                <span style="font-weight:700;color:#10b981;font-size:14px;">💡 具体的アドバイス</span><br>
                <span style="color:#e2e8f0;">{rag.get('specific_advice', 'データ不足')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# サイドバー
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar():
    """サイドバー描画"""
    with st.sidebar:
        st.markdown("## 🔦 Torch SaaS")
        st.caption("集合知RAG搭載 商談解析プラットフォーム")
        st.divider()

        # ── API キー
        st.markdown("### 🔑 Gemini API設定")
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="AIza...",
            help="Google AI StudioでAPIキーを取得してください",
        )
        if api_key:
            st.session_state["api_key"] = api_key
            st.success("✅ APIキー設定済み")
        
        st.divider()

        # ── Knowledge Base 管理
        st.markdown("### 📚 集合知ナレッジベース")
        st.caption("トップセールスの商談ログを蓄積して、比較分析の精度を向上させます")

        # アップロード
        kb_files = st.file_uploader(
            "成功事例をアップロード",
            type=["txt", "md", "vtt", "csv"],
            accept_multiple_files=True,
            key="kb_uploader",
            help="トップセールスの商談ログ（文字起こし）をアップロードしてください",
        )
        if kb_files:
            for uploaded in kb_files:
                save_path = KB_DIR / uploaded.name
                save_path.write_bytes(uploaded.getbuffer())
            st.success(f"✅ {len(kb_files)}件のファイルを保存しました")
            st.rerun()

        # ファイル一覧
        existing_files = get_kb_files()
        if existing_files:
            st.markdown(f"**蓄積済み: {len(existing_files)}件**")
            for f in existing_files:
                size_kb = f["size"] / 1024
                st.markdown(
                    f"""<div class="kb-file-card">
                        <span>📄</span>
                        <span style="flex:1;font-size:12px;color:#cbd5e1;">{f['name']}</span>
                        <span style="font-size:10px;color:#64748b;">{size_kb:.1f}KB</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
            
            if st.button("🗑 全ファイルを削除", type="secondary", use_container_width=True):
                for f in existing_files:
                    f["path"].unlink()
                st.success("削除しました")
                st.rerun()
        else:
            st.info("📂 まだ成功事例がありません。トップセールスの商談ログをアップロードしてください。")

        st.divider()
        st.caption("Powered by Accomp合同会社")
        st.caption("永沼メソッド × Gemini AI")

    return api_key


# ─────────────────────────────────────────────────────────────────────────────
# メイン
# ─────────────────────────────────────────────────────────────────────────────
def main():
    api_key = render_sidebar()

    # ── メインエリア
    tab1, tab2 = st.tabs(["📊 商談解析", "📋 解析結果（JSON）"])

    with tab1:
        st.markdown("## 📤 商談テキストをアップロード")
        st.caption("商談の文字起こしデータ（.txt, .vtt, .md）をアップロードすると、永沼メソッドに基づいてAIが自動解析します")

        uploaded = st.file_uploader(
            "商談データをアップロード",
            type=["txt", "vtt", "md"],
            key="main_uploader",
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            analyze_btn = st.button(
                "🚀 Gemini AIで解析",
                type="primary",
                use_container_width=True,
                disabled=(not uploaded or not api_key),
            )
        with col_btn2:
            demo_btn = st.button(
                "🎮 デモデータで表示",
                use_container_width=True,
            )

        if not api_key and not demo_btn:
            st.warning("⚠️ サイドバーでGemini APIキーを入力するか、「デモデータで表示」をクリックしてください")

        # ── 解析実行
        if analyze_btn and uploaded and api_key:
            transcript = uploaded.read().decode("utf-8")
            kb_count = len(get_kb_files())
            
            with st.status("🔦 Torch 解析中...", expanded=True) as status:
                st.write("📄 テキストを読み込みました")
                st.write(f"📚 集合知ナレッジベース: {kb_count}件の成功事例を参照")
                st.write("🤖 Gemini AI に送信中...")
                
                try:
                    result = analyze_with_gemini(transcript, api_key)
                    st.session_state["result"] = result
                    status.update(label="✅ 解析完了！", state="complete")
                except Exception as e:
                    status.update(label="❌ エラーが発生しました", state="error")
                    st.error(f"解析エラー: {str(e)}")
                    st.info("💡 APIキーが正しいか確認してください。また、テキストが長すぎる場合は短くしてみてください。")

        if demo_btn:
            st.session_state["result"] = DEMO_DATA

        # ── 結果表示
        if "result" in st.session_state:
            st.divider()
            render_dashboard(st.session_state["result"])

    with tab2:
        if "result" in st.session_state:
            st.json(st.session_state["result"])
        else:
            st.info("解析を実行すると、ここにJSON結果が表示されます")


if __name__ == "__main__":
    main()
