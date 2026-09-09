#!/usr/bin/env python3
"""claude-code-overview.html から SVG と PNG を書き出す。

使い方（リポジトリ直下で）:
    python3 claude-code-overview/export.py              # dist/claude-code-overview.svg と .png を書き出す
    python3 claude-code-overview/export.py --svg-only   # PNG を作らない（Chrome が無い環境・CI 用）

- SVG は HTML の <svg>…</svg> をそのまま切り出す。フォントの @import を含むので単体で表示できる
- PNG はヘッドレス Chrome で HTML を描画したスクリーンショット。大きさは <svg> の viewBox から取り、2 倍解像度で出す
- 依存は Python 標準ライブラリと Google Chrome だけ。Chrome の場所は環境変数 CHROME で上書きできる
"""
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "claude-code-overview.html"
OUT_DIR = HERE / "dist"
OUT_SVG = OUT_DIR / "claude-code-overview.svg"
OUT_PNG = OUT_DIR / "claude-code-overview.png"

SCALE = 2                       # PNG の解像度倍率
FONT_WAIT_MS = 6000             # Web フォントの読み込みを待つ仮想時間

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
)


def find_chrome() -> str | None:
    """環境変数 CHROME → 既知のパス → PATH の順に Chrome を探す。"""
    env = os.environ.get("CHROME")
    if env:
        return env
    for c in CHROME_CANDIDATES:
        if Path(c).is_file():
            return c
        found = shutil.which(c)
        if found:
            return found
    return None


def extract_svg(html: str) -> str:
    m = re.search(r"<svg.*</svg>", html, re.S)
    if not m:
        raise SystemExit(f"エラー: {SRC.name} に <svg> が見つからない")
    return m.group(0) + "\n"


def viewbox_size(svg: str) -> tuple[int, int]:
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    if not m:
        raise SystemExit('エラー: <svg> に viewBox="0 0 W H" が無い')
    return int(m.group(1)), int(m.group(2))


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"エラー: {path} が PNG ではない")
    return struct.unpack(">II", head[16:24])


def write_png(chrome: str, width: int, height: int) -> None:
    args = [
        chrome,
        "--headless=new",
        f"--screenshot={OUT_PNG}",
        f"--window-size={width},{height}",
        f"--force-device-scale-factor={SCALE}",
        "--hide-scrollbars",
        f"--virtual-time-budget={FONT_WAIT_MS}",
    ]
    if platform.system() == "Linux":
        args += ["--no-sandbox", "--disable-gpu"]
    args.append(SRC.as_uri())
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0 or not OUT_PNG.is_file():
        raise SystemExit(f"エラー: Chrome の描画に失敗した\n{result.stderr.strip()}")


def main(argv: list[str]) -> int:
    svg_only = "--svg-only" in argv
    html = SRC.read_text(encoding="utf-8")
    svg = extract_svg(html)
    width, height = viewbox_size(svg)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_SVG.write_text(svg, encoding="utf-8")
    print(f"OK — {OUT_SVG.relative_to(HERE.parent)} ({len(svg.encode('utf-8')) // 1024} KB, {width}×{height})")
    if svg_only:
        return 0

    chrome = find_chrome()
    if chrome is None:
        print("エラー: Google Chrome が見つからない。環境変数 CHROME に実行ファイルのパスを設定するか、"
              "--svg-only で SVG だけ書き出す", file=sys.stderr)
        return 1
    write_png(chrome, width, height)
    w, h = png_size(OUT_PNG)
    print(f"OK — {OUT_PNG.relative_to(HERE.parent)} ({OUT_PNG.stat().st_size // 1024} KB, {w}×{h})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
