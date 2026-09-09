#!/usr/bin/env python3
"""claude-code-guide/_source/index.html を章ごとの HTML に分解する（ワンショット）。

元 HTML の <style> / <script> / 各 <section class="chapter"> の中身は
一切書き換えずにそのまま移送する（見出しレベルの昇格のみ行う）。
目次データは toc.json に書き出し、以降のナビ再生成は tools/build_nav.py が担う。
"""
import html
import json
import re
from pathlib import Path

GUIDE = Path(__file__).resolve().parent.parent
SRC = GUIDE / "_source" / "index.html"

# 章番号 → ファイル名スラッグ
SLUGS = {
    0: "about", 1: "what-is-claude-code", 2: "core-mechanisms",
    3: "basics-and-interface", 4: "memory-and-instructions",
    5: "extension-overview", 6: "skills", 7: "subagents", 8: "hooks",
    9: "mcp", 10: "plugins", 11: "settings-and-security",
    12: "automation-and-sdk", 13: "cost-and-monitoring",
    14: "best-practices", 15: "learning-roadmap", 16: "sources",
    17: "glossary",
}


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def parse():
    doc = SRC.read_text(encoding="utf-8")

    style = re.search(r"<style>\n(.*?)\n</style>", doc, re.S).group(1)
    script = re.search(r"<script>\n(.*?)\n</script>", doc, re.S).group(1)
    footer = re.search(r"<footer>.*?</footer>", doc, re.S).group(0)
    masthead = re.search(r'<header class="masthead">.*?</header>', doc, re.S).group(0)

    chapters = []
    pattern = r'<section class="chapter" id="ch(\d+)" data-chapter="\d+">\n(.*?)\n</section>'
    for num, body in re.findall(pattern, doc, re.S):
        num = int(num)
        title = strip_tags(re.search(r"<h2>(.*?)</h2>", body, re.S).group(1))
        lede_m = re.search(r'<p class="chapter-lede">(.*?)</p>', body, re.S)
        lede = strip_tags(lede_m.group(1)) if lede_m else ""
        sections = [
            {"id": sid, "title": html.unescape(stitle)}
            for sid, stitle in re.findall(
                r'<article class="slide" id="([^"]+)"[^>]*data-slide-title="([^"]*)"', body
            )
        ]
        chapters.append({
            "num": num,
            "slug": SLUGS[num],
            "file": f"ch{num:02d}-{SLUGS[num]}.html",
            "title": title,
            "lede": lede,
            "body": body,
            "sections": sections,
        })
    chapters.sort(key=lambda c: c["num"])
    return style, script, footer, masthead, chapters


def main():
    style, script, footer, masthead, chapters = parse()

    (GUIDE / "assets" / "style.css").write_text(style + "\n", encoding="utf-8")
    (GUIDE / "assets" / "app.js").write_text(script + "\n", encoding="utf-8")

    toc = {
        "title": "Claude Code 体系的入門",
        "chapters": [
            {k: c[k] for k in ("num", "slug", "file", "title", "lede", "sections")}
            for c in chapters
        ],
    }
    (GUIDE / "toc.json").write_text(
        json.dumps(toc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # 本文だけを一時保存。ページ組み立ては build_nav.py が行う。
    parts = GUIDE / "_parts"
    parts.mkdir(exist_ok=True)
    for c in chapters:
        # 章見出しは h2 → h1 に昇格（1ページ1章になるため）
        body = c["body"].replace("<h2>" + "", "<h1>", 1).replace("</h2>", "</h1>", 1)
        (parts / (c["file"] + ".part")).write_text(body, encoding="utf-8")
    (parts / "footer.part").write_text(footer, encoding="utf-8")
    (parts / "masthead.part").write_text(masthead, encoding="utf-8")

    print(f"chapters={len(chapters)} sections={sum(len(c['sections']) for c in chapters)}")
    for c in chapters:
        print(f"  ch{c['num']:02d} {c['file']:<34} sections={len(c['sections'])}  {c['title']}")


if __name__ == "__main__":
    main()
