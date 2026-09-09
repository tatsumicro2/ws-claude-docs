#!/usr/bin/env python3
"""章の並びを一括で入れ替える。

renumber_chapter.py は 1 章ずつしか動かせず、番号が循環する並び替え
（例: 2→3 と 3→2 の入れ替え）を扱えない。本スクリプトは全章の対応表を
受け取り、全ファイルを一度に読んでから一度に書き出すことで、
任意の置換（permutation）を安全に適用する。

書き換える対象:
  - ファイル名               ch{旧:02d}-{slug}.html → ch{新:02d}-{slug}.html
  - 章の識別子               id="ch{旧}" data-chapter="{旧}"
  - 章番号の表示             <span class="chapter-num">{旧:02d}</span>
  - パンくずの章番号         第{旧}章
  - 節の識別子               id="s{旧}-M" / data-slide="{旧}-M"
  - 節の見出し番号           <h3>{旧}-M.
  - 章をまたぐリンクとアンカー ch{旧:02d}-*.html#s{旧}-M
  - 数字だけのリンク文字列     <a href="…#s{新}-M">{旧}-M</a> をリンク先に合わせる
  - 図番号                   figcaption の「図 {旧}-M」
  - toc.json                 chapters の並び順・num・file・sections[].id

実行後は build_nav.py でサイドバー・ページャ・章カードを再生成すること。

  python3 claude-code-guide/tools/reorder_chapters.py --dry-run
  python3 claude-code-guide/tools/reorder_chapters.py
"""
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

GUIDE = Path(__file__).resolve().parent.parent

# 新しい並び。値は「その位置に置く旧章番号」。
# 勉強会（週 1 回・10 分・全 18 回）のカリキュラム順に合わせた並び替え。
NEW_ORDER = [
    0,   # 0  この資料について        （据え置き）
    1,   # 1  Claude Code とは
    3,   # 2  基本操作とインターフェース  ← 旧 3
    2,   # 3  コアメカニズム            ← 旧 2
    4,   # 4  記憶と指示
    14,  # 5  ベストプラクティス        ← 旧 14
    15,  # 6  進行状況の可視化          ← 旧 15
    13,  # 7  コストと運用監視          ← 旧 13
    18,  # 8  用語集                   ← 旧 18
    5,   # 9  拡張レイヤーの全体像      ← 旧 5
    6,   # 10 Skills
    7,   # 11 Subagents と並列実行
    8,   # 12 Hooks
    9,   # 13 MCP
    10,  # 14 Plugins とマーケットプレイス
    11,  # 15 設定・権限・セキュリティ
    12,  # 16 自動化・CI/CD・Agent SDK
    16,  # 17 学習ロードマップ
    17,  # 18 情報ソース一覧
]

# 旧番号 → 新番号
REMAP = {old: new for new, old in enumerate(NEW_ORDER)}


def build_slug_table():
    """旧章番号 → slug（ファイル名の後半）"""
    table = {}
    for path in GUIDE.glob("ch[0-9][0-9]-*.html"):
        num = int(path.name[2:4])
        table[num] = path.name.split("-", 1)[1]
    return table


def rewrite(doc):
    """1 ファイル分の本文を、旧番号から新番号へ一括で書き換える。"""

    def ch_num(m):
        return "ch%02d-%s" % (REMAP[int(m.group(1))], m.group(2))

    # ch07-subagents.html のようなファイル参照
    doc = re.sub(r"ch(\d{2})-([a-z0-9-]+\.html)", ch_num, doc)
    # #s7-1 のようなアンカー
    doc = re.sub(r"#s(\d+)-(\d+)", lambda m: "#s%d-%s" % (REMAP[int(m.group(1))], m.group(2)), doc)
    # id="s7-1"
    doc = re.sub(r'id="s(\d+)-(\d+)"',
                 lambda m: 'id="s%d-%s"' % (REMAP[int(m.group(1))], m.group(2)), doc)
    # data-slide="7-1"
    doc = re.sub(r'data-slide="(\d+)-(\d+)"',
                 lambda m: 'data-slide="%d-%s"' % (REMAP[int(m.group(1))], m.group(2)), doc)
    # <h3>7-1.
    doc = re.sub(r"<h3>(\d+)-(\d+)\.",
                 lambda m: "<h3>%d-%s." % (REMAP[int(m.group(1))], m.group(2)), doc)
    # 図番号（figcaption の「図 7-1」）。図は節番号で採番されている
    doc = re.sub(r"図 (\d{1,2})-(\d{1,2})",
                 lambda m: "図 %d-%s" % (REMAP[int(m.group(1))], m.group(2)), doc)
    # id="ch7" data-chapter="7"
    doc = re.sub(r'id="ch(\d+)" data-chapter="\1"',
                 lambda m: 'id="ch%d" data-chapter="%d"'
                 % (REMAP[int(m.group(1))], REMAP[int(m.group(1))]), doc)
    # <span class="chapter-num">07</span>
    doc = re.sub(r'(<span class="chapter-num">)(\d{2})(</span>)',
                 lambda m: "%s%02d%s" % (m.group(1), REMAP[int(m.group(2))], m.group(3)), doc)
    # パンくず・ページャの「第7章」
    doc = re.sub(r"第(\d+)章",
                 lambda m: "第%d章" % REMAP[int(m.group(1))] if int(m.group(1)) in REMAP else m.group(0),
                 doc)
    return doc


LINK_RE = re.compile(r'(<a href="[^"]*?#s(\d+)-(\d+)">)([^<]*)(</a>)')


def sync_link_labels(doc):
    """「6-1」「6 章」のような数字だけのリンク文字列を、リンク先の番号に合わせる。

    href は rewrite() が書き換えるが、表示文字列は本文なので追随しない。
    ここで href を正として揃える。数字以外を含むラベルには触らない。
    """
    def fix(m):
        chapter, section, label = m.group(2), m.group(3), m.group(4)
        if re.fullmatch(r"\d+-\d+", label):
            label = "%s-%s" % (chapter, section)
        elif re.fullmatch(r"\d+ 章", label):
            label = "%s 章" % chapter
        else:
            return m.group(0)
        return m.group(1) + label + m.group(5)

    return LINK_RE.sub(fix, doc)


def rewrite_toc(toc):
    by_num = {ch["num"]: ch for ch in toc["chapters"]}
    chapters = []
    for new_num, old_num in enumerate(NEW_ORDER):
        ch = dict(by_num[old_num])
        ch["num"] = new_num
        ch["file"] = "ch%02d-%s" % (new_num, ch["file"].split("-", 1)[1])
        ch["sections"] = [
            {"id": re.sub(r"^s\d+-", "s%d-" % new_num, s["id"]), "title": s["title"]}
            for s in ch["sections"]
        ]
        chapters.append(ch)
    return {**toc, "chapters": chapters}


def main(dry_run=False):
    slugs = build_slug_table()
    missing = set(REMAP) - set(slugs)
    if missing:
        raise SystemExit("対応する章ファイルがありません: %s" % sorted(missing))

    # 全ファイルを先に読んでから書き出す（番号の循環で上書き事故を起こさないため）
    sources = {p.name: p.read_text(encoding="utf-8") for p in GUIDE.glob("*.html")}
    outputs = {}
    for name, doc in sources.items():
        if name == "index.html":
            outputs[name] = sync_link_labels(rewrite(doc))
        else:
            old_num = int(name[2:4])
            new_name = "ch%02d-%s" % (REMAP[old_num], name.split("-", 1)[1])
            outputs[new_name] = sync_link_labels(rewrite(doc))

    toc = json.loads((GUIDE / "toc.json").read_text(encoding="utf-8"))
    new_toc = rewrite_toc(toc)

    for new_num, old_num in enumerate(NEW_ORDER):
        if new_num != old_num:
            print("ch%02d-%s  →  ch%02d-%s" % (old_num, slugs[old_num], new_num, slugs[old_num]))
    if dry_run:
        print("\n--dry-run のため書き込みは行いませんでした。")
        return

    # いったん退避してから書き出す（旧ファイル名と新ファイル名の衝突を避ける）
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for name, doc in outputs.items():
            (tmp / name).write_text(doc, encoding="utf-8")
        for p in GUIDE.glob("*.html"):
            p.unlink()
        for name in outputs:
            shutil.copy2(tmp / name, GUIDE / name)

    (GUIDE / "toc.json").write_text(
        json.dumps(new_toc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("\n書き換え完了。claude-code-guide/tools/build_nav.py を実行してください。")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
