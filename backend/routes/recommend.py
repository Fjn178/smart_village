"""
推荐路由 - 相似案例推荐 API
GET /api/recommend/<village_id> - 获取目标村庄的相似案例推荐
"""
from flask import Blueprint, request
from backend.utils.response import success, error
from backend.services.recommend_service import get_recommendations, get_recommendation_detail

recommend_bp = Blueprint('recommend', __name__)


@recommend_bp.route('/api/recommend/<int:village_id>', methods=['GET'])
def recommend_cases(village_id):
    """
    获取目标村庄的相似案例推荐

    Args:
        village_id: 目标村庄ID

    Query Parameters:
        top_n: 返回数量，默认6
        weight_type: 权重类型，"equal"或"category"，默认"category"

    Returns:
        JSON响应，包含推荐案例列表
    """
    try:
        top_n = request.args.get('top_n', 6, type=int)
        weight_type = request.args.get('weight_type', 'category', type=str)

        # 参数校验
        if top_n < 1 or top_n > 20:
            top_n = 6
        if weight_type not in ['equal', 'category']:
            weight_type = 'category'

        # 调用服务层获取推荐
        recommendations = get_recommendations(
            village_id=village_id,
            top_n=top_n,
            weight_type=weight_type
        )

        if not recommendations:
            return success(
                data=[],
                message=f"村庄ID {village_id} 暂无相似案例推荐"
            )

        return success(
            data={
                'village_id': village_id,
                'total': len(recommendations),
                'recommendations': recommendations
            },
            message="获取推荐成功"
        )

    except Exception as e:
        return error(message=f"获取推荐失败: {str(e)}")


@recommend_bp.route('/api/recommend/detail/<int:case_id>', methods=['GET'])
def recommend_detail(case_id):
    """
    获取单个案例的详细信息

    Args:
        case_id: 案例ID

    Returns:
        JSON响应，包含案例详细信息
    """
    try:
        detail = get_recommendation_detail(case_id)
        if not detail:
            return error(message=f"案例ID {case_id} 不存在")

        return success(data=detail, message="获取案例详情成功")

    except Exception as e:
        return error(message=f"获取案例详情失败: {str(e)}")
