from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.village_service import VillageService
from database.models import User

village_bp = Blueprint('village', __name__)


@village_bp.route('', methods=['GET'])
@jwt_required()
def get_villages():
    """T11: 获取村庄列表"""
    identity = get_jwt_identity()
    # 从数据库查询完整用户信息（含权限字段）
    user = User.query.get(identity['id'])
    if not user:
        return jsonify({'code': 401, 'msg': '用户不存在'}), 401

    villages = VillageService.get_villages(user)

    # 序列化为 JSON
    result = []
    for v in villages:
        result.append({
            'id': v.id,
            'name': v.name,
            'town': v.town,
            'county': v.county,
            'province': v.province,
            'population': v.population,
            'area': v.area,
            'created_at': v.created_at.strftime('%Y-%m-%d %H:%M:%S') if v.created_at else None
        })

    return jsonify({
        'code': 0,
        'data': result
    })
@village_bp.route('', methods=['POST'])
@jwt_required()
def create_village():
    """T12: 新增村庄"""
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    if not user:
        return jsonify({'code': 401, 'msg': '用户不存在'}), 401

    # 权限校验：只有 admin 或 town 角色可以创建（村支书没有权限）
    if user.role not in ['admin', 'town']:
        return jsonify({'code': 403, 'msg': '无权限创建村庄'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'msg': '请求体不能为空'}), 400

    try:
        village = VillageService.create_village(data)
    except ValueError as e:
        return jsonify({'code': 400, 'msg': str(e)}), 400
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'创建失败: {str(e)}'}), 500

    # 返回创建成功的数据
    return jsonify({
        'code': 0,
        'msg': '创建成功',
        'data': {
            'id': village.id,
            'name': village.name,
            'province': village.province,
            'city': village.city,
            'county': village.county,
            'town': village.town,
            'population': village.population,
            'area': village.area
        }
    }), 201
@village_bp.route('/<int:village_id>', methods=['PUT'])
@jwt_required()
def update_village(village_id):
    """T13: 更新村庄信息"""
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    if not user:
        return jsonify({'code': 401, 'msg': '用户不存在'}), 401

    # 权限校验：只有 admin 或 town 可以更新
    if user.role not in ['admin', 'town']:
        return jsonify({'code': 403, 'msg': '无权限更新村庄'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'msg': '请求体不能为空'}), 400

    try:
        village = VillageService.update_village(village_id, data, user)
    except ValueError as e:
        return jsonify({'code': 404, 'msg': str(e)}), 404
    except PermissionError as e:
        return jsonify({'code': 403, 'msg': str(e)}), 403
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'更新失败: {str(e)}'}), 500

    # 返回更新后的数据
    return jsonify({
        'code': 0,
        'msg': '更新成功',
        'data': {
            'id': village.id,
            'name': village.name,
            'province': village.province,
            'city': village.city,
            'county': village.county,
            'town': village.town,
            'population': village.population,
            'area': village.area
        }
    })
@village_bp.route('/<int:village_id>', methods=['DELETE'])
@jwt_required()
def delete_village(village_id):
    """T14: 删除村庄"""
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    if not user:
        return jsonify({'code': 401, 'msg': '用户不存在'}), 401

    # 权限校验：只有 admin 或 town 可以删除
    if user.role not in ['admin', 'town']:
        return jsonify({'code': 403, 'msg': '无权限删除村庄'}), 403

    try:
        VillageService.delete_village(village_id, user)
    except ValueError as e:
        return jsonify({'code': 404, 'msg': str(e)}), 404
    except PermissionError as e:
        return jsonify({'code': 403, 'msg': str(e)}), 403
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'删除失败: {str(e)}'}), 500

    return jsonify({
        'code': 0,
        'msg': '删除成功'
    })