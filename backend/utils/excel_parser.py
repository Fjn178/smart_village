from __future__ import annotations

from typing import Any, Dict, List, Optional
import os

from validator import ValidationError, validate_row_against_schema


def _read_with_pandas(path: str, sheet_name: Optional[int | str] = 0):
    import pandas as pd

    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl" if path.lower().endswith(".xlsx") else None)
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def _read_csv(path: str):
    import csv

    rows: List[Dict[str, Any]] = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k: (v if v != '' else None) for k, v in r.items()})
    return rows


def parse_excel(path: str, schema: Optional[Dict[str, Dict[str, Any]]] = None, sheet_name: Optional[int | str] = 0) -> List[Dict[str, Any]]:
    """读取并校验 Excel/CSV 文件。

    - path: 文件路径（支持 .xlsx/.xls/.csv）
    - schema: 字段校验规则（见 `validator.validate_row_against_schema`）

    返回：校验通过的记录列表；若存在校验错误抛出 `ValidationError`。
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    lower = path.lower()
    if lower.endswith('.csv'):
        rows = _read_csv(path)
    else:
        try:
            rows = _read_with_pandas(path, sheet_name=sheet_name)
        except Exception as e:
            raise RuntimeError(f"failed to read excel file: {e}")

    if schema is None:
        return rows

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
