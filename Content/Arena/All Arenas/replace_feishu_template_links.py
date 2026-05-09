#!/usr/bin/env python3
"""Replace known Feishu template links with GitHub file links.

The script is intentionally scoped to the arena content tree and only replaces
the seven template links from the mapping request. Other Feishu links, such as
practice details or validation documents, are left untouched.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ARENA_ROOT = Path(__file__).resolve().parent

LINK_REPLACEMENTS = {
    "https://gvxnc4ekbvn.feishu.cn/wiki/RKTEwqiluiLZEFkciaCcj2pfnhg": "https://github.com/THU-ZJAI/Real-World-AI_Source/blob/main/Template/%E4%BA%A7%E5%93%81%E9%9C%80%E6%B1%82%E6%96%87%E6%A1%A3%EF%BC%88PRD%EF%BC%89%E6%A8%A1%E6%9D%BF.docx",
    "https://gvxnc4ekbvn.feishu.cn/wiki/HKZGwXetBije9HklRQmcAe94nZE": "https://github.com/THU-ZJAI/Real-World-AI_Source/blob/main/Template/%E5%88%9D%E6%AD%A5%E9%AA%8C%E8%AF%81%E6%8A%A5%E5%91%8A%E6%A8%A1%E6%9D%BF.docx",
    "https://gvxnc4ekbvn.feishu.cn/wiki/PC8FwObgwiMwVPkM0i4cYkr2nYf": "https://github.com/THU-ZJAI/Real-World-AI_Source/blob/main/Template/%E5%88%9D%E6%AD%A5%E9%AA%8C%E8%AF%81%E9%9C%80%E6%B1%82%E6%96%87%E6%A1%A3%E6%A8%A1%E6%9D%BF.docx",
    "https://gvxnc4ekbvn.feishu.cn/wiki/Z4U4wXExviT9UOkeJIGc8EnKnAh": "https://github.com/THU-ZJAI/Real-World-AI_Source/blob/main/Template/%E5%AD%90%E4%BB%BB%E5%8A%A1%E7%AE%97%E6%B3%95%E9%9C%80%E6%B1%82%E6%A8%A1%E6%9D%BF.docx",
    "https://gvxnc4ekbvn.feishu.cn/wiki/YkE8wV1oBitb7Gk08AycdsLZnvc": "https://github.com/THU-ZJAI/Real-World-AI_Source/blob/main/Template/%E6%8A%95%E7%A8%BF%E6%A8%A1%E6%9D%BF%EF%BC%88RWAI%E5%9B%A2%E9%98%9F%E5%86%85%E9%83%A8%E7%89%88%EF%BC%89.docx",
    "https://gvxnc4ekbvn.feishu.cn/wiki/R0jrwxeDfiBpsEkqZdYcZtgJncd": "https://github.com/THU-ZJAI/Real-World-AI_Source/blob/main/Template/%E7%AB%8B%E9%A1%B9%E6%8A%A5%E5%91%8A%E6%A8%A1%E6%9D%BF.docx",
    "https://gvxnc4ekbvn.feishu.cn/wiki/TXOqw6LDKiN1FrkhRtvcT6JdnVc": "https://github.com/THU-ZJAI/Real-World-AI_Source/blob/main/Template/%E9%A1%B9%E7%9B%AE%E5%90%88%E4%BD%9C%E9%9C%80%E6%B1%82%E9%97%AE%E8%AF%A2%E4%B9%A6%E6%A8%A1%E6%9D%BF.docx",
}

TEXT_SUFFIXES = {".json", ".md", ".txt", ".html"}
SKIP_DIRS = {"media", "__pycache__"}


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return sorted(files)


def replace_links(text: str) -> tuple[str, int]:
    total = 0
    updated = text
    for feishu_url, github_url in LINK_REPLACEMENTS.items():
        plain_count = updated.count(feishu_url)

        updated = updated.replace(f"{feishu_url}?from=from_copylink", github_url)
        updated = updated.replace(feishu_url, github_url)

        total += plain_count

    return updated, total


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace known Feishu template links under Content/Arena/All Arenas."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ARENA_ROOT,
        help="Arena content root. Defaults to the directory containing this script.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show files that would be changed without writing them.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    changed_files: list[tuple[Path, int]] = []
    total_replacements = 0

    for path in iter_text_files(root):
        text = path.read_text(encoding="utf-8")
        updated, replacements = replace_links(text)
        if replacements == 0:
            continue

        changed_files.append((path, replacements))
        total_replacements += replacements
        if not args.dry_run:
            path.write_text(updated, encoding="utf-8")

    mode = "Would update" if args.dry_run else "Updated"
    for path, replacements in changed_files:
        print(f"{mode}: {path.relative_to(root)} ({replacements} replacements)")

    print(f"{mode} {len(changed_files)} files, {total_replacements} replacements.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
