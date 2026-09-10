# 追加コンテンツ TODO

調査日: 2026-08-29 ／ 最終更新: 2026-09-04 ／ 対象: `claude-code-guide`

> **章番号について**：2026-09-04 に勉強会カリキュラムの順序へ全章を並び替えた
> （`tools/reorder_chapters.py`）。本ファイルの `chNN` は**すべて新番号**に更新済み。
> 対応は 旧2→新3、旧3→新2、旧5〜12→新9〜16、旧13→新7、旧14→新5、旧15→新6、
> 旧16→新17、旧17→新18、旧18→新8（旧1・旧4 は据え置き）。

- 一次情報源: [公式ドキュメント索引 `llms.txt`](https://code.claude.com/docs/llms.txt)（全 120 ページ超）、
  [Claude Academy](https://academy.claude.com)（Claude Code トラック 4 コース）
- 表記: `新規` = 節を新設 ／ `増補` = 既存節に追記

## 完了済み

| 内容 | 反映先 |
|---|---|
| 言語ごとのトークン消費と、作業完了までの総消費 | ch07 を 4 節 → 8 節に再構成（7-3 トークンの数え方と言語による差／7-4 1 タスクを終えるまでの総消費／7-5 プロンプトキャッシュ／7-7 長時間セッションで使用量が膨らむ理由 を新設。7-2 と 7-6 を増補） |
| AskUserQuestion と基本ツール | ch03-3 を全 45 ツール・8 カテゴリに拡張、ch03-7「主要ツールの個別挙動と落とし穴」を新設。AskUserQuestion は他のツールと同格の扱いとし、専用節は設けなかった |
| ワークフローの可視化・チェックリスト・進捗 | **新章 ch06「作業の可視化と進行管理」**（7 節）を新設。動的ワークフロー、タスクツールの既定無効、`/goal`、エージェントビュー、ステータスラインを収録。付録 3 章を旧 ch16〜18 へ繰り下げ |

## 残タスク 1. 公式ドキュメント／Academy にあって本ドキュメントに無い事柄

公式索引の全ページと突き合わせた結果。**スラッシュコマンドは公式 110 個中 42 個が未出**、
**ツールは 45 個中 20 個が未出**。以下は優先度順。

### 優先度 A — 本編に節を足すべき（実務で頻繁に効く）

| 事項 | 提案配置 | 備考 |
|---|---|---|
| worktree による並列セッション隔離 | ch11 に `新規` 節 | `--worktree`、`.worktreeinclude`、サブエージェントの `isolation` |
| エージェントチーム / クロスセッションメッセージング | ch11 に `新規` 節 | 実験的・既定無効。コストが跳ねる点も |
| セッション管理の詳細 | ch03-6 `増補` | `--from-pr`、`/rename`、`/resume` ピッカー、トランスクリプトの書き出し先 |
| Auto mode（自動モード） | ch02-4 `増補` | 分類器がプロンプトを裁く仕組み。`auto-mode-config` |
| サンドボックス環境の選択 | ch15-4 `増補` | 組み込みサンドボックス／dev container／Docker／VM の比較 |
| 大規模コードベース・モノレポ設定 | ch05 or ch04 に `新規` | ネストした CLAUDE.md、sparse worktree、パッケージ単位スキル |
| 設定の完全リファレンス／環境変数／エラー一覧 | ch15 と ch07 に参照追加 | `settings-reference` `env-vars` `errors` |
| 設定が効かないときの診断 | ch04-6 `増補` | `/context` `/doctor` `/hooks` `/mcp` で実際に読まれた物を見る |

### 優先度 B — 節を足すか、章に一覧として載せる

| 事項 | 提案配置 |
|---|---|
| Artifacts（成果物を claude.ai のページとして共有） | ch16 に `新規` |
| Routines（クラウド定期実行）／デスクトップ定期タスク／`/loop`／deep links | ch16-3 `増補`（現状は薄い） |
| Channels（外部イベントをセッションに投入） | ch16 に `新規` |
| Chrome 連携／computer use | ch01-2 `増補` ＋ ch16 に `新規` |
| Remote Control／モバイル／Dispatch／Teleport | ch01-2 `増補` |
| Slack／Claude Tag | ch01-2 `増補` |
| Code Review／ultrareview／security-guidance／Claude Security プラグイン | ch16-2 `増補` |
| モデル設定の詳細（拡張コンテキスト、autocompact 窓、fast mode、advisor） | ch03-2 `増補` |
| Output styles（ソフトウェア以外の用途に振る） | ch02 に `新規` |
| プロンプトライブラリ | ch18（情報ソース）に追加 |

### 優先度 C — 参照リンクのみで足りる（本編には書かない）

ゲートウェイ各種、self-hosted environments、cloud environments、Bedrock / Google Cloud / Microsoft Foundry、
network config、corporate launcher、devcontainer、zero data retention、feature availability、
managed settings / server-managed settings / managed MCP、analytics、communications kit / champion kit、
plugin dependencies / hints / relevance、アクセシビリティ、キーバインド、フルスクリーン、音声入力、ターミナル設定。

→ **ch18「情報ソース一覧」に「用途別・公式ドキュメント逆引き表」を新設**して受ける（`新規` 18-4）。

### Academy との差分

Claude Code トラックは 4 コース。本ドキュメントの守備範囲はおおむね上位互換だが、以下は未反映。

- **Claude Code 101** — 12 レッスン。ほぼ網羅済み。
- **Claude Code in Action** — 9 レッスン。うち **「Verification skills（検証スキル）」** と
  **「Trust it: 無人実行の検証」** が本ドキュメントに無い観点。
  → ch05「ベストプラクティス」に `新規` 節「無人で走らせるための検証設計」を立てる。
- **Introduction to Agent Skills** — ch10 で概ねカバー。
- **Introduction to Subagents** — 「構造化された出力」「ツールアクセスの限定」で
  信頼できるサブエージェントを設計する観点は ch11-2 を `増補` する価値あり。

---

## 残タスク 2. 世の中の情報から、仕事に直結するトピック

一次情報として質が高いのは **Anthropic Engineering ブログ**。コミュニティ記事は玉石混交で、
数値や仕様の記述が古いものが多いため、本ドキュメントには**原則として公式ソースのみ**を引く方針を維持する。

**配置: ch05「ベストプラクティス」に 3 節を `新規` 追加 ＋ ch18 に出典を追加**

### 5-6 コンテキストエンジニアリング `新規`

「必要になった時点で取りに行く（just-in-time）」設計。全部を前もって詰め込まず、
ファイルパス・クエリ・リンクといった**軽い識別子**を持たせ、ツールで実体を引かせる。
本ドキュメントの既存記述（スキルのオンデマンド化、MCP のツール検索、コードインテリジェンス）を
1 つの原則の下に束ね直す節にする。

出典: [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)、
[The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)

### 5-7 エージェントに渡すツールの設計 `新規`

MCP サーバーやカスタムツールを自作するとき、**API をそのまま薄くラップしたツールは効かない**。
ツールは多ければよいものではなく、評価（eval）を書いて Claude 自身に改善させる手法がある。
自作 MCP・スキルを持つチーム向けの実務ノウハウ。

出典: [Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)、
[Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 5-8 長時間・無人実行のためのハーネス設計 `新規`

コンテキストウィンドウに収まらない規模の作業を、
**環境を整える初期化エージェント + 少しずつ進めるコーディングエージェント**に分けて橋渡しする設計。
`/goal`、動的ワークフロー、検証スキル、Stop フックを「無人で回すための部品」として接続する。
Academy の「Trust it: 無人実行の検証」もここに合流させる。

出典: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)、
[Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)

### 18-2 準公式・学習リソース `増補`

Anthropic Engineering ブログの主要記事、[Claude Cookbook](https://platform.claude.com/cookbook)、
Claude Academy の 4 コースを一次情報として追加する。

---

## 着手順の提案

| 段 | 内容 |
|---|---|
| 1 | 残タスク 1 の**優先度 A**（worktree、エージェントチーム、auto mode、セッション詳細、大規模コードベースほか） |
| 2 | 残タスク 2（ch05 に 3 節追加）＋ ch18「情報ソース一覧」に用途別の逆引き表を新設し、優先度 C の受け皿にする |
| 3 | 残タスク 1 の**優先度 B** を順次 |

各段の完了後に `toc.json` 更新 → `python3 claude-code-guide/tools/build_nav.py` → ブラウザ表示確認、を回す。
