# Claude Code 体系的入門

Claude Code の全分野を、Anthropic 公式ドキュメント（`code.claude.com/docs/ja`）と
Claude Academy を一次情報源として整理した学習資料。全 19 章（0〜18 章）／112 節。

`index.html` をブラウザで開くと読める（外部依存なし）。

## 構成

```
claude-code-guide/
├── index.html              トップページ（章インデックス）
├── ch00-about.html … ch18-sources.html    章ごとのページ（1ページ＝1章）
├── toc.json                目次データ ← 章・節の構成はここが唯一のソース
├── assets/
│   ├── style.css           本文デザイン（元の 1 枚 HTML から抽出、無改変）
│   ├── app.js              コードブロックのコピー機能（同上）
│   ├── nav.css             サイドバー・ページャ・章カードのスタイル
│   └── nav.js              サイドバーの開閉・スクロール位置の維持・節のハイライト
│                           （CSS / JS は build_nav.py が内容ハッシュを ?v= で付与）
├── _source/index.html      分解前の 1 枚 HTML（内容比較の基準として保存）
├── tools/                  ビルドと検証のスクリプト（Python 3 標準ライブラリのみ）
├── dist/claude-code-guide.html   全章を 1 枚に結合した配布用 HTML（build_single.py の生成物。手で編集しない）
├── _todo/                  レビュー結果・計画・旧版などの作業メモ（資料の一部ではない）
└── TODO.md                 追加コンテンツの候補一覧
```

スクリプトは**リポジトリ直下で** `python3 claude-code-guide/tools/<名前>.py` として実行する（どこから実行しても動くが、表記はこれに揃える）。

ドキュメントは **2 階層**（章 → 節）。左サイドバーには常に全 19 章が並び、
現在の章はその節まで展開される。他の章は見出し右の `›` で開閉できる。

## 章の並び

章の順序は、社内勉強会（週 1 回・10 分・全 18 回）のカリキュラムに合わせて
**認知負荷の小さい順・実務で早く効く順**に並べている。体系上の分類順ではない。

| 幕 | 章 | ねらい |
|---|---|---|
| まず動かす | 1〜4 | 全体像 → 基本操作 → コアメカニズム → CLAUDE.md |
| うまく使う | 5〜8 | ベストプラクティス → 可視化 → コスト → 用語集（拡張の予習） |
| 拡張する | 9〜14 | 全体像 → Skills → Subagents → Hooks → MCP → Plugins |
| チームに広げる | 15〜18 | 設定と権限 → 自動化 → ロードマップ → 情報ソース |

並びを変えるときは `toc.json` を手で編集せず、`claude-code-guide/tools/reorder_chapters.py` の
`NEW_ORDER` を書き換えて実行し、`build_nav.py` → `check_docs.py` の順で回す。

## 編集の仕方

### 本文を直すとき

該当する `chNN-*.html` を直接編集する。ナビゲーション部分は
HTML コメントのマーカーで囲まれているので、そこ以外を触る分には何もしなくてよい。

```html
<!-- NAV:START -->   … 左サイドバー（全ページ共通・自動生成）
<!-- PAGER:START --> … 前後の章リンク（自動生成）
<!-- INDEX:START --> … 章カード一覧（index.html のみ・自動生成）
```

### 節を追加・改題したとき

1. 章ページに `<article class="slide" id="sN-M" data-slide="N-M" data-slide-title="…">` を追加する
2. `toc.json` の該当章の `sections` に `{"id": "sN-M", "title": "…"}` を追記する
3. `python3 claude-code-guide/tools/build_nav.py` を実行して全ページのサイドバーを更新する

### 章を追加したとき

1. 既存の章 HTML をコピーして `chNN-<slug>.html` を作り、本文を差し替える
2. **末尾に「この章の持ち帰り」節を用意する**（全章に揃えてある。実務での効き目と豆知識を書く枠）
3. `toc.json` の `chapters` にエントリを追記する
4. `python3 claude-code-guide/tools/build_nav.py` を実行する

### 編集を終える前に

```bash
python3 claude-code-guide/tools/check_docs.py    # OK が出るまで終えない
python3 claude-code-guide/tools/build_single.py  # 本文を変えたら dist/ を作り直す
```

## ツール

| スクリプト | 用途 |
|---|---|
| `tools/build_nav.py` | `toc.json` から全ページのナビ・ページャ・章カードを再生成（冪等） |
| `tools/check_docs.py` | 内部リンク・アンカー・タグの対応・見出し番号・節タイトルを検証。**編集後は必ず通す** |
| `tools/split_guide.py` | 1 枚 HTML を章ごとに分解した初回実行用スクリプト（記録として保存） |
| `tools/renumber_chapter.py` | 章番号を 1 つだけ付け替える（ファイル名・id・見出し・参照リンクを一括更新）。大きい番号から順に実行する |
| `tools/reorder_chapters.py` | 章の並びをまとめて入れ替える。番号が循環する並び替えを、全ファイルを一度に読み書きして安全に適用する |
| `tools/build_single.py` | 全章を 1 枚の自己完結 HTML（CSS / JS 埋め込み、章間リンクはページ内アンカー）に結合して `dist/claude-code-guide.html` に出力する。配布・印刷用 |
| `tools/add_takeaways.py` | 各章末の「この章の持ち帰り」節を生成した初回実行用スクリプト（記録として保存） |

## 出典

記述内容は [Claude Code 公式ドキュメント](https://code.claude.com/docs/ja/overview) を一次情報源としている。
**日本語版が英語版より古い箇所は [英語版](https://code.claude.com/docs/en/overview) に従い**、該当箇所に注記を添えている
（作成時に、権限モードの既定・非対話実行時の挙動・サブエージェントの上限など複数の食い違いを確認済み）。
コミュニティ資料は事例収集にのみ使い、仕様の根拠にはしない。方針の全文は 0-2 節にある。

学習用にまとめた非公式の整理資料であり、Anthropic による公式配布物ではない。
