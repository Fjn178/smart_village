from database.repository.village_repo import VillageRepository


class VillageService:
    """村庄业务逻辑层"""

    @staticmethod
    def get_villages(user):
        """
        根据用户角色获取村庄列表
        - admin: 查看全部
        - town: 查看本镇所有村庄
        - village: 只看本村
        """
        filters = {}
        if user.role == 'town':
            filters['town_id'] = user.town_id
        elif user.role == 'village':
            filters['village_id'] = user.village_id
        # admin 不加过滤条件
        return VillageRepository.get_all(filters)

    @staticmethod
    def get_village_by_id(village_id, user):
        """获取单个村庄，并校验权限"""
        village = VillageRepository.get_by_id(village_id)
        if not village:
            return None
        # 权限校验
        if user.role == 'town' and village.town_id != user.town_id:
            return None
        if user.role == 'village' and village.id != user.village_id:
            return None
        return village
    @staticmethod
    def create_village(data):
        """
        创建新村庄
        data: 前端传入的 JSON 数据字典
        """
        # 简单的必填校验
        if not data.get('name'):
            raise ValueError("村庄名称不能为空")

        # 调用 Repository 层写入数据库
        return VillageRepository.create(data)
    @staticmethod
    def update_village(village_id, data, user):
        """
        更新村庄信息
        village_id: 要更新的村庄ID
        data: 前端传入的更新数据字典
        user: 当前登录用户
        """
        # 先查询村庄是否存在
        village = VillageRepository.get_by_id(village_id)
        if not village:
            raise ValueError("村庄不存在")

        # 权限校验：town 只能更新自己镇内的村庄
        if user.role == 'town' and village.town_id != user.town_id:
            raise PermissionError("无权限更新此村庄")

        # 如果前端传了 name，不能为空
        if data.get('name') is not None and not data.get('name'):
            raise ValueError("村庄名称不能为空")

        # 调用 Repository 更新
        return VillageRepository.update(village_id, data)
    @staticmethod
    def delete_village(village_id, user):
        """
        删除村庄
        village_id: 要删除的村庄ID
        user: 当前登录用户
        """
        # 先查询村庄是否存在
        village = VillageRepository.get_by_id(village_id)
        if not village:
            raise ValueError("村庄不存在")

        # 权限校验：town 只能删除自己镇内的村庄
        if user.role == 'town' and village.town_id != user.town_id:
            raise PermissionError("无权限删除此村庄")

        # 调用 Repository 删除
        success = VillageRepository.delete(village_id)
        if not success:
            raise ValueError("删除失败")
        return True
