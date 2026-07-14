"""
案例数据仓库 - 负责案例数据的查询
"""
from typing import Optional, List, Dict, Any
from backend.database.db import get_db_connection


# 8个维度字段映射
DIMENSION_FIELDS = [
    "population_practice",
    "land_practice",
    "nature_practice",
    "transport_practice",
    "industry_practice",
    "economy_practice",
    "policy_practice",
    "culture_practice",
]


def get_all_cases() -> List[Dict[str, Any]]:
    """获取所有案例"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='case_library'"
            )
            if not cursor.fetchone():
                return []

            cursor = conn.execute("SELECT * FROM case_library")
            rows = cursor.fetchall()
            if not rows:
                return []

            cases = []
            for row in rows:
                row_dict = dict(row)
                cases.append(_build_case_from_row(row_dict))

            return cases

    except Exception as e:
        print(f"[case_repo] 获取案例列表失败: {e}")
        return []


def get_case_by_id(case_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取单个案例"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM case_library WHERE id = ?",
                (case_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            return _build_case_from_row(dict(row))

    except Exception as e:
        print(f"[case_repo] 获取案例详情失败: {e}")
        return None


def get_case_by_name(case_name: str) -> Optional[Dict[str, Any]]:
    """根据案例名称获取案例"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM case_library WHERE case_name = ?",
                (case_name,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            return _build_case_from_row(dict(row))

    except Exception as e:
        print(f"[case_repo] 根据名称获取案例失败: {e}")
        return None


def get_case_by_village_id(village_id: int) -> Optional[Dict[str, Any]]:
    """根据村庄ID获取案例"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM case_library WHERE village_id = ?",
                (village_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            return _build_case_from_row(dict(row))

    except Exception as e:
        print(f"[case_repo] 根据村庄ID获取案例失败: {e}")
        return None


def _build_case_from_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """从数据库行构建案例对象"""
    # 基本信息
    case = {
        'id': row.get('id'),
        'case_name': row.get('case_name', ''),
        'village_id': row.get('village_id'),
        'industry': row.get('industry', ''),
        'province': row.get('province', ''),
        'city': row.get('city', ''),
        'county': row.get('county', ''),
        'description': row.get('description', ''),
    }

    # 8个维度做法
    practices = {}
    for field in DIMENSION_FIELDS:
        practices[field] = row.get(field, '') or ''

    case['practices'] = practices

    return case
