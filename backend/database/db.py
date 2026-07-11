# backend/database/db.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ---------- 用户表（权限控制） ----------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='village')  # admin, town, village
    town_id = db.Column(db.String(50))                  # 乡镇干部所属乡镇
    village_id = db.Column(db.String(32))               # 村支书所属村庄

# ---------- 村庄基本信息表 ----------
class Village(db.Model):
    __tablename__ = 'villages'
    village_id = db.Column(db.String(32), primary_key=True)
    village_name = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    county = db.Column(db.String(50))
    town = db.Column(db.String(50))
    survey_year = db.Column(db.Integer)                 # 数据年份（可选）
    data_source = db.Column(db.String(200))             # 数据来源（可选）
    remarks = db.Column(db.Text)                        # 备注（可选）

# ---------- 指标定义表（核心变动：增加 indicator_desc） ----------
class IndicatorDefinition(db.Model):
    __tablename__ = 'indicator_definitions'
    indicator_id = db.Column(db.Integer, primary_key=True)
    indicator_name = db.Column(db.String(100), nullable=False)
    category_l1 = db.Column(db.String(50))              # 一级分类（如：人口资源）
    category_l2 = db.Column(db.String(50))              # 二级分类（如：人口规模）
    indicator_desc = db.Column(db.Text)                 # 🆕 指标说明（对应模板中的“指标说明”列）
    unit = db.Column(db.String(20))                     # 单位
    data_type = db.Column(db.String(20), default='数值') # 数值 / 文本

# ---------- 村庄指标数据表（存储具体数值/文本） ----------
class VillageIndicator(db.Model):
    __tablename__ = 'village_indicators'
    id = db.Column(db.Integer, primary_key=True)
    village_id = db.Column(db.String(32), db.ForeignKey('villages.village_id'), nullable=False)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicator_definitions.indicator_id'), nullable=False)
    indicator_value = db.Column(db.Float)               # 数值型指标值
    text_value = db.Column(db.String(200))              # 文本型指标值
    update_time = db.Column(db.DateTime, default=datetime.now)

# ---------- 案例知识库表 ----------
class CaseLibrary(db.Model):
    __tablename__ = 'case_library'
    case_id = db.Column(db.String(32), primary_key=True)
    case_name = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    county = db.Column(db.String(50))
    village_name = db.Column(db.String(100))
    industry = db.Column(db.String(100))                # 主导产业
    industry_type = db.Column(db.String(50))            # 产业类别
    introduction = db.Column(db.Text)                   # 案例简介
    development_path = db.Column(db.Text)               # 发展历程
    business_model = db.Column(db.String(200))          # 运营模式
    success_experience = db.Column(db.Text)             # 成功经验
    government_support = db.Column(db.Text)             # 政策支持
    core_advantage = db.Column(db.Text)                 # 核心优势
    suitable_conditions = db.Column(db.Text)            # 适用条件
    unsuitable_conditions = db.Column(db.Text)          # 不适用条件
    investment_scale = db.Column(db.String(50))         # 投资规模
    annual_income = db.Column(db.String(50))            # 年收益
    risk_analysis = db.Column(db.Text)                  # 风险分析
    replication_level = db.Column(db.String(10))        # 可复制程度
    keywords = db.Column(db.String(200))                # 标签
    reference = db.Column(db.String(200))               # 数据来源

# ---------- 案例指标数据表（用于相似度计算） ----------
class CaseIndicator(db.Model):
    __tablename__ = 'case_indicators'
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(32), db.ForeignKey('case_library.case_id'), nullable=False)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicator_definitions.indicator_id'), nullable=False)
    indicator_value = db.Column(db.Float)               # 数值型
    text_value = db.Column(db.String(200))              # 文本型（一般不用）
    remarks = db.Column(db.Text)
