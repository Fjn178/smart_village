# backend/services/recommend_service.py
from backend.database.repository.case_repo import get_all_cases


def get_recommendations(village_id):
    """
    根据目标村庄ID，推荐相似的案例村庄
    """
    # 1. 获取所有案例
    all_cases = get_all_cases()
    
    if not all_cases:
        return {
            "target_village_id": village_id,
            "recommendations": [],
            "message": "暂无案例数据"
        }
    
    # 2. 暂时返回所有案例（后面再做相似度）
    recommendations = [
        {
            "case_id": case["id"],
            "name": case["name"],
            "location": case["location"],
            "industry": case["industry"],
            "success_factors": case["success_factors"],
            "similarity_score": 0.0
        }
        for case in all_cases
    ]
    
    return {
        "target_village_id": village_id,
        "recommendations": recommendations[:6],
        "message": "推荐完成"
    }
