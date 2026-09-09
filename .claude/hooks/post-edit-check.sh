#!/bin/bash
# PostToolUse(Edit|Write)
# claude-code-guide/ 配下の章 HTML か toc.json を編集した直後に check_docs.py を回す。
# 失敗したら exit 2 で指摘を Claude に返し、その場で直させる（jq 不要・Python 標準ライブラリのみ）。
set -u
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

FILE=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null)

case "$FILE" in
  *claude-code-guide/_source/*|*claude-code-guide/dist/*|*claude-code-guide/_todo/*) exit 0 ;;
  *claude-code-guide/*.html|*claude-code-guide/toc.json) ;;
  *) exit 0 ;;
esac

OUT=$(python3 claude-code-guide/tools/check_docs.py 2>&1) && exit 0
{
  echo "check_docs.py が失敗した。python3 claude-code-guide/tools/build_nav.py → python3 claude-code-guide/tools/check_docs.py が通るまで作業を終えないこと。"
  echo "$OUT"
} >&2
exit 2
