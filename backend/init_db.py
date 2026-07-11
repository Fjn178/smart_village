from app import create_app
from database.models import db, User

app = create_app()
with app.app_context():
    User.query.filter_by(username='admin').delete()
    admin = User(username='admin', role='admin')
    admin.set_password('123456')
    db.session.add(admin)
    db.session.commit()
    print("✅ 测试账号创建成功！用户名: admin , 密码: 123456")