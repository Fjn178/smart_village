from database.models import db
from database.models import Village  # 注意：这个 Village 模型我们还没创建，后面会补


class VillageRepository:
    """村庄数据访问层"""

    @staticmethod
    def get_all(filters=None):
        """
        获取所有村庄
        filters: 可选的过滤条件，如 {'town_id': 1, 'village_id': 2}
        """
        query = Village.query
        if filters:
            if filters.get('town_id'):
                query = query.filter(Village.town_id == filters['town_id'])
            if filters.get('village_id'):
                query = query.filter(Village.id == filters['village_id'])
        return query.all()

    @staticmethod
    def get_by_id(village_id):
        """根据ID获取单个村庄"""
        return Village.query.get(village_id)

    @staticmethod
    def create(data):
        """新增村庄"""
        village = Village(**data)
        db.session.add(village)
        db.session.commit()
        return village

    @staticmethod
    def update(village_id, data):
        """更新村庄"""
        village = Village.query.get(village_id)
        if not village:
            return None
        for key, value in data.items():
            setattr(village, key, value)
        db.session.commit()
        return village

    @staticmethod
    def delete(village_id):
        """删除村庄"""
        village = Village.query.get(village_id)
        if not village:
            return False
        db.session.delete(village)
        db.session.commit()
        return True