#!/usr/bin/env python3
"""Convert filename: GitHub URL mappings into Markdown links."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MAPPING_LINE = re.compile(
    r"^(?P<prefix>\s*(?:\d+[、.]\s*)?)"
    r"(?P<name>[^：:\n]+?)"
    r"\s*[：:]\s*"
    r"(?P<url>https://github\.com/\S+)"
    r"\s*$"
)

MARKDOWN_LINK = re.compile(r"\[(?P<name>[^\]]+)\]\((?P<url>https://github\.com/[^)]+)\)")


def convert_line(line: str) -> str:
    match = MAPPING_LINE.match(line)
    if not match:
        return line

    prefix = match.group("prefix")
    name = match.group("name").strip()
    url = match.group("url").strip()
    return f"{prefix}[{name}]({url})"


def convert_text(text: str) -> str:
    return "\n".join(convert_line(line) for line in text.splitlines())


def load_mapping(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        raw_match = MAPPING_LINE.match(line)
        if raw_match:
            mapping[raw_match.group("name").strip()] = raw_match.group("url").strip()
            continue

        link_match = MARKDOWN_LINK.search(line)
        if link_match:
            mapping[link_match.group("name").strip()] = link_match.group("url").strip()

    return mapping


def replace_placeholders(text: str, mapping: dict[str, str]) -> str:
    converted = text
    for name, url in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        placeholder = re.compile(rf"\[{re.escape(name)}\](?!\()")
        converted = placeholder.sub(f"[{name}]({url})", converted)
    return converted


def update_file(path: Path, converted: str) -> None:
    original = path.read_text(encoding="utf-8")
    if converted != original:
        path.write_text(converted + ("\n" if not converted.endswith("\n") else ""), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert GitHub file mappings to clickable Markdown links."
    )
    parser.add_argument("path", type=Path, nargs="+", help="Text file(s) to update in place")
    parser.add_argument(
        "--mapping",
        type=Path,
        help="Mapping file used to replace [filename] placeholders in target files",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Print the converted content without writing changes",
    )
    args = parser.parse_args()

    if args.mapping:
        mapping = load_mapping(args.mapping)
        for path in args.path:
            text = path.read_text(encoding="utf-8")
            converted = replace_placeholders(text, mapping)
            if args.check:
                print(f"--- {path} ---")
                print(converted)
            else:
                update_file(path, converted)
        return 0

    for path in args.path:
        text = path.read_text(encoding="utf-8")
        converted = convert_text(text)

        if args.check:
            print(f"--- {path} ---")
            print(converted)
        else:
            update_file(path, converted)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
