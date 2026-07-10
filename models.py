from db import db
from datetime import datetime
# ============================================================
# 表1：用户表（T7-T10 登录认证用）
# ============================================================
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='viewer')   # admin / town / village
    town_id = db.Column(db.Integer, nullable=True)
    village_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'


# ============================================================
# 表2：村庄表（存储村庄基本信息 + PDF 里的 72 个指标字段）
# ============================================================
class Village(db.Model):
    __tablename__ = 'villages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # ----- 地理位置 -----
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    county = db.Column(db.String(50))
    town = db.Column(db.String(50))
    location = db.Column(db.String(200))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    
    # ----- 基础数据 -----
    population = db.Column(db.Integer)          # 户籍人口
    area = db.Column(db.Float)                  # 总面积
    
    # ----- 调研信息 -----
    survey_year = db.Column(db.Integer)
    data_source = db.Column(db.String(100))
    priority_problem = db.Column(db.Text)       # 当前主要发展问题
    expected_industry = db.Column(db.String(200))  # 希望发展的产业
    development_goal = db.Column(db.Text)       # 发展目标
    remarks = db.Column(db.Text)                # 调研备注
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Village {self.name}>'


# ============================================================
# 表3：指标定义表（PDF 第 16-20 页的 72 个指标）
# ============================================================
class IndicatorDefinition(db.Model):
    __tablename__ = 'indicator_definitions'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)   # IND_001
    name = db.Column(db.String(100), nullable=False)               # 户籍人口
    category = db.Column(db.String(50))                            # 一级分类：人口资源
    sub_category = db.Column(db.String(50))                        # 二级分类：人口规模
    unit = db.Column(db.String(20))                                # 人
    dimension = db.Column(db.String(50))                           # 所属维度
    weight = db.Column(db.Float, default=1.0)
    
    def __repr__(self):
        return f'<Indicator {self.code}: {self.name}>'


# ============================================================
# 表4：村庄指标值表（存储每个村庄在每个指标上的实际值）
# ============================================================
class VillageIndicator(db.Model):
    __tablename__ = 'village_indicators'
    
    id = db.Column(db.Integer, primary_key=True)
    village_id = db.Column(db.Integer, db.ForeignKey('villages.id'), nullable=False)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicator_definitions.id'), nullable=False)
    
    value = db.Column(db.Float)                 # 原始值
    normalized_value = db.Column(db.Float)      # 标准化后的值（0-1）
    score = db.Column(db.Float)                 # 评分（0-100）
    
    year = db.Column(db.Integer)
    data_source = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    
    def __repr__(self):
        return f'<VillageIndicator village={self.village_id} indicator={self.indicator_id}>'


# ============================================================
# 表5：案例库 - 基础信息表
# ============================================================
class CaseLibrary(db.Model):
    __tablename__ = 'case_library'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    
    # ----- 核心字段：主导产业（推荐依据） -----
    industry = db.Column(db.String(100))
    
    # ----- 成功因素摘要 -----
    success_factors = db.Column(db.Text)
    
    # ----- 关联做法详情（一对多） -----
    practices = db.relationship('CasePractice', backref='case', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CaseLibrary {self.name}>'


# ============================================================
# 表6：案例做法详情表（六个板块 + 细分小点，每个小点一行）
# ============================================================
class CasePractice(db.Model):
    __tablename__ = 'case_practices'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_library.id'), nullable=False)
    
    # ----- 分类字段 -----
    module = db.Column(db.String(50), nullable=False)       # 大板块
    
    # ----- 具体做法描述 -----
    practice = db.Column(db.Text, nullable=False)
    
    # ----- 额外信息（可选） -----
    source = db.Column(db.String(100))          # 来源：如"山口庄村案例"
    year = db.Column(db.Integer)                # 做法实施年份
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CasePractice {self.module} > {self.sub_module}>'


# ============================================================
# 表7：案例指标表（案例的指标向量，用于相似度计算）
# ============================================================
class CaseIndicator(db.Model):
    __tablename__ = 'case_indicators'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_library.id'), nullable=False)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicator_definitions.id'), nullable=False)
    
    value = db.Column(db.Float)
    normalized_value = db.Column(db.Float)
    score = db.Column(db.Float)
    
    remarks = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CaseIndicator case={self.case_id} indicator={self.indicator_id}>'


# ============================================================
# 表8：诊断报告表
# ============================================================
class DiagnosisReport(db.Model):
    __tablename__ = 'diagnosis_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    village_id = db.Column(db.Integer, db.ForeignKey('villages.id'), nullable=False)
    
    report_date = db.Column(db.DateTime, default=datetime.utcnow)
    scores_json = db.Column(db.Text)            # 五维评分 JSON
    overall_score = db.Column(db.Float)         # 综合得分
    swot_analysis = db.Column(db.Text)          # SWOT 分析
    suggestions = db.Column(db.Text)            # 改进建议
    pdf_path = db.Column(db.String(200))        # PDF 文件路径
    
    def __repr__(self):
        return f'<DiagnosisReport village={self.village_id} date={self.report_date}>'


# ============================================================
# 表9：推荐反馈表
# ============================================================
class RecommendFeedback(db.Model):
    __tablename__ = 'recommend_feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('diagnosis_reports.id'), nullable=False)
    
    recommendation = db.Column(db.Text)         # 推荐内容
    industry_name = db.Column(db.String(100))   # 被推荐的产业名称
    is_useful = db.Column(db.Boolean, default=True)  # 用户是否认为有用
    feedback_text = db.Column(db.Text)          # 用户反馈文字
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RecommendFeedback report={self.report_id} useful={self.is_useful}>'


# ============================================================
# 表10：上传任务追踪表（解决内存存储重启丢失的问题）
# ============================================================
class UploadTask(db.Model):
    __tablename__ = 'upload_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), unique=True, nullable=False)  # UUID
    status = db.Column(db.String(20), default='pending')  # pending / processing / done / fail / cancelled
    total = db.Column(db.Integer, default=0)
    current = db.Column(db.Integer, default=0)
    error = db.Column(db.Text)
    filename = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UploadTask {self.task_id} status={self.status}>'