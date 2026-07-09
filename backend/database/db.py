from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ---------- 数据模型（对应计划书第6章） ----------
class Village(db.Model):
    __tablename__ = 'villages'
    village_id = db.Column(db.String(32), primary_key=True)  # 自定义ID或UUID
    village_name = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    county = db.Column(db.String(50))
    town = db.Column(db.String(50))
    survey_year = db.Column(db.Integer)
    data_source = db.Column(db.String(200))
    remarks = db.Column(db.Text)

class IndicatorDefinition(db.Model):
    __tablename__ = 'indicator_definitions'
    indicator_id = db.Column(db.Integer, primary_key=True)
    indicator_name = db.Column(db.String(100), nullable=False)
    category_l1 = db.Column(db.String(50))  # 一级分类：人口资源、土地资源...
    category_l2 = db.Column(db.String(50))  # 二级分类
    unit = db.Column(db.String(20))
    data_type = db.Column(db.String(20))    # 数值 / 文本

class VillageIndicator(db.Model):
    __tablename__ = 'village_indicators'
    id = db.Column(db.Integer, primary_key=True)
    village_id = db.Column(db.String(32), db.ForeignKey('villages.village_id'))
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicator_definitions.indicator_id'))
    indicator_value = db.Column(db.Float)   # 数值存浮点，文本存NULL或单独处理
    text_value = db.Column(db.String(200))  # 专门存文本型指标（如产业类型）
    update_time = db.Column(db.DateTime, default=datetime.now)

# 导入进度存储（内存表，服务重启即清空，生产可换Redis）
tasks_db = {}
