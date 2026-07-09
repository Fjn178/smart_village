import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    # SQLite 数据库路径
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "smart_village.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # 密钥（生产环境请替换）
    SECRET_KEY = 'dev-secret-key-123456'
