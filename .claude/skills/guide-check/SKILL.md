---
name: guide-check
description: claude-code-guide を編集したあとの仕上げ。build_toc.py → check_docs.py → build_single.py を順に実行して生成物を最新にし、結果を報告する。「検証して」「仕上げて」「チェックして」と言われたとき、または資料の編集を終える直前に使う。
allowed-tools: Bash(python3 claude-code-guide/tools/build_toc.py:*), Bash(python3 claude-code-guide/tools/check_docs.py:*), Bash(python3 claude-code-guide/tools/build_single.py:*), Bash(git status:*), Bash(git diff:*)
---

# 資料の仕上げ手順

リポジトリ直下で、次を**この順で**実行する。途中で失敗したら先へ進まない。

1. `python3 claude-code-guide/tools/build_toc.py`
   各章ファイルから目次データ assets/toc.js を再生成する（冪等）。目次が古いと check_docs.py が落ちる
2. `python3 claude-code-guide/tools/check_docs.py`
   `OK — 7 ページ、問題なし` 以外が出たら、指摘をすべて直して 1 からやり直す
3. `python3 claude-code-guide/tools/build_single.py`
   `claude-code-guide/dist/claude-code-guide.html` を再生成する
4. `git status --short`
   変更ファイルを一覧し、意図しないファイルが混じっていないか確かめる

## 報告に含めること

- check_docs.py の結果（OK か、残った指摘の全文）
- 変更されたファイルの一覧
- `claude-code-overview/claude-code-overview.html` が変更に含まれる場合、`python3 claude-code-overview/export.py` で SVG / PNG を書き出し直す必要があると伝える（PNG は Chrome が必要）
