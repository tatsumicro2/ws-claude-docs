#!/usr/bin/env python3
"""claude-code-guide/ の全章を 1 枚の自己完結 HTML にまとめる。

- CSS / JS はインラインに埋め込む（外部ファイル参照なし。図は元から SVG インライン）
- 章間リンク chNN-*.html#sX-Y は #sX-Y に、章リンクは #chN に書き換える
- サイドバー・章カード・フッターは Python 側で描く（章ページでは nav.js が描くもの）。
  サイドバーは全章を展開した状態で、スクロールに応じて節と章をハイライトする
- ページャ・パンくずは置かない

出力先: claude-code-guide/dist/claude-code-guide.html（引数で変更可）

使い方:
    python3 claude-code-guide/tools/build_single.py
    python3 claude-code-guide/tools/build_single.py 別の出力先.html
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guide_toc import GUIDE, load_toc, sidebar_html, index_cards_html, footer_html  # noqa: E402

DEFAULT_OUT = GUIDE / "dist" / "claude-code-guide.html"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def between(text: str, start: str, end: str) -> str:
    i = text.index(start) + len(start)
    j = text.index(end, i)
    return text[i:j]


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    toc = load_toc()
    chapters = toc["chapters"]
    file_to_anchor = {c["file"]: f"#ch{c['num']}" for c in chapters}

    def rewrite_links(html: str) -> str:
        def repl(m: re.Match) -> str:
            fname, frag = m.group(1), m.group(2)
            return f'href="{frag}"' if frag else f'href="{file_to_anchor.get(fname, "#top")}"'
        html = re.sub(r'href="(ch\d{2}-[a-z0-9-]+\.html)(#[^"]*)?"', repl, html)
        html = re.sub(r'href="index\.html(#[^"]*)?"', 'href="#top"', html)
        return html

    def href(f, anchor):
        if f == "index.html":
            return "#top"
        return "#" + anchor if anchor else file_to_anchor[f]

    nav = sidebar_html(toc, current=None, expand_all=True, href=href)
    cards = index_cards_html(toc, href=lambda f: file_to_anchor[f])

    # ---- 表紙（index.html の main。章カードの空の受け皿を Python の描画で置き換える） ----
    cover = between(read(GUIDE / "index.html"), "<main>", "</main>")
    cover = re.sub(r'<ol class="index-grid" data-index>\s*</ol>', cards, cover, count=1)
    cover = rewrite_links(cover)
    cover = cover.replace('<header class="masthead">', '<header class="masthead" id="top">', 1)

    # ---- 各章の本文 ----
    bodies = []
    for c in chapters:
        body = between(read(GUIDE / c["file"]), "<main>", "</main>")
        body = re.sub(r'<nav class="crumb">.*?</nav>\s*', "", body, flags=re.S)
        bodies.append(rewrite_links(body.strip()))

    # ---- アセットをインライン化 ----
    assets = GUIDE / "assets"
    css = read(assets / "style.css") + "\n" + read(assets / "nav.css")
    js = read(assets / "toc.js") + "\n" + read(assets / "app.js") + "\n" + read(assets / "nav.js")

    extra_css = """
/* ---------- 単一ファイル版の追加スタイル ---------- */
html{scroll-behavior:auto}  /* 章をまたぐ長距離ジャンプが多いので即時スクロールにする */
.chapter{scroll-margin-top:1rem}
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

    title = toc["title"]
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

{nav}

<main>
{cover.strip()}

{chr(10).join(bodies)}

{footer_html(toc)}
</main>
</div>

<script>
{js}
{extra_js}
</script>
</body>
</html>
"""

    ids = set(re.findall(r'\bid="([^"]+)"', doc))
    missing = sorted({frag for frag in re.findall(r'href="#([^"]+)"', doc) if frag not in ids})
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
