#!/usr/bin/env python3
"""claude-code-guide の内部リンク・見出し番号・アンカーを検証する。"""
import re, sys, json
from pathlib import Path
from html.parser import HTMLParser

GUIDE = Path(__file__).resolve().parent.parent
pages = sorted(p for p in GUIDE.glob("*.html"))
ids = {p.name: set(re.findall(r'id="([^"]+)"', p.read_text(encoding="utf-8"))) for p in pages}
errors = []

class Balance(HTMLParser):
    VOID = {"br","hr","img","input","meta","link","source","path","rect","line","circle","use","col","polygon","polyline","stop","ellipse"}
    def __init__(self): super().__init__(convert_charrefs=True); self.stack=[]
    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID: self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if self.stack and self.stack[-1]==tag: self.stack.pop()
        else: errors.append(f"{self.name}: 閉じタグ不一致 </{tag}> (期待 {self.stack[-1:] or '無し'})")

for p in pages:
    t = p.read_text(encoding="utf-8")
    b = Balance(); b.name = p.name; b.feed(t)
    if b.stack: errors.append(f"{p.name}: 閉じられていないタグ {b.stack}")
    for href in re.findall(r'href="([^"#][^"]*?)?(#[^"]*)?"', t):
        page, anchor = (href[0] or p.name).split("?")[0], href[1]
        if page.startswith(("http", "mailto")) or not page.endswith(".html"): continue
        if page not in ids: errors.append(f"{p.name}: リンク先なし {page}"); continue
        if anchor and anchor[1:] not in ids[page]: errors.append(f"{p.name}: アンカーなし {page}{anchor}")
    for m in re.finditer(r'data-slide-title="([^"]+)">\s*\n\s*<h3>[\d-]+\.\s*([^<]+)</h3>', t):
        if not m.group(2).strip().startswith(m.group(1)):
            errors.append(f"{p.name}: 節タイトルと h3 の不一致 slide={m.group(1)!r} h3={m.group(2).strip()!r}")
    # 見出し番号と data-slide の整合
    for m in re.finditer(r'data-slide="([\d.-]+)"[^>]*>\s*\n\s*<h3>([\d-]+)\.', t):
        if m.group(1) != m.group(2): errors.append(f"{p.name}: 番号不一致 data-slide={m.group(1)} h3={m.group(2)}")

# toc.json と実ページの節タイトル一致
toc = json.loads((GUIDE / "toc.json").read_text(encoding="utf-8"))
for ch in toc["chapters"]:
    t = (GUIDE / ch["file"]).read_text(encoding="utf-8")
    titles = re.findall(r'<article class="slide"[^>]*data-slide-title="([^"]+)"', t)
    want = [s["title"] for s in ch["sections"]]
    if titles != want: errors.append(f'{ch["file"]}: toc.json と節タイトル不一致\n  toc : {want}\n  page: {titles}')

print("\n".join(errors) if errors else f"OK — {len(pages)} ページ、問題なし")
sys.exit(1 if errors else 0)
