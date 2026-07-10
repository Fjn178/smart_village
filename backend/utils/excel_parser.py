from typing import Any, Dict, List, Optional
import os
import io
import pandas as pd
import csv
# 引入 validator（c 的长处）
from utils.validator import ValidationError, validate_row_against_schema
# ==================== 通用解析工具（c的部分） ====================

def _read_with_pandas(path: str, sheet_name: Optional[int | str] = 0):
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl" if path.lower().endswith(".xlsx") else None)
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def _read_csv(path: str):
    rows: List[Dict[str, Any]] = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k: (v if v != '' else None) for k, v in r.items()})
    return rows
def parse_excel(
    path_or_bytes, 
    schema: Optional[Dict[str, Dict[str, Any]]] = None, 
    sheet_name: Optional[int | str] = 0,
    is_bytes: bool = False
) -> List[Dict[str, Any]]:
    """
    通用 Excel/CSV 解析器（A 的完整功能）
    - 支持文件路径或字节流
    - 支持传入 schema 校验
    - 校验通过返回记录列表，失败抛出 ValidationError
    """
    # 统一转为记录列表
    if is_bytes:
        df = pd.read_excel(io.BytesIO(path_or_bytes), sheet_name=sheet_name, engine="openpyxl")
        df = df.where(pd.notnull(df), None)
        rows = df.to_dict(orient="records")
    else:
        if not os.path.exists(path_or_bytes):
            raise FileNotFoundError(path_or_bytes)
        lower = path_or_bytes.lower()
        if lower.endswith('.csv'):
            rows = _read_csv(path_or_bytes)
        else:
            try:
                rows = _read_with_pandas(path_or_bytes, sheet_name=sheet_name)
            except Exception as e:
                raise RuntimeError(f"failed to read excel file: {e}")

    # 没有 schema 就直接返回原始数据
    if schema is None:
        return rows

    # 按 schema 逐行校验
    errors = []
    valid_rows: List[Dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        row_errors = validate_row_against_schema(row, schema)
        if row_errors:
            for err in row_errors:
                err.setdefault('row', idx)
            errors.extend(row_errors)
        else:
            valid_rows.append(row)

    if errors:
        raise ValidationError(errors)

    return valid_rows


# ==================== 业务专用函数（l的逻辑，放到这里作为封装） ====================

def parse_and_validate_excel(file_bytes, indicator_map):
    """
    专门用于村庄指标导入的业务函数（B 的功能）
    内部调用上面的通用 parse_excel，然后做业务组装
    """
    # 1. 构建校验规则 Schema
    schema = {
        "村庄名称": {"required": True, "type": "str"},
        "所属乡镇": {"required": True, "type": "str"}
    }
    for col, indicator_def in indicator_map.items():
        if hasattr(indicator_def, 'data_type') and indicator_def.data_type == '文本':
            schema[col] = {"required": False, "type": "str"}
        else:
            schema[col] = {"required": False, "type": "float", "min": 0}

    # 2. 调用通用解析器（A 的功能）
    try:
        rows = parse_excel(file_bytes, schema=schema, is_bytes=True)
    except ValidationError as e:
        # 把校验错误转换成 B 需要的格式
        errors = []
        for err in e.errors:
            errors.append({
                "row": err.get('row', 0),
                "field": err.get('field', ''),
                "msg": err.get('message', '')
            })
        return False, [], errors
    # 3. 组装成 l需要的业务数据结构
    valid_rows = []
    for row in rows:
        village_name = row.get('村庄名称', '')
        town = row.get('所属乡镇', '')
        indicator_values = {}
        for col, ind_id in indicator_map.items():
            if col in row and row[col] is not None:
                val = row[col]
                # 判断是文本还是数值
                if isinstance(val, str):
                    indicator_values[ind_id] = {'text': val}
                else:
                    indicator_values[ind_id] = {'numeric': float(val)}
        valid_rows.append({
            "village_name": village_name,
            "town": town,
            "indicators": indicator_values
        })

    return True, valid_rows, []