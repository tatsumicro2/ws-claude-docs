## 変更の要約

<!-- 何を・なぜ。章・節は番号で示す（例: 7-3 に見出しを追加） -->

## 種類

- [ ] 本文の修正（誤り・古い記述の訂正）
- [ ] 節・章の追加
- [ ] 構成の変更（並び替え・改題）
- [ ] 概要図（claude-code-overview/）
- [ ] ツール・CI・運用まわり

## 出典

<!-- 仕様に関わる記述を変えた場合、根拠にした公式ドキュメントの URL。
     日本語版と英語版が食い違う箇所は英語版に従い、本文にその旨を注記したか -->

## 手元で確認したこと

- [ ] `python3 claude-code-guide/tools/build_toc.py` を実行した
- [ ] `python3 claude-code-guide/tools/check_docs.py` が `OK` を返す
- [ ] 本文を変えた場合、`python3 claude-code-guide/tools/build_single.py` で `claude-code-guide/dist/claude-code-guide.html` を更新した
- [ ] 節を足した／改題した場合、節 id が `sN-1` `sN-2` … の連番になっている
- [ ] `claude-code-overview/claude-code-overview.html` を触った場合、`python3 claude-code-overview/export.py` で SVG と PNG を書き出し直した
- [ ] ブラウザで表示を確認した
- [ ] Claude Code に書かせた箇所は自分で読み、出典の URL を開いて確かめた
