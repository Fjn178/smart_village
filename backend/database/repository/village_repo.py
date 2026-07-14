"""
村庄数据仓库 - 负责村庄基础数据的查询
"""
from typing import Optional, List, Dict, Any
from backend.database.db import get_db_connection


def get_village_name(village_id: int) -> Optional[str]:
    """根据ID获取村庄名称"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM village WHERE id = ?",
                (village_id,)
            )
            row = cursor.fetchone()
            return row["name"] if row else None
    except Exception as e:
        print(f"[village_repo] 获取村庄名称失败: {e}")
        return None


def get_all_villages() -> List[Dict[str, Any]]:
    """获取所有村庄基本信息"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, province, city, county, town FROM village"
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"[village_repo] 获取村庄列表失败: {e}")
        return []


def get_village_basic_info(village_id: int) -> Optional[Dict[str, Any]]:
    """获取单个村庄基本信息"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, province, city, county, town FROM village WHERE id = ?",
                (village_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)
    except Exception as e:
        print(f"[village_repo] 获取村庄信息失败: {e}")
        return None


def get_village_indicator_value(village_id: int, indicator_id: int) -> Optional[float]:
    """获取某个村庄的某个指标值"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM village_indicators WHERE village_id = ? AND indicator_id = ?",
                (village_id, indicator_id)
            )
            row = cursor.fetchone()
            return row["value"] if row else None
    except Exception as e:
        print(f"[village_repo] 获取指标值失败: {e}")
        return None


def get_village_all_indicators(village_id: int) -> Dict[int, float]:
    """获取某个村庄的所有指标值，返回 {indicator_id: value}"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT indicator_id, value FROM village_indicators WHERE village_id = ?",
                (village_id,)
            )
            rows = cursor.fetchall()
            return {row["indicator_id"]: row["value"] for row in rows}
    except Exception as e:
        print(f"[village_repo] 获取所有指标失败: {e}")
        return {}


def get_all_village_indicator_values() -> Dict[int, Dict[int, float]]:
    """
    获取所有村庄的所有指标值
    返回: {village_id: {indicator_id: value}}
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT village_id, indicator_id, value FROM village_indicators"
            )
            rows = cursor.fetchall()
            
            result = {}
            for row in rows:
                vid = row["village_id"]
                iid = row["indicator_id"]
                value = row["value"]
                
                if vid not in result:
                    result[vid] = {}
                result[vid][iid] = value
            
            return result
    except Exception as e:
        print(f"[village_repo] 获取所有村庄指标失败: {e}")
        return {}
