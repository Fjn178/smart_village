from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='village')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    # ===== 在 models.py 末尾追加 Village 模型 =====

class Village(db.Model):
    __tablename__ = 'villages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    county = db.Column(db.String(50))
    town = db.Column(db.String(50))
    population = db.Column(db.Integer)
    area = db.Column(db.Float)  # 村域面积（亩）
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # 关联用户表（用于权限判断）
    # 注意：User 表中的 village_id 和 town_id 需要与这里的 id 对应