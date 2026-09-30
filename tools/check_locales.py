#!/usr/bin/env python3
"""Check locale JSON files against locales/en.json."""

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")
RESET = "\033[0m"
BOLD_RED = "\033[1;31m"
COLORS = {
    "filename": "\033[96m",
    "Missing keys": "\033[33m",
    "Extra keys": "\033[35m",
    "Placeholder mismatches": "\033[31m",
    "Empty values": "\033[34m",
    "File errors": "\033[31m",
    "OK": "\033[32m",
    "total": BOLD_RED,
}


def paint(text, color, enabled):
    """Wrap text in ANSI color when output is an interactive terminal."""
    if not enabled:
        return text
    return f"{COLORS[color]}{text}{RESET}"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--locales-dir",
        type=Path,
        default=Path("locales"),
        help="directory containing en.json and translated locale JSON files",
    )
    return parser.parse_args()


def load_locale(path):
    """Load a locale JSON file, returning (data, error)."""
    try:
        with path.open(encoding="utf-8") as locale_file:
            data = json.load(locale_file)
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)

    if not isinstance(data, dict):
        return None, "top-level JSON value must be an object"
    return data, None


def extract_placeholders(value):
    """Return placeholder occurrence counts, such as {"count": 2}."""
    if not isinstance(value, str):
        return Counter()
    return Counter(PLACEHOLDER_RE.findall(value))


def validate_locale(reference, translation):
    """Return categorized issues for one translation mapping."""
    issues = {
        "Missing keys": [],
        "Extra keys": [],
        "Placeholder mismatches": [],
        "Empty values": [],
    }
    reference_keys = set(reference)
    translation_keys = set(translation)

    issues["Missing keys"] = sorted(reference_keys - translation_keys)
    issues["Extra keys"] = sorted(translation_keys - reference_keys)

    for key in sorted(reference_keys & translation_keys):
        source_value = reference[key]
        translated_value = translation[key]

        if translated_value == "":
            issues["Empty values"].append(key)

        source_placeholders = extract_placeholders(source_value)
        translated_placeholders = extract_placeholders(translated_value)
        if source_placeholders != translated_placeholders:
            issues["Placeholder mismatches"].append(
                f"{key} (English: {dict(sorted(source_placeholders.items()))}, "
                f"translation: {dict(sorted(translated_placeholders.items()))})"
            )

    return issues


def format_locale_report(locale_name, issues, color_enabled=False):
    """Format one locale's categorized validation results."""
    issue_count = sum(len(items) for items in issues.values())
    if not issue_count:
        return (
            f"{paint(locale_name, 'filename', color_enabled)}: "
            f"{paint('OK', 'OK', color_enabled)}"
        )

    lines = [f"{paint(locale_name, 'filename', color_enabled)}: {issue_count} issue(s)"]
    for category, items in issues.items():
        if items:
            lines.append(f"  {paint(category + ':', category, color_enabled)}")
            lines.extend(f"    - {item}" for item in items)
    return "\n".join(lines)


def main():
    args = parse_args()
    locales_dir = args.locales_dir
    reference_path = locales_dir / "en.json"

    reference, error = load_locale(reference_path)
    if error:
        print(f"Error loading {reference_path}: {error}", file=sys.stderr)
        return 1

    locale_paths = sorted(
        path for path in locales_dir.glob("*.json")
        if path.name != reference_path.name
    )

    color_enabled = sys.stdout.isatty() and "NO_COLOR" not in os.environ

    total_issues = 0
    locale_reports = []
    for locale_path in locale_paths:
        translation, error = load_locale(locale_path)
        if error:
            issues = {"File errors": [f"Could not load JSON: {error}"]}
        else:
            issues = validate_locale(reference, translation)

        total_issues += sum(len(items) for items in issues.values())
        locale_reports.append(format_locale_report(locale_path.name, issues, color_enabled))

    total_line = paint(f"Total: {total_issues} issue(s)", "total", color_enabled)
    print(total_line)
    for report in locale_reports:
        print(report)
    return 1 if total_issues else 0


if __name__ == "__main__":
    sys.exit(main())
