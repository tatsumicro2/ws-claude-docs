"""章ファイル群から目次データを組み立てる共通モジュール。

章・節の構成は各 chNN-*.html が唯一のソース。
  - 章番号   : <section class="chapter" data-chapter="N">
  - 章タイトル: <div class="chapter-head"> の <h1>
  - 章の導入  : <p class="chapter-lede">（章カードの説明文に使う）
  - 節        : <article class="slide" id="sN-M" data-slide-title="…">
資料名とフッター文言は site.json に持つ。
"""
import html
import json
import re
from pathlib import Path

GUIDE = Path(__file__).resolve().parent.parent
SITE = GUIDE / "site.json"

CHAPTER_RE = re.compile(r'<section class="chapter"[^>]*data-chapter="(\d+)"')
TITLE_RE = re.compile(r'<div class="chapter-head">.*?<h1>(.*?)</h1>', re.S)
LEDE_RE = re.compile(r'<p class="chapter-lede">(.*?)</p>', re.S)
SECTION_RE = re.compile(r'<article class="slide" id="([^"]+)"[^>]*data-slide-title="([^"]+)"')
TAG_RE = re.compile(r"<[^>]+>")


def chapter_files():
    return sorted(GUIDE.glob("ch[0-9][0-9]-*.html"))


def plain(s):
    return html.unescape(re.sub(r"\s+", " ", TAG_RE.sub("", s))).strip()


def load_toc():
    site = json.loads(SITE.read_text(encoding="utf-8"))
    chapters = []
    for f in chapter_files():
        doc = f.read_text(encoding="utf-8")
        m = CHAPTER_RE.search(doc)
        if not m:
            raise SystemExit("章の宣言がありません: %s（<section class=\"chapter\" data-chapter=\"N\"> が必要）" % f.name)
        t = TITLE_RE.search(doc)
        if not t:
            raise SystemExit("章タイトルがありません: %s（<div class=\"chapter-head\"> 内の <h1>）" % f.name)
        lede = LEDE_RE.search(doc)
        chapters.append({
            "num": int(m.group(1)),
            "file": f.name,
            "title": plain(t.group(1)),
            "lede": plain(lede.group(1)) if lede else "",
            "sections": [{"id": sid, "title": html.unescape(title)}
                         for sid, title in SECTION_RE.findall(doc)],
        })
    return {"title": site["title"], "footer": site["footer"], "chapters": chapters}


def toc_js(toc):
    """assets/toc.js の中身。ブラウザが file:// で JSON を fetch できないため JS にする。"""
    return ("/* 生成物。編集しない。章ファイルから tools/build_toc.py が作る */\n"
            "window.CCGUIDE = %s;\n"
            % json.dumps(toc, ensure_ascii=False, indent=2))


def esc(s):
    return html.escape(s, quote=True)


CARET = ('<svg viewBox="0 0 16 16" width="9" height="9" aria-hidden="true">'
         '<path d="M5.5 3l5 5-5 5" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def sidebar_html(toc, current=None, expand_all=False, href=None):
    """単一ファイル版が使う Python 側の描画。通常ページは nav.js が同じものを描く。"""
    href = href or (lambda f, anchor: f + ("#" + anchor if anchor else ""))
    out = ['<nav class="sidebar" aria-label="目次">',
           '  <a class="sidebar-brand" href="%s">Claude Code<em>体系的入門</em></a>' % href("index.html", None),
           '  <p class="sidebar-label">Contents</p>',
           '  <ol class="toc-tree">']
    for ch in toc["chapters"]:
        n, f = ch["num"], ch["file"]
        cur = n == current
        open_ = cur or expand_all
        listid = "toc-sec-%d" % n
        out.append("    <li>")
        out.append('      <div class="toc-ch-row%s">' % (" is-current" if cur else ""))
        out.append('        <a class="toc-ch-link" href="%s"%s>'
                   '<span class="toc-num">%02d</span><span>%s</span></a>'
                   % (href(f, None), ' aria-current="page"' if cur else "", n, esc(ch["title"])))
        if ch["sections"]:
            out.append('        <button class="toc-toggle" type="button" aria-expanded="%s" '
                       'aria-controls="%s" aria-label="%sの節を開閉">%s</button>'
                       % ("true" if open_ else "false", listid, esc(ch["title"]), CARET))
        out.append("      </div>")
        if ch["sections"]:
            out.append('      <ul class="toc-sections" id="%s"%s>' % (listid, "" if open_ else " hidden"))
            for s in ch["sections"]:
                out.append('        <li><a href="%s">%s</a></li>' % (href(f, s["id"]), esc(s["title"])))
            out.append("      </ul>")
        out.append("    </li>")
    out += ["  </ol>", "</nav>"]
    return "\n".join(out)


def index_cards_html(toc, href=None):
    href = href or (lambda f: f)
    out = ['<ol class="index-grid" data-index>']
    for ch in toc["chapters"]:
        out.append('  <li><a class="index-card" href="%s">'
                   '<span class="n">CHAPTER %02d</span><h2>%s</h2><p>%s</p>'
                   '<span class="count">%d sections</span></a></li>'
                   % (href(ch["file"]), ch["num"], esc(ch["title"]),
                      esc(ch["lede"][:110]), len(ch["sections"])))
    out.append("</ol>")
    return "\n".join(out)


def footer_html(toc):
    return '<footer>\n  <p><strong>%s</strong> — %s</p>\n</footer>' % (esc(toc["title"]), esc(toc["footer"]))
