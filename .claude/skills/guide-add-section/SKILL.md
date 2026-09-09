---
name: guide-add-section
description: claude-code-guide に節を追加するときの手順。「N 章に節を足したい」「〜の節を新設して」と言われたときに使う。article の書式、toc.json への追記、番号の付け替え、check_docs.py が要求する規則をまとめてある。
---

# 節を追加する手順

## 1. 置き場所を決める

- 各章の末尾は「この章の持ち帰り」節。新しい節は**その手前**に入れる
- 途中に入れて以降の節番号がずれる場合、ずれる節すべてについて次を更新する
  - `id="sN-M"` `data-slide="N-M"` `<h3>N-M.` の 3 か所
  - 他の章からのリンク `chNN-*.html#sN-M`（`grep -rn '#sN-' claude-code-guide/*.html` で洗う）
  - 本文中の「N-M 節」のような素の番号参照（grep で拾えないので目視）

## 2. article を書く

```html
  <article class="slide" id="sN-M" data-slide="N-M" data-slide-title="節タイトル">
    <h3>N-M. 節タイトル</h3>
    …本文…
    <div class="src">
      <span class="label">Source</span>
      …出典へのリンク…
    </div>
  </article>
```

check_docs.py が落ちる書き方：

- `data-slide-title` と `<h3>` のタイトルが一致していない（完全一致が必要）
- `<h3>` の中にタグがある（`<strong>` も不可）
- `data-slide` と `<h3>` の番号が違う

書き方の方針（CLAUDE.md より）：

- 出典は公式ドキュメント。日本語版が英語版より古い箇所は英語版に従い、その旨を注記する
- バージョン依存の記述には `v2.1.x 以降` のように条件を添える
- 表で順序のある軸を扱うときは、上ほど高い／強い／深い
- 「試してみる」ブロックでは、シェルコマンドとセッション内コマンドを混ぜない
- 数値は手元で実測できるものだけ書く。推測で置かない

## 3. toc.json に追記する

該当章の `sections` の**同じ位置**に `{"id": "sN-M", "title": "節タイトル"}` を足す。
toc.json の並びと実ページの並びが一致していないと check_docs.py が落ちる。

## 4. 仕上げる

`/guide-check` を実行する（build_nav.py → check_docs.py → build_single.py）。
