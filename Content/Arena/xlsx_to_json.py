#!/usr/bin/env python3
"""
自动检测 V1/V2 格式的 xlsx 转换脚本
输入：List of Arenas.xlsx
输出：page.zh.json, page.common.json
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import posixpath
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

OUTPUT_ZH_JSON_NAME = "page.zh.json"
OUTPUT_COMMON_JSON_NAME = "page.common.json"
OUTPUT_CSV_NAME = "List of Arenas.csv"
ROW_FIELDS = [
    "arena_no",
    "title",
    "champion",
    "related_references",
    "verification_status",
    "highlights",
    "industry",
    "category",
    "speed",
    "quality",
    "security",
    "cost",
    "challenger",
    "video_url_zh",
    "video_url_global",
    "video_cover_image_url",
    "homepage_display_order",
]
ZH_JSON_FIELDS = [
    field for field in ROW_FIELDS if field not in {"video_url_zh", "video_url_global", "video_cover_image_url", "homepage_display_order"}
]

# V1（历史）：列 B~Q（索引 1~16），含“关联引用”列
XLSX_COLS_V1 = {
    "arena_no": 1,
    "title": 2,
    "champion": 3,
    "related_references": 4,
    "verification_status": 5,
    "highlights": 6,
    "industry": 7,
    "category": 8,
    "speed": 9,
    "quality": 10,
    "security": 11,
    "cost": 12,
    "challenger": 13,
    "video_url_zh": 14,
    "video_url_global": 15,
    "video_cover_image_url": 16,
    "homepage_display_order": 17,
}

# V2（当前）：列 A~Q（索引 0~16），D 列为“关联引用”
XLSX_COLS_V2 = {
    "arena_no": 0,
    "title": 1,
    "champion": 2,
    "related_references": 3,
    "verification_status": 4,
    "highlights": 5,
    "industry": 6,
    "category": 7,
    "speed": 8,
    "quality": 9,
    "security": 10,
    "cost": 11,
    "challenger": 12,
    "video_url_zh": 13,
    "video_url_global": 14,
    "video_cover_image_url": 15,
    "homepage_display_order": 16,
}

HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    "arena_no": ("擂台编号",),
    "title": ("擂台名称",),
    "champion": ("本周擂主",),
    "related_references": ("关联引用",),
    "verification_status": ("验证状态",),
    "highlights": ("亮点",),
    "industry": ("行业类别",),
    "category": ("应用类别",),
    "speed": ("速度",),
    "quality": ("质量",),
    "security": ("安全",),
    "cost": ("成本",),
    "challenger": ("攻擂中",),
    "video_url_zh": ("国内视频链接", "视频链接"),
    "video_url_global": ("国际视频链接", "海外视频链接"),
    "video_cover_image_url": ("视频封面图片链接", "视频封面链接"),
    "homepage_display_order": ("首页展示顺序",),
}


def get_relationship_id(sheet: ET.Element) -> str | None:
    for key, value in sheet.attrib.items():
        if key == "r:id" or key.endswith("}id"):
            return value
    return None


def col_letters_to_index(ref: str) -> int:
    match = re.match(r"([A-Za-z]+)", ref)
    if not match:
        return 0
    letters = match.group(1).upper()
    index = 0
    for ch in letters:
        index = index * 26 + (ord(ch) - ord("A") + 1)
    return max(index - 1, 0)


def load_xml(zipf: zipfile.ZipFile, name: str) -> ET.Element:
    with zipf.open(name) as f:
        return ET.parse(f).getroot()


def parse_shared_strings(zipf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zipf.namelist():
        return []

    root = load_xml(zipf, "xl/sharedStrings.xml")
    items: list[str] = []
    for si in root.findall("{*}si"):
        text_parts = [t.text or "" for t in si.findall(".//{*}t")]
        items.append("".join(text_parts))
    return items


def parse_sheet_paths(zipf: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook = load_xml(zipf, "xl/workbook.xml")
    rels = load_xml(zipf, "xl/_rels/workbook.xml.rels")

    rel_map: dict[str, str] = {}
    for rel in rels.findall("{*}Relationship"):
        rel_id = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if rel_id and target:
            # Handle absolute paths (e.g., /xl/worksheets/sheet2.xml)
            if target.startswith("/"):
                full_path = target.lstrip("/")
            else:
                full_path = posixpath.normpath(posixpath.join("xl", target))
            rel_map[rel_id] = full_path

    results: list[tuple[str, str]] = []
    for sheet in workbook.findall("{*}sheets/{*}sheet"):
        name = sheet.attrib.get("name", "Sheet")
        rel_id = get_relationship_id(sheet)
        if not rel_id:
            continue
        path = rel_map.get(rel_id)
        if path and path in zipf.namelist():
            results.append((name, path))

    return results


def read_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")

    if cell_type == "inlineStr":
        parts = [t.text or "" for t in cell.findall(".//{*}t")]
        return "".join(parts)

    v = cell.find("{*}v")
    if v is None or v.text is None:
        return ""

    raw = v.text
    if cell_type == "s":
        try:
            return shared_strings[int(raw)]
        except (ValueError, IndexError):
            return raw
    if cell_type == "b":
        return "TRUE" if raw == "1" else "FALSE"
    return raw


def parse_sheet_rows(zipf: zipfile.ZipFile, sheet_path: str, shared_strings: list[str]) -> list[list[str]]:
    root = load_xml(zipf, sheet_path)

    row_maps: list[dict[int, str]] = []
    max_col = 0

    for row in root.findall("{*}sheetData/{*}row"):
        row_map: dict[int, str] = {}
        for cell in row.findall("{*}c"):
            ref = cell.attrib.get("r", "")
            col_idx = col_letters_to_index(ref)
            row_map[col_idx] = read_cell_value(cell, shared_strings)
            if col_idx + 1 > max_col:
                max_col = col_idx + 1
        row_maps.append(row_map)

    if max_col == 0:
        return []

    rows: list[list[str]] = []
    for row_map in row_maps:
        values = [""] * max_col
        for idx, val in row_map.items():
            if 0 <= idx < max_col:
                values[idx] = val
        rows.append(values)

    return rows


def detect_version(rows: list[list[str]]) -> str:
    """
    检测 xlsx 格式版本
    V2: 第一列(A列，索引0)是"擂台编号"
    V1: 第一列是空的，第二列(B列，索引1)是"擂台编号"
    """
    if not rows:
        return "v1"

    # 找第一个非空行作为表头行
    header_row = None
    for row in rows:
        # 检查是否有任何单元格包含"擂台编号"
        for cell in row:
            if "擂台编号" in cell:
                header_row = row
                break
        if header_row:
            break

    if not header_row:
        return "v1"  # 默认v1

    # 检查 A 列（索引0）是否是"擂台编号"
    col_a = header_row[0].strip() if len(header_row) > 0 else ""

    # 检查 B 列（索引1）是否是"擂台编号"
    col_b = header_row[1].strip() if len(header_row) > 1 else ""

    if col_a == "擂台编号":
        return "v2"
    elif col_b == "擂台编号":
        return "v1"
    else:
        # 如果都检测不到，看 A 列是否有内容
        # V2 的 A 列有内容，V1 的 A 列通常是空的
        return "v2" if col_a else "v1"


def clean_value(value: str) -> str:
    text = value.strip()
    if text.endswith(".0"):
        number_text = text[:-2]
        if number_text.isdigit():
            return number_text
    return text


def find_header_col_map(rows: list[list[str]]) -> dict[str, int]:
    for row in rows[:5]:
        normalized_row = [clean_value(cell) for cell in row]
        if "擂台编号" not in normalized_row:
            continue

        col_map: dict[str, int] = {}
        for field, aliases in HEADER_ALIASES.items():
            found_idx = None
            for alias in aliases:
                for idx, cell in enumerate(normalized_row):
                    if cell == alias:
                        found_idx = idx
                        break
                if found_idx is not None:
                    break
            if found_idx is not None:
                col_map[field] = found_idx
        return col_map
    return {}


def normalize_arena_no(text: str) -> str:
    value = clean_value(text)
    if value.isdigit():
        return str(int(value))
    try:
        f = float(value)
        if math.isfinite(f) and f.is_integer():
            return str(int(f))
    except ValueError:
        pass
    return value


def normalize_int_or_text(text: str) -> int | str | None:
    value = clean_value(text)
    if not value:
        return None
    if value.isdigit():
        return int(value)
    try:
        f = float(value)
        if math.isfinite(f) and f.is_integer():
            return int(f)
    except ValueError:
        pass
    return value


def build_rows(rows: list[list[str]], version: str) -> list[dict[str, str]]:
    xlsx_cols = XLSX_COLS_V2 if version == "v2" else XLSX_COLS_V1
    header_cols = find_header_col_map(rows)

    def get_cell(row: list[str], key: str) -> str:
        if key in header_cols:
            idx = header_cols[key]
            return row[idx] if len(row) > idx else ""
        idx = xlsx_cols[key]
        return row[idx] if len(row) > idx else ""

    result: list[dict[str, str]] = []
    for row in rows:
        arena_no = normalize_arena_no(get_cell(row, "arena_no"))
        title = clean_value(get_cell(row, "title"))

        if not arena_no or not arena_no.isdigit():
            continue
        if not title or "敬请期待" in title:
            continue

        item: dict[str, str] = {}
        for key in ROW_FIELDS:
            item[key] = clean_value(get_cell(row, key))

        # 兼容旧表：只有一个“视频链接”列时，补全另一列
        if not item["video_url_zh"] and "video_url_zh" not in header_cols and "video_url_global" not in header_cols:
            item["video_url_zh"] = clean_value(get_cell(row, "video_url_zh"))
        if not item["video_url_global"] and "video_url_global" not in header_cols:
            item["video_url_global"] = item["video_url_zh"]

        item["arena_no"] = arena_no
        result.append(item)

    return result


def split_rows_for_outputs(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str | int | None]]]:
    zh_rows: list[dict[str, str]] = []
    common_rows: list[dict[str, str | int | None]] = []

    for row in rows:
        zh_rows.append({key: row.get(key, "") for key in ZH_JSON_FIELDS})
        video_url_zh = clean_value(row.get("video_url_zh", ""))
        video_url_global = clean_value(row.get("video_url_global", ""))
        video_cover_image_url = clean_value(row.get("video_cover_image_url", ""))
        homepage_display_order = normalize_int_or_text(row.get("homepage_display_order", ""))
        common_rows.append({
            "arena_no": row.get("arena_no", ""),
            "video_url_zh": video_url_zh if video_url_zh else None,
            "video_url_global": video_url_global if video_url_global else None,
            "video_cover_image_url": video_cover_image_url if video_cover_image_url else None,
            "homepage_display_order": homepage_display_order,
        })

    return zh_rows, common_rows


def parse_xlsx(xlsx_path: Path) -> tuple[list[list[str]], str]:
    """解析 xlsx，返回行数据和检测到的版本"""
    with zipfile.ZipFile(xlsx_path, "r") as zipf:
        shared_strings = parse_shared_strings(zipf)
        sheets = parse_sheet_paths(zipf)
        if not sheets:
            raise ValueError("No worksheets found in workbook.")

        _, sheet_path = sheets[0]
        rows = parse_sheet_rows(zipf, sheet_path, shared_strings)

    version = detect_version(rows)
    return rows, version


def to_json_and_csv(xlsx_path: Path) -> tuple[Path, Path, Path]:
    if not xlsx_path.exists():
        raise FileNotFoundError(f"File not found: {xlsx_path}")

    rows, version = parse_xlsx(xlsx_path)

    json_output_path = xlsx_path.parent / OUTPUT_ZH_JSON_NAME
    common_output_path = xlsx_path.parent / OUTPUT_COMMON_JSON_NAME
    csv_output_path = xlsx_path.parent / OUTPUT_CSV_NAME
    parsed_rows = build_rows(rows, version)
    zh_rows, common_rows = split_rows_for_outputs(parsed_rows)

    with json_output_path.open("w", encoding="utf-8") as f:
        json.dump(zh_rows, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with common_output_path.open("w", encoding="utf-8") as f:
        json.dump(common_rows, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with csv_output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ROW_FIELDS)
        writer.writeheader()
        writer.writerows(parsed_rows)

    print(f"Detected format: {version.upper()}")
    return json_output_path, common_output_path, csv_output_path


def main() -> None:
    default_file = Path(__file__).resolve().parent / "List of Arenas.xlsx"

    parser = argparse.ArgumentParser(
        description="Generate 'page.zh.json' and 'page.common.json' from List of Arenas.xlsx (auto-detect V1/V2 format)."
    )
    parser.add_argument(
        "xlsx",
        nargs="?",
        default=str(default_file),
        help="Path to the .xlsx file (default: Content/Arena/List of Arenas.xlsx)",
    )
    args = parser.parse_args()

    xlsx_path = Path(args.xlsx).expanduser().resolve()
    json_output, common_output, csv_output = to_json_and_csv(xlsx_path)

    print(f"Input: {xlsx_path}")
    print(f"Generated: {json_output}")
    print(f"Generated: {common_output}")
    print(f"Generated: {csv_output}")


if __name__ == "__main__":
    main()
