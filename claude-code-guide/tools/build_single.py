#!/usr/bin/env python3
"""claude-code-guide/ の全章を 1 枚の自己完結 HTML にまとめる。

- CSS / JS はインラインに埋め込む（外部ファイル参照なし。図は元から SVG インライン）
- 章間リンク chNN-*.html#sX-Y は #sX-Y に、章リンクは #chN に書き換える
- サイドバーは全章を展開した状態で残し、スクロールに応じて節と章をハイライトする
- ページャ・パンくずは除去し、フッタは末尾に 1 つだけ置く

出力先: claude-code-guide/dist/claude-code-guide.html（引数で変更可）

使い方:
    python3 claude-code-guide/tools/build_single.py
    python3 claude-code-guide/tools/build_single.py 別の出力先.html
"""
import json
import re
import sys
from pathlib import Path

GUIDE = Path(__file__).resolve().parent.parent
DEFAULT_OUT = GUIDE / "dist" / "claude-code-guide.html"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def between(text: str, start: str, end: str) -> str:
    i = text.index(start) + len(start)
    j = text.index(end, i)
    return text[i:j]


def strip_block(text: str, start: str, end: str) -> str:
    return re.sub(re.escape(start) + r".*?" + re.escape(end), "", text, flags=re.S)


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    toc = json.loads(read(GUIDE / "toc.json"))
    chapters = toc["chapters"]
    file_to_anchor = {c["file"]: f"#ch{c['num']}" for c in chapters}

    def rewrite_links(html: str) -> str:
        def repl(m: re.Match) -> str:
            fname, frag = m.group(1), m.group(2)
            if frag:
                return f'href="{frag}"'
            return f'href="{file_to_anchor.get(fname, "#top")}"'

        html = re.sub(r'href="(ch\d{2}-[a-z0-9-]+\.html)(#[^"]*)?"', repl, html)
        html = re.sub(r'href="index\.html(#[^"]*)?"', 'href="#top"', html)
        return html

    # ---- サイドバー（index.html のものを流用。全章を展開状態にする） ----
    index_html = read(GUIDE / "index.html")
    nav = between(index_html, "<!-- NAV:START -->", "<!-- NAV:END -->")
    nav = rewrite_links(nav)
    nav = nav.replace(' class="toc-ch-row is-current"', ' class="toc-ch-row"')
    nav = nav.replace(' aria-current="page"', "")
    nav = nav.replace('aria-expanded="false"', 'aria-expanded="true"')
    nav = re.sub(r'(<ul class="toc-sections" id="toc-sec-\d+") hidden>', r"\1>", nav)

    # ---- 表紙（index.html の main。章カードは #chN へ） ----
    cover = between(index_html, "<main>", "</main>")
    cover = strip_block(cover, "<footer>", "</footer>")
    cover = rewrite_links(cover)
    cover = cover.replace('<header class="masthead">', '<header class="masthead" id="top">', 1)
    # 表紙の図は 1 章の図 1-1 と同じ SVG なので、marker の id が衝突しないよう付け替える
    cover = cover.replace('ar-core', 'ar-core-cover')

    # ---- 各章の本文 ----
    bodies = []
    footer = ""
    for c in chapters:
        html = read(GUIDE / c["file"])
        body = between(html, "<main>", "</main>")
        body = re.sub(r'<nav class="crumb">.*?</nav>\s*', "", body, flags=re.S)
        body = strip_block(body, "<!-- PAGER:START -->", "<!-- PAGER:END -->")
        m = re.search(r"<footer>.*?</footer>", body, flags=re.S)
        if m:
            footer = m.group(0)
            body = body.replace(m.group(0), "")
        bodies.append(rewrite_links(body.strip()))

    # ---- アセットをインライン化 ----
    assets = GUIDE / "assets"
    css = read(assets / "style.css") + "\n" + read(assets / "nav.css")
    js = read(assets / "app.js") + "\n" + read(assets / "nav.js")

    extra_css = """
/* ---------- 単一ファイル版の追加スタイル ---------- */
html{scroll-behavior:auto}  /* 章をまたぐ長距離ジャンプが多いので即時スクロールにする */
.chapter{scroll-margin-top:1rem}
.single-toc-note{font-size:.78rem; color:var(--muted); margin:-.4rem 0 .8rem}
.chapter + .chapter, .index-grid + .chapter{margin-top:5rem; padding-top:3rem; border-top:1px solid var(--line)}
@media print{ .chapter{break-before:page} }
"""

    extra_js = """
// 単一ファイル版: ハイライト中の節が属する章の行も強調し、その行が見えるようサイドバーを追従させる
(function(){
  var sidebar = document.querySelector('.sidebar');
  if (!sidebar) return;
  var rows = Array.prototype.slice.call(sidebar.querySelectorAll('.toc-ch-row'));
  function sync(){
    var active = sidebar.querySelector('.toc-sections a.is-active');
    var list = active ? active.closest('.toc-sections') : null;
    var row = list ? list.parentElement.querySelector(':scope > .toc-ch-row') : null;
    rows.forEach(function(r){ r.classList.toggle('is-current', r === row); });
    if (!active) return;
    var a = active.getBoundingClientRect();
    var s = sidebar.getBoundingClientRect();
    var margin = 48;
    if (a.top < s.top + margin) sidebar.scrollTop -= (s.top + margin - a.top);
    else if (a.bottom > s.bottom - margin) sidebar.scrollTop += (a.bottom - (s.bottom - margin));
  }
  var obs = new MutationObserver(sync);
  sidebar.querySelectorAll('.toc-sections a').forEach(function(a){
    obs.observe(a, { attributes: true, attributeFilter: ['class'] });
  });
  sync();
})();
"""

    title = toc.get("title", "Claude Code 体系的入門")
    total_sections = sum(len(c["sections"]) for c in chapters)
    desc = f"{title}。全 {len(chapters)} 章 / {total_sections} 節を 1 ファイルにまとめた版。"

    doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}（全章・単一ファイル版）</title>
<meta name="description" content="{desc}">
<style>
{css}
{extra_css}
</style>
</head>
<body>
<div class="wrap">

<!-- NAV:START -->{nav}<!-- NAV:END -->

<main>
{cover.strip()}

{chr(10).join(bodies)}

{footer}
</main>
</div>

<script>
{js}
{extra_js}
</script>
</body>
</html>
"""

    # ---- 検証: ページ内リンクの参照先がすべて存在するか ----
    ids = set(re.findall(r'\bid="([^"]+)"', doc))
    missing = sorted({
        frag for frag in re.findall(r'href="#([^"]+)"', doc) if frag not in ids
    })
    if missing:
        print("アンカー切れ:", ", ".join(missing), file=sys.stderr)
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"OK — {out.relative_to(GUIDE.parent)} ({len(doc.encode('utf-8')) // 1024} KB, "
          f"{len(chapters)} 章 / {total_sections} 節)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
