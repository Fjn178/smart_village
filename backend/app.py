from flask import Flask
from flask_jwt_extended import JWTManager
from database.models import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)  # 初始化JWT

    # 注册蓝图
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # 自动建表
    app.run(debug=True, host='0.0.0.0', port=5000)