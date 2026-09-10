#!/usr/bin/env python3
"""claude-code-guide の内部リンク・見出し番号・アンカー・章ファイルの宣言を検証する。

章・節の構成は各 chNN-*.html が唯一のソースなので、突き合わせ先の toc.json は無い。
代わりに、章ファイルの宣言（data-chapter・節 id・h3 番号）が互いに整合しているかと、
生成物 assets/toc.js が章ファイルの現状から作られたものかを検査する。
"""
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guide_toc import GUIDE, chapter_files, load_toc, toc_js  # noqa: E402

pages = sorted(p for p in GUIDE.glob("*.html"))
ids = {p.name: set(re.findall(r'id="([^"]+)"', p.read_text(encoding="utf-8"))) for p in pages}
errors = []


class Balance(HTMLParser):
    VOID = {"br", "hr", "img", "input", "meta", "link", "source", "path", "rect", "line", "circle",
            "use", "col", "polygon", "polyline", "stop", "ellipse"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            errors.append(f"{self.name}: 閉じタグ不一致 </{tag}> (期待 {self.stack[-1:] or '無し'})")


for p in pages:
    t = p.read_text(encoding="utf-8")
    b = Balance(); b.name = p.name; b.feed(t)
    if b.stack:
        errors.append(f"{p.name}: 閉じられていないタグ {b.stack}")
    for href in re.findall(r'href="([^"#][^"]*?)?(#[^"]*)?"', t):
        page, anchor = (href[0] or p.name).split("?")[0], href[1]
        if page.startswith(("http", "mailto")) or not page.endswith(".html"):
            continue
        if page not in ids:
            errors.append(f"{p.name}: リンク先なし {page}"); continue
        if anchor and anchor[1:] not in ids[page]:
            errors.append(f"{p.name}: アンカーなし {page}{anchor}")
    for m in re.finditer(r'data-slide-title="([^"]+)">\s*\n\s*<h3>[\d-]+\.\s*([^<]+)</h3>', t):
        if not m.group(2).strip().startswith(m.group(1)):
            errors.append(f"{p.name}: 節タイトルと h3 の不一致 slide={m.group(1)!r} h3={m.group(2).strip()!r}")
    for m in re.finditer(r'data-slide="([\d.-]+)"[^>]*>\s*\n\s*<h3>([\d-]+)\.', t):
        if m.group(1) != m.group(2):
            errors.append(f"{p.name}: 番号不一致 data-slide={m.group(1)} h3={m.group(2)}")

# 章ファイルの宣言: ファイル名の番号 = data-chapter、節 id は sN-1, sN-2, … と連番
for f in chapter_files():
    t = f.read_text(encoding="utf-8")
    fnum = int(f.name[2:4])
    m = re.search(r'<section class="chapter" id="ch(\d+)" data-chapter="(\d+)">', t)
    if not m:
        errors.append(f'{f.name}: <section class="chapter" id="chN" data-chapter="N"> がない'); continue
    if not (int(m.group(1)) == int(m.group(2)) == fnum):
        errors.append(f"{f.name}: 章番号の不一致 ファイル名={fnum} id=ch{m.group(1)} data-chapter={m.group(2)}")
    sids = re.findall(r'<article class="slide" id="([^"]+)"', t)
    want = [f"s{fnum}-{k}" for k in range(1, len(sids) + 1)]
    if sids != want:
        errors.append(f"{f.name}: 節 id が連番でない\n  期待: {want}\n  実際: {sids}")
    if len(set(re.findall(r'data-chapter="', t))) and t.count("<section class=\"chapter\"") != 1:
        errors.append(f"{f.name}: 章は 1 ファイルに 1 つ")

# 生成物の鮮度: assets/toc.js が今の章ファイルから作られたものか
toc_path = GUIDE / "assets" / "toc.js"
if not toc_path.exists() or toc_path.read_text(encoding="utf-8") != toc_js(load_toc()):
    errors.append("assets/toc.js が古い。python3 claude-code-guide/tools/build_toc.py を実行する")

print("\n".join(errors) if errors else f"OK — {len(pages)} ページ、問題なし")
sys.exit(1 if errors else 0)
