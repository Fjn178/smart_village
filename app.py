# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from backend.database import db
from backend.routes.recommend import recommend_bp


def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_village.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False
    
    # 跨域
    CORS(app)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册路由
    app.register_blueprint(recommend_bp)
    
    # 健康检查
    @app.route('/')
    def index():
        return jsonify({"code": 0, "message": "智联乡策后端已启动"})
    
    @app.route('/api/health')
    def health():
        return jsonify({"code": 0, "data": {"status": "ok"}})
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)