import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1小时过期
    SQLALCHEMY_DATABASE_URI = 'sqlite:///smart_village.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False