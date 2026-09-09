#!/usr/bin/env python3
"""章番号を付け替える。 使い方: renumber_chapter.py <旧番号> <新番号>

ファイル名、<section id>、data-chapter、章見出しの通し番号、
節の id / data-slide / 見出し番号、他ページからの参照リンクをまとめて書き換える。
番号が衝突しないよう、大きい番号から順に実行すること。
"""
import re
import subprocess
import sys
from pathlib import Path

GUIDE = Path(__file__).resolve().parent.parent


def main(old, new):
    src = next(GUIDE.glob(f"ch{old:02d}-*.html"))
    slug = src.name.split("-", 1)[1]
    dst = GUIDE / f"ch{new:02d}-{slug}"

    doc = src.read_text(encoding="utf-8")
    doc = doc.replace(f'id="ch{old}" data-chapter="{old}"', f'id="ch{new}" data-chapter="{new}"')
    doc = doc.replace(f'<span class="chapter-num">{old:02d}</span>', f'<span class="chapter-num">{new:02d}</span>')
    doc = doc.replace(f'第{old}章', f'第{new}章')
    doc = re.sub(rf'id="s{old}-(\d+)" data-slide="{old}-(\d+)"', rf'id="s{new}-\1" data-slide="{new}-\2"', doc)
    doc = re.sub(rf'<h3>{old}-(\d+)\.', rf'<h3>{new}-\1.', doc)
    dst.write_text(doc, encoding="utf-8")
    src.unlink()

    # 他ページからの参照を更新
    for f in GUIDE.glob("*.html"):
        t = f.read_text(encoding="utf-8")
        u = t.replace(src.name, dst.name)
        if u != t:
            f.write_text(u, encoding="utf-8")
    print(f"ch{old:02d} -> ch{new:02d}  ({src.name} -> {dst.name})")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
