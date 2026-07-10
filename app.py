# app.py - 智联乡策完整后端入口
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
import os

# ============================================================
# 1. 应用初始化
# ============================================================
app = Flask(__name__)

# 跨域配置（允许前端访问）
CORS(app)

# ============================================================
# 2. 数据库配置（使用 SQLite，文件在项目根目录）
# ============================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_village.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ============================================================
# 3. 数据模型
# ============================================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='viewer')
    created_at = db.Column(db.DateTime, default=datetime.now)

class IndicatorDefinition(db.Model):
    __tablename__ = 'indicator_definitions'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    sub_category = db.Column(db.String(50))
    unit = db.Column(db.String(20))
    dimension = db.Column(db.String(50))
    weight = db.Column(db.Float, default=1.0)

class VillageIndicator(db.Model):
    __tablename__ = 'village_indicators'
    id = db.Column(db.Integer, primary_key=True)
    village_id = db.Column(db.Integer, nullable=False)
    indicator_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float)
    normalized_value = db.Column(db.Float)
    year = db.Column(db.Integer)
    data_source = db.Column(db.String(100))
    remarks = db.Column(db.Text)

class CaseLibrary(db.Model):
    __tablename__ = 'case_library'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    success_factors = db.Column(db.Text)

class CasePractice(db.Model):
    __tablename__ = 'case_practices'
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_library.id'), nullable=False)
    module = db.Column(db.String(50))
    sub_module = db.Column(db.String(50))
    practice = db.Column(db.Text)
    case = db.relationship('CaseLibrary', backref='practices')

class CaseIndicator(db.Model):
    __tablename__ = 'case_indicators'
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_library.id'), nullable=False)
    indicator_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float)
    normalized_value = db.Column(db.Float)
    remarks = db.Column(db.Text)

# ============================================================
# 4. 初始化函数
# ============================================================

def init_db():
    with app.app_context():
        db.create_all()
        print("✅ 所有数据库表创建成功！")

def create_admin():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("⚠️  admin 已存在")
        else:
            new_admin = User(
                username='admin',
                password_hash='admin123',
                role='admin',
                created_at=datetime.now()
            )
            db.session.add(new_admin)
            db.session.commit()
            print("✅ admin 创建成功！ (账号: admin, 密码: admin123)")

def import_indicators_from_excel():
    import pandas as pd
    excel_path = 'data/indicator_definitions.xlsx'
    if not os.path.exists(excel_path):
        print(f"⚠️  Excel 不存在: {excel_path}，跳过")
        return
    with app.app_context():
        xls = pd.ExcelFile(excel_path)
        count = 0
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            if 'indicator_id' not in df.columns:
                continue
            for _, row in df.iterrows():
                ind_id = row.get('indicator_id')
                if pd.isna(ind_id):
                    continue
                code = f"IND_{int(ind_id):03d}"
                if IndicatorDefinition.query.filter_by(code=code).first():
                    continue
                indicator = IndicatorDefinition(
                    code=code,
                    name=row.get('指标名称', ''),
                    category=row.get('一级分类', ''),
                    sub_category=row.get('二级分类', ''),
                    unit=row.get('单位', ''),
                    dimension='数值型' if row.get('数据类型') == '数值' else '文本型',
                    weight=1.0
                )
                db.session.add(indicator)
                count += 1
        db.session.commit()
        print(f"✅ 成功导入指标 {count} 条")

def init_all():
    print("🚀 开始初始化系统...")
    init_db()
    create_admin()
    import_indicators_from_excel()
    print("🎉 系统初始化完成！")

# ============================================================
# 5. API 路由
# ============================================================

@app.route('/')
def hello():
    return jsonify({"code": 0, "message": "智联乡策后端已启动"})

@app.route('/api/health')
def health():
    return jsonify({"code": 0, "data": {"status": "ok"}})

@app.route('/api/users')
def list_users():
    users = User.query.all()
    return jsonify({
        "code": 0,
        "data": [{"id": u.id, "username": u.username, "role": u.role} for u in users]
    })

# ============================================================
# 6. 启动
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)