#!/usr/bin/env bash
set -o pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: Python 3.9+ is required but was not found in PATH." >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

if [[ -n "${LOCALES_DIR:-}" ]]; then
  case "$LOCALES_DIR" in
    /*) LOCALE_DIR="$LOCALES_DIR" ;;
    *) LOCALE_DIR="${REPO_DIR}/${LOCALES_DIR}" ;;
  esac
else
  LOCALE_DIR="${REPO_DIR}/locales"
fi

if [[ ! -d "$LOCALE_DIR" || ! -r "$LOCALE_DIR" || ! -x "$LOCALE_DIR" ]]; then
  echo "Error: Locale directory '$LOCALE_DIR' does not exist or cannot be read." >&2
  exit 1
fi

EN_JSON="${LOCALE_DIR}/en.json"
if [[ ! -r "$EN_JSON" ]]; then
  echo "Error: Cannot read en.json at '$EN_JSON'. Check that the file exists and is readable." >&2
  exit 1
fi

KEY_COUNT="$(python3 -c 'import json, sys; print(len(json.load(open(sys.argv[1], encoding="utf-8"))))' "$EN_JSON")"
echo "Keys in en.json: ${KEY_COUNT}"

LOCALE_COUNT="$(find "$LOCALE_DIR" -maxdepth 1 -type f -name '*.json' ! -name 'en.json' | wc -l)"
if (( LOCALE_COUNT == 0 )); then
  echo "Error: No locale JSON files found in '$LOCALE_DIR' (excluding en.json)." >&2
  exit 1
fi

echo "Other locale files found: ${LOCALE_COUNT}"

REPORT_DIR="${SCRIPT_DIR}/../reports"
REPORT_FILE="${REPORT_DIR}/locale-report.txt"
mkdir -p -- "$REPORT_DIR"

export LOCALES_DIR="$LOCALE_DIR"
python3 "${SCRIPT_DIR}/check_locales.py" 2>&1 | tee "$REPORT_FILE"
VALIDATOR_STATUS=${PIPESTATUS[0]}
exit "$VALIDATOR_STATUS"
