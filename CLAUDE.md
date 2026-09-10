# CLAUDE.md

Claude Code の学習資料。プロジェクトは 2 つだけで、直下に第 3 のフォルダを作らない。

- `claude-code-guide/` 基礎学習ドキュメント（全 6 章の静的 HTML。1 章 = 1 ファイル `chNN-*.html`）
- `claude-code-overview/` Claude Code の 1 枚絵（`claude-code-overview.html` が唯一のソース）

## 編集後に必ず実行する（リポジトリ直下で）

```bash
python3 claude-code-guide/tools/build_toc.py     # 章ファイルから目次 assets/toc.js を再生成
python3 claude-code-guide/tools/check_docs.py    # 「OK — 7 ページ、問題なし」が出るまで作業を終えない
python3 claude-code-guide/tools/build_single.py  # 配布用 1 枚 HTML dist/ を再生成
python3 claude-code-overview/export.py           # 1 枚絵を触ったときだけ。dist/ に SVG と PNG（Chrome が必要）
```

## 守ること

- **main に直接コミットしない。** `docs/`（本文）`fix/`（小修正）`chore/`（運用）のブランチを切り、PR で入れる。
- **1 章 1 ファイル。** 章ページには本文だけを置く。目次・ページャ・フッターは `assets/toc.js` から `nav.js` が描くので埋め込まない。
  共有ファイル（`index.html` `site.json` `assets/`）の変更は章の PR に混ぜない。
- **生成物は手で編集しない。** `assets/toc.js`、`dist/`、`index.html` の `<!-- OVERVIEW:START -->` 区間。
- **`check_docs.py` の規則。** `data-slide-title` と `<h3>N-M. …</h3>` の題名を完全一致、`<h3>` にタグを入れない、
  節 id は `sN-1` `sN-2` … の連番で N はファイル名の番号 = `data-chapter`。
- **範囲は 6 章の主題に固定。** サブエージェント・MCP・プラグイン・CI/CD・Agent SDK は扱わない。提案があっても足さない。
- **出典は公式ドキュメント。** 日本語版が古い箇所は英語版に従い注記する。数値は実測か公式。推測で置かない。
- **見た目はトークンだけ。** 色・文字サイズ・幅を HTML に `style=` で直書きしない。

## 詳細を読む場所（該当する作業の前に読む）

| したいこと | 読む |
|---|---|
| 章・節の追加、番号の付け替え、ファイル構成、書き方の方針、章の並びの意図 | [claude-code-guide/README.md](claude-code-guide/README.md) |
| 配色・フォント・文字サイズ・幅・部品（注記・試してみる・Source・図・表）の使い分け | [claude-code-guide/STYLE.md](claude-code-guide/STYLE.md) |
| ブランチ運用、PR、レビュー観点、生成物が衝突したときの直し方、Claude Code への頼み方 | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 追加コンテンツの候補、作業メモ、19 章版の旧版 | [claude-code-guide/_todo/README.md](claude-code-guide/_todo/README.md) |
| 1 枚絵の描き方の約束と書き出し | `claude-code-overview/claude-code-overview.html` 冒頭のコメント、`export.py` の docstring |
| 仕上げ手順 `/guide-check`、節の追加 `/guide-add-section`、章の照合レビュー `guide-reviewer` | [.claude/](.claude/) |
