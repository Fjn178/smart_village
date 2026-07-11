# backend/routes/recommend.py
from flask import Blueprint, jsonify
from backend.services.recommend_service import get_recommendations

recommend_bp = Blueprint("recommend", __name__, url_prefix="/api/recommend")


@recommend_bp.route("/<int:village_id>")
def recommend(village_id):
    """
    推荐接口
    GET /api/recommend/{village_id}
    返回 Top6 相似案例 + 共性做法
    """
    # TODO: 后续从 VillageIndicator 表查询 target_vector
    # 目前使用占位数据（indicator_id: value）
    target_vector = {
        1: 0.8,
        2: 0.6,
        3: 0.7,
        4: 0.5,
        5: 0.9
    }
    
    result = get_recommendations(village_id, target_vector)
    return jsonify(result)