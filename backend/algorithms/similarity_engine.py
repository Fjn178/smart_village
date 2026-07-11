from __future__ import annotations

import math
import sqlite3
import os
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database.db import get_db_connection

INDICATOR_IDS: List[int] = list(range(1, 157))

CATEGORY_WEIGHTS: Dict[str, float] = {
    "population": 1.0,
    "land": 0.8,
    "nature": 0.7,
    "transport": 1.2,
    "industry": 1.5,
    "economy": 1.4,
    "policy": 0.9,
    "culture": 1.1,
}

INDICATOR_CATEGORIES: Dict[str, List[int]] = {
    "population": list(range(1, 18)),
    "land": list(range(18, 36)),
    "nature": list(range(36, 49)),
    "transport": list(range(49, 72)),
    "industry": list(range(72, 102)),
    "economy": list(range(102, 118)),
    "policy": list(range(118, 141)),
    "culture": list(range(141, 157)),
}


def weighted_euclidean_distance(target: Sequence[float], case: Sequence[float], weights: Sequence[float]) -> float:
    """计算加权欧氏距离。"""
    if len(target) != len(case) or len(target) != len(weights):
        raise ValueError("target、case 和 weights 长度必须一致")

    total = 0.0
    for t, c, w in zip(target, case, weights):
        t_value = _normalize_number(t)
        c_value = _normalize_number(c)
        diff = t_value - c_value
        total += w * diff * diff

    return math.sqrt(total)


def distance_to_similarity_score(dist: float) -> float:
    """使用指数衰减，相似度更平滑。"""
    if dist is None:
        return 0.0
    dist = float(dist)
    if dist < 0:
        dist = abs(dist)
    score = 100.0 * math.exp(-dist * 0.3)
    return round(score, 2)


def get_case_count() -> int:
    """返回 case_library 表中的案例总数。"""
    try:
        with get_db_connection() as conn:
            if not _table_exists(conn, "case_library"):
                return 0
            cursor = conn.execute("SELECT COUNT(*) AS count FROM case_library")
            row = cursor.fetchone()
            return int(row["count"]) if row else 0
    except Exception:
        return 0


def get_village_name(village_id: int | str) -> str:
    """尝试读取目标村庄的名称。"""
    try:
        with get_db_connection() as conn:
            candidate_tables = ["village", "villages", "village_info", "case_library"]
            for table in candidate_tables:
                if not _table_exists(conn, table):
                    continue

                columns = _get_table_columns(conn, table)
                id_column = _find_column(columns, ["id", "village_id", "vid", "村庄id", "村庄编号"])
                name_column = _find_column(columns, ["name", "village_name", "村名", "村庄名称", "case_name", "案例名称"])
                if not id_column or not name_column:
                    continue

                sql = f"SELECT {name_column} FROM {table} WHERE {id_column} = ? LIMIT 1"
                cursor = conn.execute(sql, (village_id,))
                row = cursor.fetchone()
                if row and row[name_column] is not None:
                    return str(row[name_column])
    except Exception:
        pass

    return f"村庄ID: {village_id}"


def match_similar_cases(
    village_id: int | str,
    top_n: int = 5,
    weight_type: str = "equal",
    use_mock: bool = True,
) -> List[Dict[str, Any]]:
    """匹配目标村庄的相似案例。"""
    try:
        return _match_similar_cases(village_id, top_n=top_n, weight_type=weight_type)
    except Exception:
        return []


def get_similarity_recommendations(
    village_id: int | str,
    top_n: int = 5,
    weight_type: str = "equal",
    use_mock: bool = True,
    flask_response: bool = True,
) -> List[Dict[str, Any]]:
    """返回相似案例推荐结果。"""
    return match_similar_cases(village_id, top_n=top_n, weight_type=weight_type)


def _match_similar_cases(village_id: int | str, top_n: int, weight_type: str) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        target_vector = _get_village_indicator_vector(conn, village_id)
        if target_vector is None:
            return []

        target_vector = _normalize_vector(target_vector)
        case_rows = _load_case_library_rows(conn)
        if not case_rows:
            return []

        weights = _build_weights(len(target_vector), weight_type)
        distances: List[Dict[str, Any]] = []
        seen_case_ids = set()

        for row in case_rows:
            row_dict = dict(row)
            case_village_id = _extract_case_village_id(row_dict)
            if case_village_id is None:
                continue

            if str(case_village_id) == str(village_id):
                continue

            if case_village_id in seen_case_ids:
                continue

            case_vector = _get_village_indicator_vector(conn, case_village_id)
            if case_vector is None:
                continue

            case_vector = _normalize_vector(case_vector)
            distance = weighted_euclidean_distance(target_vector, case_vector, weights)
            similarity_score = distance_to_similarity_score(distance)
            seen_case_ids.add(case_village_id)

            distances.append(
                {
                    "case_name": _extract_case_text(row_dict, ["case_name", "案例名称", "name", "title"])
                    or f"案例 {row_dict.get('id') or row_dict.get('case_id') or case_village_id}",
                    "industry": _extract_case_text(row_dict, ["industry", "产业", "sector"]),
                    "distance": distance,
                    "similarity_score": round(similarity_score, 2),
                    "result": _extract_case_text(row_dict, ["result", "结果", "summary", "描述"]),
                    "key_practices": _extract_case_text(row_dict, ["key_practices", "关键做法", "best_practices", "practices"]),
                    "special_notes": _extract_case_text(row_dict, ["special_notes", "备注", "notes", "remarks"]),
                }
            )

        distances.sort(key=lambda item: item["distance"])
        return distances[:top_n]


def _build_weights(length: int, weight_type: str) -> List[float]:
    if weight_type == "equal":
        return [1.0] * length

    weights: List[float] = []
    for indicator_id in INDICATOR_IDS[:length]:
        category = _find_indicator_category(indicator_id)
        weights.append(CATEGORY_WEIGHTS.get(category, 1.0))
    return weights


def _normalize_number(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except Exception:
        return 0.0


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND lower(name)=?", (table_name.lower(),)
    )
    return cursor.fetchone() is not None



def _get_table_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall() if row]


def _find_column(columns: Iterable[str], desired_names: Sequence[str]) -> Optional[str]:
    lower_columns = [col.lower() for col in columns]
    for desired in desired_names:
        desired_lower = desired.lower()
        for idx, col_lower in enumerate(lower_columns):
            if desired_lower == col_lower or desired_lower in col_lower or col_lower in desired_lower:
                return list(columns)[idx]
    return None


def _get_village_indicator_vector(conn: sqlite3.Connection, village_id: int | str) -> Optional[List[float]]:
    if not _table_exists(conn, "village_indicators"):
        return None

    columns = _get_table_columns(conn, "village_indicators")
    village_id_col = _find_column(columns, ["village_id", "village", "vid", "村庄id", "村庄编号"])
    indicator_id_col = _find_column(columns, ["indicator_id", "indicator", "指标id", "指标编号"])
    value_col = _find_column(columns, ["value", "indicator_value", "val", "数据值", "value_num"])

    if not village_id_col or not indicator_id_col or not value_col:
        return None

    sql = f"SELECT {indicator_id_col} AS indicator_id, {value_col} AS value FROM village_indicators WHERE {village_id_col} = ?"
    cursor = conn.execute(sql, (village_id,))
    rows = cursor.fetchall()
    if not rows:
        return None

    values: Dict[int, float] = {}
    for row in rows:
        indicator_id = _to_int(row["indicator_id"])
        numeric_value = _normalize_number(row["value"])
        if indicator_id is not None and 1 <= indicator_id <= len(INDICATOR_IDS):
            values[indicator_id] = numeric_value

    if not values:
        return None

    result: List[float] = []
    for indicator_id in INDICATOR_IDS:
        if indicator_id in values:
            result.append(values[indicator_id])
        else:
            result.append(_get_category_median(conn, indicator_id))
    return result


def _load_case_library_rows(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    if not _table_exists(conn, "case_library"):
        return []
    cursor = conn.execute("SELECT * FROM case_library")
    return cursor.fetchall()


def _get_category_median(conn: sqlite3.Connection, indicator_id: int) -> float:
    category = _find_indicator_category(indicator_id)
    if category is None:
        return 0.0

    indicator_ids = INDICATOR_CATEGORIES.get(category, [])
    if not indicator_ids:
        return 0.0

    placeholders = ",".join("?" for _ in indicator_ids)
    cursor = conn.execute(
        f"SELECT value FROM village_indicators WHERE indicator_id IN ({placeholders}) AND value IS NOT NULL",
        tuple(indicator_ids),
    )
    raw_values = [_normalize_number(row["value"]) for row in cursor.fetchall()]
    if not raw_values:
        return 0.0

    raw_values.sort()
    mid = len(raw_values) // 2
    if len(raw_values) % 2 == 1:
        return raw_values[mid]
    return (raw_values[mid - 1] + raw_values[mid]) / 2.0


def _normalize_vector(vector: List[float]) -> List[float]:
    """Z-score 标准化。"""
    if not vector:
        return vector

    mean = sum(vector) / len(vector)
    std = math.sqrt(sum((x - mean) ** 2 for x in vector) / len(vector))
    if std == 0:
        return vector
    return [(x - mean) / std for x in vector]


def _find_indicator_category(indicator_id: int) -> Optional[str]:
    for category, ids in INDICATOR_CATEGORIES.items():
        if indicator_id in ids:
            return category
    return None


def _extract_case_village_id(row: Dict[str, Any]) -> Optional[int]:
    candidates = ["village_id", "case_village_id", "village", "村庄id", "村庄编号"]
    for candidate in candidates:
        if candidate in row and row[candidate] not in (None, ""):
            return _to_int(row[candidate])
    for key in row:
        lower_key = key.lower()
        if "village" in lower_key or "村庄" in lower_key:
            value = row[key]
            if value not in (None, ""):
                return _to_int(value)
    return None


def _extract_case_text(row: Dict[str, Any], keys: Sequence[str]) -> str:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return str(row[key])
    lower = {k.lower(): k for k in row.keys()}
    for key in keys:
        candidate = key.lower()
        for actual in lower:
            if candidate == actual or candidate in actual or actual in candidate:
                value = row[lower[actual]]
                if value not in (None, ""):
                    return str(value)
    return ""


def _to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(float(value))
    except Exception:
        try:
            return int(str(value).strip())
        except Exception:
            return None
