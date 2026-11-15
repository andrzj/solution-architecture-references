#!/usr/bin/env bash
# Sample external links from further-reading sections (HTTP status only).
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
urls=$(grep -rhoP 'href="\Khttps?://[^"]+' --include='*.html' . | sort -u)
fail=0
checked=0
while IFS= read -r url; do
  [[ -z "$url" ]] && continue
  code=$(curl -sL -o /dev/null -w "%{http_code}" --max-time 15 "$url" || echo "000")
  checked=$((checked + 1))
  if [[ "$code" =~ ^[23] ]]; then
  : # ok
  else
    echo "FAIL $code $url"
    fail=$((fail + 1))
  fi
done <<< "$urls"
echo "Checked $checked URLs; failures: $fail"
exit "$fail"