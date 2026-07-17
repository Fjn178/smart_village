from flask import Blueprint, jsonify, request
from services.case_service import get_top5_case_matches

cases_bp = Blueprint('cases', __name__, url_prefix='/api/cases')


@cases_bp.route('/match/<village_id>', methods=['GET'])
def match_cases(village_id):
    try:
        result = get_top5_case_matches(village_id=village_id, top_n=5)
    except ValueError as exc:
        return jsonify({"code": 400, "msg": str(exc)}), 400
    except Exception as exc:
        return jsonify({"code": 500, "msg": "案例匹配服务异常，请稍后重试。", "detail": str(exc)}), 500

    return jsonify({"code": 200, "data": result})
