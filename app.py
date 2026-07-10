from flask import Flask
from config import Config
from db import db, migrate
from models import *   # 导入所有模型

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)     #新增：连接数据库
migrate.init_app(app, db)  # 

@app.route('/')
def hello():
    return "Smart Village API is running!"  # 改为纯文本，方便测试

# 🔥 新增：自动创建所有数据表
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")
    app.run(debug=True, host='0.0.0.0', port=5000)