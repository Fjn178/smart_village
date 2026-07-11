from app import create_app
from database.models import db, Village

app = create_app()

with app.app_context():
    # 1. 确保表已经创建（如果还没建表，这句会自动建）
    db.create_all()

    # 2. 检查是否已经有数据了，避免重复插入
    if Village.query.count() > 0:
        print("ℹ️ 村庄数据已存在，跳过插入。")
    else:
        # 3. 插入你文档里的两个示范村
        v1 = Village(
            name='辛庄村',
            province='北京市',
            city='北京市',
            county='房山区',
            town='大石窝镇',
            population=1876,
            area=5973.0
        )
        v2 = Village(
            name='富各庄村',
            province='北京市',
            city='北京市',
            county='通州区',
            town='于家务回族乡',
            population=450,
            area=2100.0
        )

        db.session.add(v1)
        db.session.add(v2)
        db.session.commit()
        print("✅ 测试村庄数据创建成功！ (辛庄村、富各庄村)")