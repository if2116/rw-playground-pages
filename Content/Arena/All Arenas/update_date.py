#!/usr/bin/env python3
"""
更新所有擂台中的更新日期字段
将 overview.raw.json、overview.zh.json、overview.en.json 和 Original Documents/main.md 中的
"最近更新"和"Last Updated"更新为当天日期
"""

import re
from datetime import datetime
from pathlib import Path

DATE_PATTERN = r"\d{4}-\d{2}-\d{2}"

OVERVIEW_ZH_PATTERNS = (
    ("最近更新", rf"(- \*\*最近更新\*\*: )({DATE_PATTERN})"),
)

OVERVIEW_EN_PATTERNS = (
    ("Last Updated", rf"(- \*\*Last Updated\*\*: )({DATE_PATTERN})"),
)

ORIGINAL_DOC_PATTERNS = (
    ("最近更新", rf"(最近更新[：:]\s*)({DATE_PATTERN})"),
    ("Last Updated", rf"(Last Updated[:：]\s*)({DATE_PATTERN})"),
)


def get_today_date():
    """获取今天日期，格式 YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")


def replace_dates(content, today_date, patterns):
    """按给定模式更新日期，返回更新后的内容和匹配结果。"""
    new_content = content
    matches = []

    for label, pattern in patterns:
        new_content, count = re.subn(pattern, rf"\g<1>{today_date}", new_content)
        if count > 0:
            matches.append((label, count))

    return new_content, matches


def update_file_dates(file_path, today_date, patterns):
    """更新单个文件的日期"""
    content = file_path.read_text(encoding="utf-8")
    new_content, matches = replace_dates(content, today_date, patterns)

    if not matches:
        print("  ⚠ 未找到日期字段")
        return False

    if new_content == content:
        labels = ", ".join(f"{label} ({count})" for label, count in matches)
        print(f"  - 日期已是最新: {labels}")
        return False

    file_path.write_text(new_content, encoding="utf-8")
    labels = ", ".join(f"{label} ({count})" for label, count in matches)
    print(f"  ✓ 更新日期: {labels}")
    return True


def update_if_exists(file_path, today_date, patterns, missing_message):
    """文件存在时更新，不存在时输出提示。"""
    if not file_path.exists():
        print(f"  ⚠ {missing_message}")
        return False, False

    try:
        print(f"  📄 {file_path.name if file_path.name == 'main.md' else file_path.name}")
        return update_file_dates(file_path, today_date, patterns), False
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return False, True


def main():
    """主函数"""
    base_dir = Path(__file__).parent
    today_date = get_today_date()

    print(f"=" * 60)
    print(f"日期更新脚本")
    print(f"今天日期: {today_date}")
    print(f"=" * 60)

    updated_count = 0
    error_count = 0

    # 遍历所有子目录
    for item in sorted(base_dir.iterdir()):
        if not item.is_dir():
            continue

        # 跳过非擂台目录（如 common, __pycache__ 等）
        if item.name.startswith('.') or item.name in ['common', '__pycache__']:
            continue

        # 只处理编号开头的擂台目录 (1-xxx, 2-xxx, ...)
        if not re.match(r'^\d+-.+', item.name):
            continue

        print(f"\n📁 处理擂台: {item.name}")

        raw_file = item / 'overview.raw.json'
        updated, errored = update_if_exists(raw_file, today_date, OVERVIEW_ZH_PATTERNS, "未找到 raw 文件")
        updated_count += int(updated)
        error_count += int(errored)

        zh_file = item / 'overview.zh.json'
        updated, errored = update_if_exists(zh_file, today_date, OVERVIEW_ZH_PATTERNS, "未找到中文文件")
        updated_count += int(updated)
        error_count += int(errored)

        en_file = item / 'overview.en.json'
        updated, errored = update_if_exists(en_file, today_date, OVERVIEW_EN_PATTERNS, "未找到英文文件")
        updated_count += int(updated)
        error_count += int(errored)

        original_main = item / 'Original Documents' / 'main.md'
        updated, errored = update_if_exists(
            original_main,
            today_date,
            ORIGINAL_DOC_PATTERNS,
            "未找到原始文档 main.md",
        )
        updated_count += int(updated)
        error_count += int(errored)

    print(f"\n" + "=" * 60)
    print(f"完成！")
    print(f"  成功更新文件数: {updated_count}")
    print(f"  错误数: {error_count}")
    print(f"=" * 60)


if __name__ == '__main__':
    main()
