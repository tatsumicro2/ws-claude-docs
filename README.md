# ws-claude / docs

Claude Code を学ぶための資料。プロジェクトは 2 つ。

| ディレクトリ | 内容 |
|---|---|
| [`claude-code-guide/`](claude-code-guide/) | **基礎学習ドキュメント** — 全 6 章の静的 HTML。`index.html` を開けば読める |
| [`claude-code-overview/`](claude-code-overview/) | **Claude Code の 1 枚絵** — `claude-code-overview.html` が唯一のソース。`export.py` が `dist/` に SVG / PNG を書き出す |

```bash
open claude-code-guide/index.html                    # 学習ドキュメント
open claude-code-guide/dist/claude-code-guide.html   # 同じ内容の 1 枚 HTML（配布・印刷用）
open claude-code-overview/claude-code-overview.html  # 1 枚絵
```

外部依存はない。記述は Anthropic 公式ドキュメントを一次情報源とし、日本語版が古い箇所は英語版に従う。
学習用にまとめた非公式の整理資料であり、Anthropic による公式配布物ではない。

## 編集する

| 目的 | 読む |
|---|---|
| 編集後に必ず実行するコマンドと、守るべき規則 | [CLAUDE.md](CLAUDE.md) |
| 章・節の追加、ファイル構成、書き方の方針 | [claude-code-guide/README.md](claude-code-guide/README.md) |
| 配色・フォント・幅の決まり | [claude-code-guide/STYLE.md](claude-code-guide/STYLE.md) |
| ブランチ運用、PR、レビュー、Claude Code での作業のしかた | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 追加コンテンツの候補・作業メモ | [claude-code-guide/_todo/README.md](claude-code-guide/_todo/README.md) |
