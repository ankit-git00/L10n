#!/usr/bin/env bash
set -o pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: Python 3.9+ is required but was not found in PATH." >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
EN_JSON="${SCRIPT_DIR}/../locales/en.json"
if [[ ! -r "$EN_JSON" ]]; then
  echo "Error: Cannot read en.json at '$EN_JSON'. Check that the file exists and is readable." >&2
  exit 1
fi

KEY_COUNT="$(python3 -c 'import json, sys; print(len(json.load(open(sys.argv[1], encoding="utf-8"))))' "$EN_JSON")"
echo "Keys in en.json: ${KEY_COUNT}"

LOCALE_DIR="$(dirname -- "$EN_JSON")"
LOCALE_COUNT="$(find "$LOCALE_DIR" -maxdepth 1 -type f -name '*.json' ! -name 'en.json' | wc -l)"
if (( LOCALE_COUNT == 0 )); then
  echo "Error: No locale JSON files found in '$LOCALE_DIR' (excluding en.json)." >&2
  exit 1
fi

echo "Other locale files found: ${LOCALE_COUNT}"

REPORT_DIR="${SCRIPT_DIR}/../reports"
REPORT_FILE="${REPORT_DIR}/locale-report.txt"
mkdir -p -- "$REPORT_DIR"

python3 "${SCRIPT_DIR}/check_locales.py" 2>&1 | tee "$REPORT_FILE"
VALIDATOR_STATUS=${PIPESTATUS[0]}
exit "$VALIDATOR_STATUS"
