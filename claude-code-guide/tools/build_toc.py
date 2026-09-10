#!/usr/bin/env python3
"""章ファイル群から assets/toc.js を生成し、トップページに概要図を差し込む。

章ページには目次・ページャ・フッターの HTML を埋め込まない。
それらは assets/toc.js のデータから nav.js が表示時に描くので、
1 つの章を書き換えても他の章ファイルは変わらない。

生成・更新するもの
  assets/toc.js        章・節の一覧（各 chNN-*.html から抽出）と、site.json の資料名・フッター文言
  index.html           <!-- OVERVIEW:START --> 〜 <!-- OVERVIEW:END --> に claude-code-overview/ の SVG を差し込む

使い方（リポジトリ直下で）:
  python3 claude-code-guide/tools/build_toc.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guide_toc import GUIDE, load_toc, toc_js  # noqa: E402

OVERVIEW_RE = re.compile(r"(<!-- OVERVIEW:START -->).*?(<!-- OVERVIEW:END -->)", re.S)
OVERVIEW_SRC = GUIDE.parent / "claude-code-overview" / "claude-code-overview.html"


def overview_svg():
    """claude-code-overview の <svg> を取り出し、ガイドの CSS と干渉しないよう
    クラス名に ov- を付け、スタイルを #overview-landscape 配下に限定して返す。"""
    html = OVERVIEW_SRC.read_text(encoding="utf-8")
    svg = re.search(r"<svg.*</svg>", html, re.S).group(0)
    svg = re.sub(r'class="([^"]*)"',
                 lambda m: 'class="%s"' % " ".join("ov-" + c for c in m.group(1).split()), svg)

    def scope_style(m):
        rules = []
        for line in m.group(1).splitlines():
            t = line.strip()
            if not t:
                continue
            if t.startswith("@import"):
                rules.append("  " + t)
                continue
            t = re.sub(r"\.([A-Za-z_][\w-]*)", r".ov-\1", t)
            rules.append("  #overview-landscape " + t)
        return "<style>\n" + "\n".join(rules) + "\n</style>"
    return re.sub(r"<style>(.*?)</style>", scope_style, svg, count=1, flags=re.S)


def main():
    toc = load_toc()
    out = GUIDE / "assets" / "toc.js"
    out.write_text(toc_js(toc), encoding="utf-8")

    idx = GUIDE / "index.html"
    doc = idx.read_text(encoding="utf-8")
    if not OVERVIEW_RE.search(doc):
        raise SystemExit("index.html に <!-- OVERVIEW:START --> がありません")
    doc = OVERVIEW_RE.sub(lambda m: m.group(1) + "\n" + overview_svg() + "\n" + m.group(2), doc, count=1)
    idx.write_text(doc, encoding="utf-8")

    n = sum(len(c["sections"]) for c in toc["chapters"])
    print("updated: assets/toc.js (%d 章 / %d 節) + index.html の概要図" % (len(toc["chapters"]), n))


if __name__ == "__main__":
    main()
