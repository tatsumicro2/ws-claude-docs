# 貢献の手引き

このリポジトリを複数人で育てるための約束事。**「守らないと壊れること」は [CLAUDE.md](CLAUDE.md)**、
**資料の構造と編集の手順は [claude-code-guide/README.md](claude-code-guide/README.md)** にある。
ここには作業の流れ・レビュー・Claude Code の使い方を書く。

リポジトリのプロジェクトは 2 つ。**`claude-code-guide/`（基礎学習ドキュメント）と `claude-code-overview/`（1 枚絵）**。
スクリプト・生成物・作業メモはすべて各プロジェクトのフォルダの中に置き、直下に第 3 のフォルダを作らない。

## 作業の流れ

```
main から枝を切る → 編集 → 手元で検証 → PR → CI とレビュー → マージ → 枝を消す
```

1. **main に直接コミットしない。** 必ずブランチを切る
   ```bash
   git switch main && git pull
   git switch -c docs/<topic>
   ```
2. 編集する。資料本体なら `claude-code-guide/chNN-*.html`、概要図なら `claude-code-overview/claude-code-overview.html`
3. **手元で検証する**（下の「マージ前に通すもの」）
4. push して PR を出す。テンプレートのチェック項目をすべて埋める
   ```bash
   git push -u origin docs/<topic>
   gh pr create
   ```
5. CI（`check`）が緑で、1 人のレビューが付いたらマージする。マージ後にブランチは削除する

### ブランチ名

| 接頭辞 | 用途 |
|---|---|
| `docs/` | 資料本文・概要図の追加や修正（ほとんどの作業はこれ） |
| `fix/` | リンク切れ・番号ずれなどの小さな修正 |
| `chore/` | ツール・CI・設定・運用まわり |

### コミットメッセージ

`<type>: <説明>` の 1 行。type は `docs` `fix` `feat` `refactor` `chore` `ci`。
説明は日本語でよい。**どの章・節を変えたかを番号で示す**（例 `docs: 7-3 にプロンプトキャッシュの図を追加`）。

## マージ前に通すもの

| 変えたもの | 実行するもの |
|---|---|
| 章 HTML | `python3 claude-code-guide/tools/build_toc.py` → `check_docs.py` → `build_single.py` |
| site.json, assets/*.css, *.js | `build_toc.py` → `build_single.py` |
| claude-code-overview/claude-code-overview.html | `python3 claude-code-overview/export.py`（PNG の書き出しに Google Chrome が必要）→ `build_toc.py` と `build_single.py`（表紙の概要図も更新される） |
| claude-code-guide/tools/*.py | 上の全部を回して差分が出ないこと |

CI は「生成物が最新か」と「check_docs.py が通るか」を検査する。手元で回さずに push すると赤くなる。

## 生成物と元ファイル

生成物は手で編集しない。元ファイルを直して再生成する。

| 生成物 | 元ファイル | 生成コマンド |
|---|---|---|
| `claude-code-guide/assets/toc.js`（目次データ） | 各 `chNN-*.html` と `site.json` | `claude-code-guide/tools/build_toc.py` |
| `index.html` の `<!-- OVERVIEW -->` 区間（概要図） | `claude-code-overview/claude-code-overview.html` | `claude-code-guide/tools/build_toc.py` |
| `claude-code-guide/dist/claude-code-guide.html` | `claude-code-guide/*.html` | `claude-code-guide/tools/build_single.py` |
| `claude-code-overview/dist/claude-code-overview.svg` `.png` | `claude-code-overview/claude-code-overview.html` | `claude-code-overview/export.py` |

章ページは 1 章 1 ファイルで完結していて、目次・ページャ・フッターは表示時に `nav.js` が描きます。
**別々の章を同時に編集しても元ファイルは衝突しません。** 衝突するのは生成物だけです。

### 衝突したとき

生成物は複数人の変更が同時に入ると必ず衝突する。**中身を手で解決しない。**

```bash
git merge main                                   # 衝突が出る
git checkout --theirs claude-code-guide/assets/toc.js claude-code-guide/dist/claude-code-guide.html   # 生成物はどちらでもよい（後で作り直す）
# 元ファイル（chNN-*.html）の衝突は手で解決する。別々の章を触っていれば起きない
python3 claude-code-guide/tools/build_toc.py && python3 claude-code-guide/tools/check_docs.py && python3 claude-code-guide/tools/build_single.py
git add -A && git commit
```

## レビューの観点

レビュアーは次を見る。書き手は PR を出す前に自分で見ておく。

- **出典。** 仕様に関わる記述は公式ドキュメントに根拠があるか。日本語版が英語版より古い箇所は英語版に従い、注記があるか
- **数値。** 上限・既定値・トークン数などは実測か公式の記載か。推測で置かれていないか
- **並び。** 章の順序は勉強会のカリキュラム順（認知負荷の小さい順）。体系上の分類で並べ直していないか
- **表。** 順序のある軸は上ほど高い／強い／深いか
- **「試してみる」。** シェルコマンドとセッション内コマンドが混在していないか
- **持ち帰り。** 章を足したら「この章の持ち帰り」節があるか
- **表示。** ブラウザで開いて崩れていないか（レビュアーも手元で開く）。色・文字サイズ・幅を HTML に直書きしていないか（[STYLE.md](claude-code-guide/STYLE.md)）

## Claude Code で作業する

このリポジトリの作業はほぼ Claude Code で行う。`.claude/` にチーム共有の設定が入っていて、
クローンすればそのまま効く。

| 場所 | 中身 |
|---|---|
| `CLAUDE.md` | 毎セッション読み込まれる規約。**守らないと壊れること**だけを書く。増やすときは相談する |
| `.claude/settings.json` | 共有の権限（claude-code-guide/tools/*.py・claude-code-overview/export.py と git の読み取り系を確認なしで実行可）とフック。`git push --force` は拒否 |
| `.claude/hooks/` | 章 HTML を編集した直後と作業終了時に `check_docs.py` を回し、失敗なら Claude に指摘を返して直させる |
| `.claude/skills/guide-check` | `/guide-check` — build_toc → check_docs → build_single の仕上げ手順 |
| `.claude/skills/guide-add-section` | `/guide-add-section` — 節を追加する手順（書式・番号付け替え） |
| `.claude/agents/guide-reviewer` | 章を公式ドキュメント英語版と突き合わせ、`claude-code-guide/_todo/review-*.md` にレビューノートを書く。本文は変えない |

個人の設定（追加の許可、個人用フックなど）は `.claude/settings.local.json` に書く。gitignore 済み。

### 頼み方の目安

- 章・節は番号で指定する（「7-3 の表を直して」）。ファイル名より確実
- 仕様を書かせるときは「公式の英語版を根拠に、URL を添えて」と言う。出典なしで書かれた仕様は信用しない
- 終わりに `/guide-check` を実行させる。フックも回るが、明示したほうが確実
- **Claude が書いた出典 URL は自分で開く。** 存在しないページやズレた節を指すことがある

### してはいけないこと

- `assets/toc.js` や `index.html` の `<!-- OVERVIEW -->` 区間を Claude に直接編集させる（`build_toc.py` で上書きされる）
- 章ページに目次・ページャ・フッターを手で埋め込む（他章との結合が戻る）
- 章番号を手で付け替える（`claude-code-guide/tools/renumber_chapter.py` を使う）

## Issue と作業メモ

- 記述の誤りや追加提案は Issue テンプレートから出す（「記述の誤り・古い記述」「節・章の追加提案」）
- 追加コンテンツの候補一覧は [claude-code-guide/_todo/README.md](claude-code-guide/_todo/README.md) に集約する
- レビュー結果・計画・旧版は [`claude-code-guide/_todo/`](claude-code-guide/_todo/) に置く（命名規則はそこの README）

## 管理者向け：初回セットアップ

リポジトリ管理者が 1 度だけ行う。ブランチ保護（ルールセット）で、
main への直接 push と force push を禁止し、PR に CI の緑と 1 人の承認を必須にする。

```bash
gh api -X POST repos/tatsumicro2/ws-claude-docs/rulesets --input - <<'JSON'
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "pull_request",
      "parameters": { "required_approving_review_count": 1, "dismiss_stale_reviews_on_push": true,
                      "require_code_owner_review": false, "require_last_push_approval": false,
                      "required_review_thread_resolution": false, "allowed_merge_methods": ["merge", "squash"] } },
    { "type": "required_status_checks",
      "parameters": { "strict_required_status_checks_policy": true,
                      "required_status_checks": [ { "context": "check" } ] } }
  ]
}
JSON
```

- メンバーが 2 人以下のうちは `required_approving_review_count` を `0` にしてもよい（CI の緑だけを必須にする）
- 資料を URL で配りたくなったら GitHub Pages（Settings → Pages → Source: GitHub Actions）を有効にし、
  `claude-code-guide/` を配信するワークフローを足す。現時点では未設定
