# ws-claude / docs

Claude Code を学ぶための資料。プロジェクトは 2 つ。

| ディレクトリ | 内容 |
|---|---|
| [`claude-code-guide/`](claude-code-guide/) | **Claude Code 基礎学習ドキュメント** — 全 19 章 / 112 節の静的 HTML。ビルド・検証スクリプト（`tools/`）、配布用の 1 枚 HTML（`dist/`）、作業メモ（`_todo/`）もこの中にある |
| [`claude-code-overview/`](claude-code-overview/) | **Claude Code の 1 枚絵** — 中央に核（ハーネス）、周辺に関連要素を置いた概要図。`claude-code-overview.html` が唯一のソースで、`export.py` が `dist/` に SVG / PNG を書き出す |

それ以外の直下のファイルは運用のためのもの（`.claude/` は Claude Code のチーム共有設定、`.github/` は CI と PR / Issue テンプレート）。

## 読む

```bash
open claude-code-guide/index.html     # 学習ドキュメント（章ごとのページ）
open claude-code-guide/dist/claude-code-guide.html   # 同じ内容の 1 枚 HTML（配布・印刷用）
open claude-code-overview/claude-code-overview.html    # 1 枚絵
```

外部依存はない。ブラウザで開けばそのまま読める。

## 編集する

**学習ドキュメント**は `claude-code-guide/chNN-*.html` を直接編集する。編集したら必ず、リポジトリ直下で次を順に実行する。

```bash
python3 claude-code-guide/tools/build_nav.py       # toc.json から全ページのナビを再生成（冪等）
python3 claude-code-guide/tools/check_docs.py      # リンク・アンカー・見出し番号・節タイトルを検証
python3 claude-code-guide/tools/build_single.py    # dist/ の 1 枚 HTML を再生成
```

`check_docs.py` が `OK — 20 ページ、問題なし` を返さないうちは作業を終えない。
詳しい手順と章の並びの意図は [`claude-code-guide/README.md`](claude-code-guide/README.md) にある。

**1 枚絵**は `claude-code-overview/claude-code-overview.html` だけを編集する（図の約束と基準線は HTML 冒頭のコメントにある）。編集したら書き出し直す。

```bash
python3 claude-code-overview/export.py            # dist/claude-code-overview.svg と .png を書き出す（PNG は Google Chrome が必要）
```

## 複数人で編集する

main に直接コミットせず、`docs/<topic>` ブランチ → PR → CI とレビュー → マージ、の順で進める。
ブランチ名・コミットメッセージ・レビューの観点・生成物が衝突したときの直し方・Claude Code への頼み方は
[`CONTRIBUTING.md`](CONTRIBUTING.md) に、Claude Code で作業するときの規約は [`CLAUDE.md`](CLAUDE.md) にある。

## 出典の方針

記述は Anthropic 公式ドキュメントを一次情報源とする。**日本語版が英語版より古い箇所は英語版に従う**
（作成時に権限モードの既定や非対話実行時の挙動など複数の食い違いを確認済み）。
コミュニティ資料は事例収集にのみ使い、仕様の根拠にはしない。方針の全文は資料の 0-2 節にある。

学習用にまとめた非公式の整理資料であり、Anthropic による公式配布物ではない。
