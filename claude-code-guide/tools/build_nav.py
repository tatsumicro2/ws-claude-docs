#!/usr/bin/env python3
"""toc.json を唯一のソースとして、全ページのナビゲーションを再生成する。

差し替えるのはマーカーで囲まれた区間だけなので、章の本文を直接編集しても壊れない。

  <!-- NAV:START -->   〜 <!-- NAV:END -->    左サイドバー（全ページ）
  <!-- PAGER:START --> 〜 <!-- PAGER:END -->  前後の章リンク（章ページ）
  <!-- INDEX:START --> 〜 <!-- INDEX:END -->  章カード一覧（トップページ）

使い方:
  1. 章や節を追加・変更したら toc.json を編集する
  2. python3 claude-code-guide/tools/build_nav.py を実行する

新しい章ページを足すときは、既存の章 HTML をコピーして本文を差し替え、
toc.json に章エントリを追記してから本スクリプトを実行する。
"""
import hashlib
import html
import json
import re
from pathlib import Path

GUIDE = Path(__file__).resolve().parent.parent

CARET = ('<svg viewBox="0 0 16 16" width="9" height="9" aria-hidden="true">'
         '<path d="M5.5 3l5 5-5 5" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')

NAV_RE = re.compile(r"(<!-- NAV:START -->).*?(<!-- NAV:END -->)", re.S)
PAGER_RE = re.compile(r"(<!-- PAGER:START -->).*?(<!-- PAGER:END -->)", re.S)
INDEX_RE = re.compile(r"(<!-- INDEX:START -->).*?(<!-- INDEX:END -->)", re.S)
ASSET_RE = re.compile(r'(href|src)="(assets/[a-z]+\.(?:css|js))(?:\?v=[0-9a-f]+)?"')


def asset_versions():
    """アセットの内容ハッシュを返す。ブラウザが古い CSS / JS を使い続けるのを防ぐ。"""
    out = {}
    for f in sorted((GUIDE / "assets").glob("*.*")):
        digest = hashlib.sha256(f.read_bytes()).hexdigest()[:8]
        out["assets/" + f.name] = digest
    return out


def stamp_assets(doc, versions):
    return ASSET_RE.sub(
        lambda m: '%s="%s?v=%s"' % (m.group(1), m.group(2), versions.get(m.group(2), "0")), doc
    )


def esc(s):
    return html.escape(s, quote=True)


def sidebar(toc, current):
    """current: 章番号。トップページでは None を渡す。"""
    out = ['<nav class="sidebar" aria-label="目次">',
           '  <a class="sidebar-brand" href="index.html">Claude Code<em>体系的入門</em></a>',
           '  <p class="sidebar-label">Contents</p>',
           '  <ol class="toc-tree">']
    for ch in toc["chapters"]:
        n, f = ch["num"], ch["file"]
        cur = n == current
        listid = "toc-sec-%d" % n
        out.append("    <li>")
        out.append('      <div class="toc-ch-row%s">' % (" is-current" if cur else ""))
        out.append('        <a class="toc-ch-link" href="%s"%s>'
                   '<span class="toc-num">%02d</span><span>%s</span></a>'
                   % (f, ' aria-current="page"' if cur else "", n, esc(ch["title"])))
        if ch["sections"]:
            out.append('        <button class="toc-toggle" type="button" aria-expanded="%s" '
                       'aria-controls="%s" aria-label="%sの節を開閉">%s</button>'
                       % ("true" if cur else "false", listid, esc(ch["title"]), CARET))
        out.append("      </div>")
        if ch["sections"]:
            out.append('      <ul class="toc-sections" id="%s"%s>'
                       % (listid, "" if cur else " hidden"))
            for s in ch["sections"]:
                out.append('        <li><a href="%s#%s">%s</a></li>'
                           % (f, s["id"], esc(s["title"])))
            out.append("      </ul>")
        out.append("    </li>")
    out += ["  </ol>", "</nav>"]
    return "\n".join(out)


def pager(toc, current):
    chs = toc["chapters"]
    i = next(k for k, c in enumerate(chs) if c["num"] == current)
    out = ['<nav class="pager" aria-label="章の移動">']
    if i > 0:
        p = chs[i - 1]
        out.append('  <a class="prev" href="%s" rel="prev">'
                   '<span class="dir">← 第%d章</span><span class="name">%s</span></a>'
                   % (p["file"], p["num"], esc(p["title"])))
    if i < len(chs) - 1:
        nx = chs[i + 1]
        out.append('  <a class="next" href="%s" rel="next">'
                   '<span class="dir">第%d章 →</span><span class="name">%s</span></a>'
                   % (nx["file"], nx["num"], esc(nx["title"])))
    out.append("</nav>")
    return "\n".join(out)


def index_cards(toc):
    out = ['<ol class="index-grid">']
    for ch in toc["chapters"]:
        out.append('  <li><a class="index-card" href="%s">'
                   '<span class="n">CHAPTER %02d</span><h2>%s</h2><p>%s</p>'
                   '<span class="count">%d sections</span></a></li>'
                   % (ch["file"], ch["num"], esc(ch["title"]),
                      esc(ch["lede"][:110]), len(ch["sections"])))
    out.append("</ol>")
    return "\n".join(out)


def replace(doc, regex, block, where):
    if not regex.search(doc):
        raise SystemExit("マーカーが見つかりません: %s (%s)" % (regex.pattern, where))
    return regex.sub(lambda m: m.group(1) + "\n" + block + "\n" + m.group(2), doc, count=1)


def main():
    toc = json.loads((GUIDE / "toc.json").read_text(encoding="utf-8"))
    versions = asset_versions()

    for ch in toc["chapters"]:
        path = GUIDE / ch["file"]
        if not path.exists():
            raise SystemExit("ページがありません: %s（既存章をコピーして作成してください）" % path)
        doc = path.read_text(encoding="utf-8")
        doc = replace(doc, NAV_RE, sidebar(toc, ch["num"]), ch["file"])
        doc = replace(doc, PAGER_RE, pager(toc, ch["num"]), ch["file"])
        doc = stamp_assets(doc, versions)
        path.write_text(doc, encoding="utf-8")

    idx = GUIDE / "index.html"
    doc = idx.read_text(encoding="utf-8")
    doc = replace(doc, NAV_RE, sidebar(toc, None), "index.html")
    doc = replace(doc, INDEX_RE, index_cards(toc), "index.html")
    doc = stamp_assets(doc, versions)
    idx.write_text(doc, encoding="utf-8")

    print("updated: index.html + %d chapter pages" % len(toc["chapters"]))


if __name__ == "__main__":
    main()
