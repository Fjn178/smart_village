# backend/database/repository/case_repo.py
from app import db
from app import CaseLibrary, CaseIndicator


def get_all_cases():
    """获取所有案例的基本信息"""
    cases = CaseLibrary.query.all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "location": c.location,
            "industry": c.industry,
            "success_factors": c.success_factors
        }
        for c in cases
    ]


def get_case_indicators(case_id):
    """获取某个案例的所有指标值"""
    indicators = CaseIndicator.query.filter_by(case_id=case_id).all()
    return {
        "case_id": case_id,
        "indicators": [
            {
                "indicator_id": ind.indicator_id,
                "value": ind.value,
                "normalized_value": ind.normalized_value
            }
            for ind in indicators
        ]
    }


def get_all_case_vectors():
    """获取所有案例的指标向量（用于相似度计算）"""
    all_cases = CaseLibrary.query.all()
    result = {}
    for case in all_cases:
        indicators = CaseIndicator.query.filter_by(case_id=case.id).all()
        vec = {}
        for ind in indicators:
            val = ind.normalized_value if ind.normalized_value is not None else ind.value
            if val is not None:
                vec[ind.indicator_id] = val
        result[case.id] = {
            "name": case.name,
            "vector": vec
        }
    return result