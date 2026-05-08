#!/usr/bin/env python3
"""
更新所有擂台 overview.zh.json 和 overview.en.json 中的日期字段
将"最近更新"和"最近审阅"更新为当天日期
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path


def get_today_date():
    """获取今天日期，格式 YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")


def update_overview_dates(file_path, today_date):
    """更新单个 overview JSON 文件的日期"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检测是中文还是英文文件
    is_chinese = 'overview.zh.json' in file_path

    # 记录是否有更新
    updated = False

    if is_chinese:
        # 中文：最近更新、最近审阅
        # 匹配 "- **最近更新**: YYYY-MM-DD"
        pattern_update = r'(- \*\*最近更新\*\*: )(\d{4}-\d{2}-\d{2})'
        pattern_review = r'(- \*\*最近审阅\*\*: )(\d{4}-\d{2}-\d{2})'

        new_content, count1 = re.subn(pattern_update, rf'\g<1>{today_date}', content)
        new_content, count2 = re.subn(pattern_review, rf'\g<1>{today_date}', new_content)

        if count1 > 0 or count2 > 0:
            updated = True
            print(f"  ✓ 更新中文日期: 最近更新 ({count1}), 最近审阅 ({count2})")
    else:
        # 英文：Last Updated、Last Reviewed
        pattern_update = r'(- \*\*Last Updated\*\*: )(\d{4}-\d{2}-\d{2})'
        pattern_review = r'(- \*\*Last Reviewed\*\*: )(\d{4}-\d{2}-\d{2})'

        new_content, count1 = re.subn(pattern_update, rf'\g<1>{today_date}', content)
        new_content, count2 = re.subn(pattern_review, rf'\g<1>{today_date}', new_content)

        if count1 > 0 or count2 > 0:
            updated = True
            print(f"  ✓ 更新英文日期: Last Updated ({count1}), Last Reviewed ({count2})")

    if updated:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    else:
        print(f"  ⚠ 未找到日期字段或无需更新")
        return False


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

        # 处理中文文件
        zh_file = item / 'overview.zh.json'
        if zh_file.exists():
            try:
                print(f"  📄 {zh_file.name}")
                if update_overview_dates(str(zh_file), today_date):
                    updated_count += 1
            except Exception as e:
                print(f"  ✗ 错误: {e}")
                error_count += 1
        else:
            print(f"  ⚠ 未找到中文文件")

        # 处理英文文件
        en_file = item / 'overview.en.json'
        if en_file.exists():
            try:
                print(f"  📄 {en_file.name}")
                if update_overview_dates(str(en_file), today_date):
                    updated_count += 1
            except Exception as e:
                print(f"  ✗ 错误: {e}")
                error_count += 1
        else:
            print(f"  ⚠ 未找到英文文件")

    print(f"\n" + "=" * 60)
    print(f"完成！")
    print(f"  成功更新文件数: {updated_count}")
    print(f"  错误数: {error_count}")
    print(f"=" * 60)


if __name__ == '__main__':
    main()
