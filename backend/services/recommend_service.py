"""
推荐服务 - 相似案例推荐核心逻辑
"""
from typing import List, Dict, Any, Optional
from backend.algorithms.similarity_engine import match_similar_cases
from backend.database.repository import case_repo, village_repo


# 8个维度对应的前端展示名称
DIMENSION_NAMES = {
    "population": "人口资源",
    "land": "土地资源",
    "nature": "自然资源",
    "transport": "交通物流",
    "industry": "产业基础",
    "economy": "经济基础",
    "policy": "政策环境",
    "culture": "特色文化",
}


def get_recommendations(
    village_id: int,
    top_n: int = 6,
    weight_type: str = "equal"
) -> List[Dict[str, Any]]:
    """
    获取目标村庄的相似案例推荐

    Args:
        village_id: 目标村庄ID
        top_n: 返回的推荐案例数量,默认6
        weight_type: 权重类型，"equal"或"category"

    Returns:
        推荐案例列表,包含案例信息和8个维度的做法详情
    """
    # 1. 调用相似度引擎
    similar_cases = match_similar_cases(
        village_id=village_id,
        top_n=top_n,
        weight_type=weight_type
    )

    if not similar_cases:
        return []

    # 2. 获取目标村庄名称
    village_name = village_repo.get_village_name(village_id) or f"村庄{village_id}"

    # 3. 为每个案例补充8个维度的做法详情
    result = []
    for case in similar_cases:
        case_name = case.get("case_name", "")
        if not case_name:
            case_name = f"案例{case.get('id', '')}"
        
        # 从 case_repo 获取完整案例信息（含8个维度做法）
        case_detail = case_repo.get_case_by_name(case_name)
        
        if case_detail:
            # 构建8个维度的做法
            practices = {}
            for dim_key, dim_name in DIMENSION_NAMES.items():
                # 假设 case_library 表中有对应字段: population_practice, land_practice, ...
                field_name = f"{dim_key}_practice"
                practices[dim_name] = case_detail.get(field_name, "")
        else:
            # 如果没有详情，返回空
            practices = {dim_name: "" for dim_name in DIMENSION_NAMES.values()}
        
        # 组装返回数据
        result.append({
            "id": case.get("id"),
            "case_name": case_name,
            "industry": case.get("industry", ""),
            "similarity_score": case.get("similarity_score", 0),
            "distance": case.get("distance", 0),
            "key_practices": case.get("key_practices", ""),
            "special_notes": case.get("special_notes", ""),
            "practices": practices,  # 8个维度的做法详情
        })

    return result


def get_recommendation_detail(case_id: int) -> Optional[Dict[str, Any]]:
    """
    获取单个案例的详细信息(含8个维度做法)
    """
    case_detail = case_repo.get_case_by_id(case_id)
    if not case_detail:
        return None

    # 构建8个维度的做法
    practices = {}
    for dim_key, dim_name in DIMENSION_NAMES.items():
        field_name = f"{dim_key}_practice"
        practices[dim_name] = case_detail.get(field_name, "")

    return {
        "id": case_detail.get("id"),
        "case_name": case_detail.get("case_name", ""),
        "village_id": case_detail.get("village_id"),
        "industry": case_detail.get("industry", ""),
        "province": case_detail.get("province", ""),
        "city": case_detail.get("city", ""),
        "county": case_detail.get("county", ""),
        "description": case_detail.get("description", ""),
        "practices": practices,  # 8个维度的做法详情
    }


def get_dimension_practices(case_id: int) -> Dict[str, str]:
    """
    获取案例的8个维度做法(单独接口,用于前端点击展开)
    """
    case_detail = case_repo.get_case_by_id(case_id)
    if not case_detail:
        return {dim_name: "" for dim_name in DIMENSION_NAMES.values()}

    practices = {}
    for dim_key, dim_name in DIMENSION_NAMES.items():
        field_name = f"{dim_key}_practice"
        practices[dim_name] = case_detail.get(field_name, "")
    
    return practices
