#!/bin/bash
# Stop
# claude-code-guide/ に未コミットの変更があるとき、check_docs.py が通るまで作業を終えさせない。
# 資料に触れていないセッションでは何もしない。
set -u
INPUT=$(cat)

# このフックが原因で再開した周回では素通しする（無限ループ防止）
if printf '%s' "$INPUT" | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("stop_hook_active") else 1)' 2>/dev/null; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

if git diff --quiet HEAD -- claude-code-guide 2>/dev/null \
   && [ -z "$(git ls-files --others --exclude-standard claude-code-guide)" ]; then
  exit 0
fi

OUT=$(python3 claude-code-guide/tools/check_docs.py 2>&1) && exit 0
{
  echo "資料に未コミットの変更があり、check_docs.py が失敗している。"
  echo "python3 claude-code-guide/tools/build_toc.py → python3 claude-code-guide/tools/check_docs.py を通してから終えること。"
  echo "$OUT"
} >&2
exit 2
