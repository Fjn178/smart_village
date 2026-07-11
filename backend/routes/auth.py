from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from utils.auth_utils import generate_token

auth_bp = Blueprint('auth', __name__)

# ========== T7: 登录 ==========
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'}), 400

    user = AuthService.authenticate(data['username'], data['password'])
    if not user:
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401

    token = generate_token(user.id, user.username, user.role)
    return jsonify({
        'code': 0,
        'msg': '登录成功',
        'data': {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'access_token': token
        }
    })

# ========== T8: 登出 ==========
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # 后端只验证 token 有效性，返回成功即可（前端清除本地 token）
    return jsonify({
        'code': 0,
        'msg': '登出成功'
    })

# ========== T9: 获取当前用户信息 ==========
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    # 从 token 中提取用户身份信息（即生成 token 时放入的 identity 字典）
    identity = get_jwt_identity()
    return jsonify({
        'code': 0,
        'data': identity
    })