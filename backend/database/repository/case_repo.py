# backend/database/repository/case_repo.py
from backend.database import db
from backend.database.models import CaseLibrary, CasePractice, CaseIndicator


def get_all_cases():
    """获取所有案例的基本信息 + 做法详情 + 指标向量"""
    cases = CaseLibrary.query.all()
    result = []
    
    for case in cases:
        # 获取该案例的所有做法
        practices = CasePractice.query.filter_by(case_id=case.id).all()
        practices_list = [
            {
                "module": p.module,
                "sub_module": p.sub_module,
                "practice": p.practice
            }
            for p in practices
        ]
        
        # 获取该案例的所有指标值
        indicators = CaseIndicator.query.filter_by(case_id=case.id).all()
        indicator_vector = {}
        for ind in indicators:
            val = ind.normalized_value if ind.normalized_value is not None else ind.value
            if val is not None:
                indicator_vector[ind.indicator_id] = val
        
        result.append({
            "id": case.id,
            "name": case.name,
            "location": case.location,
            "industry": case.industry,
            "success_factors": case.success_factors,
            "practices": practices_list,
            "indicator_vector": indicator_vector
        })
    
    return result


def get_case_by_id(case_id):
    """根据 ID 获取单个案例的完整信息"""
    case = CaseLibrary.query.get(case_id)
    if not case:
        return None
    
    practices = CasePractice.query.filter_by(case_id=case.id).all()
    indicators = CaseIndicator.query.filter_by(case_id=case.id).all()
    
    return {
        "id": case.id,
        "name": case.name,
        "location": case.location,
        "industry": case.industry,
        "success_factors": case.success_factors,
        "practices": [{"module": p.module, "sub_module": p.sub_module, "practice": p.practice} for p in practices],
        "indicator_vector": {ind.indicator_id: ind.value for ind in indicators}
    }