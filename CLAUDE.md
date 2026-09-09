# CLAUDE.md

Claude Code の学習資料リポジトリ。プロジェクトは 2 つだけ。`claude-code-guide/`（基礎学習ドキュメント・全 19 章 / 112 節の静的 HTML）と
`claude-code-overview/`（Claude Code の 1 枚絵）。それぞれのフォルダで完結させ、直下に第 3 のフォルダを作らない。
構成の全体像は [README.md](README.md)、編集手順の詳細は
[claude-code-guide/README.md](claude-code-guide/README.md) にある。ここには**守らないと壊れること**だけを書く。

## 編集後に必ず実行する

```bash
python3 claude-code-guide/tools/build_nav.py     # toc.json からナビ・ページャ・章カードを再生成
python3 claude-code-guide/tools/check_docs.py    # 検証。OK が出るまで作業を終えない
```

`build_nav.py` を飛ばすとサイドバーが古いまま残る。`check_docs.py` はリンク切れ・アンカー切れ・
タグの不整合・見出し番号のずれを検出する。**両方通してから完了とすること。**

## ブランチと生成物

- **main に直接コミットしない。** `docs/<topic>`（本文）`fix/`（小修正）`chore/`（ツール・運用）のブランチを切り、PR で入れる。
  流れとレビュー観点は [CONTRIBUTING.md](CONTRIBUTING.md)。
- `claude-code-guide/dist/claude-code-guide.html` は `build_single.py` の生成物。本文を変えたら再生成する。CI が古さを検出して落とす。
- `claude-code-overview/dist/` は `claude-code-overview/export.py` の生成物。`claude-code-overview.html` を変えたら `python3 claude-code-overview/export.py` で書き出し直す（PNG は Chrome が必要）。
- レビュー結果・計画・旧版などの作業メモは `claude-code-guide/_todo/` に置く（資料の一部ではない）。
- `.claude/` はチーム共有の設定（権限・フック・Skill・Subagent）。個人の設定は `.claude/settings.local.json` に書く（gitignore 済み）。
  仕上げは `/guide-check`、節の追加は `/guide-add-section`、章の照合レビューは `guide-reviewer` サブエージェント。

## 触ってはいけないもの

- `<!-- NAV:START -->` `<!-- PAGER:START -->` `<!-- INDEX:START -->` で囲まれた区間は自動生成。
  手で編集しても `build_nav.py` で上書きされる。
- `assets/*.css` `*.js` の `?v=` ハッシュ。`build_nav.py` が内容から自動で付ける。
- `claude-code-guide/_source/index.html` は分解前の原本。内容比較の基準として保存してあるもので、更新しない。

## `check_docs.py` が通らなくなる書き方

| 規則 | 理由 |
|---|---|
| `data-slide-title="X"` と `<h3>N-M. X</h3>` の X を完全一致させる | 突き合わせ検査がある |
| `<h3>` の中にタグを入れない（`<strong>` も不可） | 検査が `[^<]+` で読む |
| `data-slide="N-M"` と `<h3>N-M.` の番号を一致させる | 同上 |
| 節を足したら `toc.json` の `sections` にも追記する | 節タイトルの並びを突き合わせる |

## 章・節を動かすとき

- **章の並び替えは `claude-code-guide/tools/reorder_chapters.py`。** `NEW_ORDER` を書き換えて実行する。
  `renumber_chapter.py` は 1 章ずつしか動かせず、2↔3 のような循環する入れ替えを扱えない。
- 章番号を変えると**節 ID・図番号・章をまたぐリンク・アンカー・数字だけのリンク文字列**が
  すべて追随する。`reorder_chapters.py` はこれらを一括で書き換えるが、
  **本文中の素の番号（「詳細は 7 章」「5 〜 11 章」など）は拾えない**ので、実行後に手で確認する。
- `toc.json` が章・節構成の唯一のソース。手で書き換えず、スクリプト経由か、節追加時の追記に留める。

## 書き方の方針

- **出典は公式ドキュメント。日本語版が英語版より古い箇所は英語版に従い、その旨を注記する。**
  コミュニティ資料は事例収集にのみ使い、仕様の根拠にしない。
- バージョン依存の記述には `v2.1.x 以降` のように条件を添える。
- 表で順序のある軸（性能・コスト・優先度・容量）を扱うときは、**上ほど高い／強い／深い**で統一する。
- 「試してみる」ブロックは、シェルコマンドとセッション内コマンドを混ぜない。
- 数値や仕様を書くときは、可能なら手元で実測してから書く。推測で数字を置かない。

## この資料の設計意図

章の順序は**体系上の分類順ではなく、社内勉強会（週 1 回・10 分・全 18 回）のカリキュラム順**。
認知負荷の小さい順・実務で早く効く順に並べてある。ただし「第 N 週 = 第 N 章」という対応付けは**しない**（本文に書かない）。
並びを変えるときは、この意図を壊していないか確認すること（4 幕構成の意図は
[claude-code-guide/README.md](claude-code-guide/README.md) の「章の並び」にある）。

各章の末尾には「この章の持ち帰り」節がある。**実務での効き目と、意外と知られていない事実**を
書く枠で、章を追加したときは同じ体裁で用意する。
