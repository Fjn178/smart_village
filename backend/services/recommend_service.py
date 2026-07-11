# backend/services/recommend_service.py
from backend.database.repository.case_repo import get_all_cases
from backend.algorithms.similarity_engine import calculate_cosine_similarity


def get_recommendations(target_village_id, target_vector):
    """
    推荐服务：根据目标村庄向量，返回 Top6 相似案例 + 共性做法
    相似度计算由 similarity_engine 模块负责
    """
    all_cases = get_all_cases()
    
    if not all_cases:
        return {
            "target_village_id": target_village_id,
            "recommendations": [],
            "common_practices": {},
            "message": "暂无案例数据"
        }

    # 计算每个案例的相似度（调用别人的模块）
    scored = []
    for case in all_cases:
        if not case.get("indicator_vector"):
            continue
        sim = calculate_cosine_similarity(target_vector, case["indicator_vector"])
        scored.append({
            "id": case["id"],
            "name": case["name"],
            "location": case["location"],
            "industry": case["industry"],
            "success_factors": case["success_factors"],
            "practices": case["practices"],
            "similarity_score": sim
        })

    # 按相似度降序排序，取 Top6
    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    top6 = scored[:6]

    # 提取 Top6 的共性做法（按板块聚合）
    common_practices = {}
    for case in top6:
        for p in case.get("practices", []):
            module = p.get("module", "其他")
            common_practices.setdefault(module, []).append(p.get("practice", ""))

    # 去重，每个板块最多保留5条
    for module in common_practices:
        common_practices[module] = list(set(common_practices[module]))[:5]

    return {
        "target_village_id": target_village_id,
        "recommendations": top6,
        "common_practices": common_practices,
        "message": f"成功推荐 {len(top6)} 个相似案例"
    }