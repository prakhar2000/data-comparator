#!/usr/bin/env python3
"""Compare two CSV files and report rows added, removed, and changed.

The publish pipeline mounts inputs at /inputs/<name> and reads the report
from stdout. Flags and env vars override those paths for a local run.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two CSV files.")
    parser.add_argument(
        "--older",
        default=os.environ.get("FILE_A") or os.environ.get("INPUT_FILE_A") or "/inputs/file_a",
        help="Older CSV. Env: FILE_A or INPUT_FILE_A. Default: /inputs/file_a",
    )
    parser.add_argument(
        "--newer",
        default=os.environ.get("FILE_B") or os.environ.get("INPUT_FILE_B") or "/inputs/file_b",
        help="Newer CSV. Env: FILE_B or INPUT_FILE_B. Default: /inputs/file_b",
    )
    parser.add_argument(
        "--out",
        default=os.environ.get("OUTPUT_REPORT") or "/outputs/report.json",
        help="Where to write the JSON report. Also printed to stdout.",
    )
    parser.add_argument(
        "--key",
        default=os.environ.get("KEY_COLUMN", ""),
        help="Column that identifies a row. Defaults to the first column.",
    )
    return parser.parse_args()


def load_csv(path: Path, key: str) -> tuple[str, list[str], dict[str, dict[str, str]]]:
    if not path.is_file():
        raise SystemExit(f"Missing file: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise SystemExit(f"{path} has no header row")
        fields = list(reader.fieldnames)
        key_name = key or fields[0]
        if key_name not in fields:
            raise SystemExit(f"{path} has no column named {key_name}")
        rows: dict[str, dict[str, str]] = {}
        for line_number, row in enumerate(reader, start=2):
            row_key = (row.get(key_name) or "").strip()
            if not row_key:
                raise SystemExit(f"{path}:{line_number} has an empty {key_name}")
            if row_key in rows:
                raise SystemExit(f"{path}:{line_number} repeats {key_name} {row_key}")
            rows[row_key] = {name: (row.get(name) or "").strip() for name in fields}
    return key_name, fields, rows


def changed_fields(older: dict[str, str], newer: dict[str, str]) -> list[str]:
    names = list(dict.fromkeys([*older.keys(), *newer.keys()]))
    return [name for name in names if older.get(name, "") != newer.get(name, "")]


def compare(
    older_rows: dict[str, dict[str, str]],
    newer_rows: dict[str, dict[str, str]],
) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for key in [*older_rows.keys(), *[key for key in newer_rows if key not in older_rows]]:
        older = older_rows.get(key)
        newer = newer_rows.get(key)
        if older is None:
            rows.append({"key": key, "status": "added", "older": None, "newer": newer, "fields": []})
        elif newer is None:
            rows.append({"key": key, "status": "removed", "older": older, "newer": None, "fields": []})
        else:
            fields = changed_fields(older, newer)
            if fields:
                rows.append(
                    {"key": key, "status": "changed", "older": older, "newer": newer, "fields": fields}
                )
    summary = {
        "added": sum(1 for row in rows if row["status"] == "added"),
        "removed": sum(1 for row in rows if row["status"] == "removed"),
        "changed": sum(1 for row in rows if row["status"] == "changed"),
    }
    return {"summary": summary, "rows": rows}


def main() -> None:
    args = parse_args()
    key_name, _, older_rows = load_csv(Path(args.older), args.key)
    _, _, newer_rows = load_csv(Path(args.newer), key_name)
    report = compare(older_rows, newer_rows)
    report["key"] = key_name
    payload = json.dumps(report, indent=2)

    out = Path(args.out)
    if str(out) not in ("", "-"):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")

    sys.stdout.write(payload + "\n")
    summary = report["summary"]
    print(
        f"{summary['added']} added, {summary['removed']} removed, {summary['changed']} changed",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
