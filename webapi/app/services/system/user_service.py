from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.system.user import User
from app.models.entities.system.user_role import UserRole
from app.schemas.system.user import UserCreateViewModel, UserUpdateViewModel, UserViewModel
from app.core.current_user import CurrentUser
from app.utils.md5_util import md5_encrypt_32
from app.repositories.system.user_repository import UserRepository
from app.services.base_service import TenantAwareService


class UserService(TenantAwareService[UserRepository, User]):
    """
    用户服务类
    
    提供用户相关的业务逻辑处理,包括用户查询、创建、更新、删除等操作
    """
    def __init__(self, db_session: AsyncSession):
        repository = UserRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        user_name: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[UserViewModel], int]:
        search_params = {}
        if user_name:
            search_params["user_name"] = user_name
        
        entities, totals = await self._repository.search_by_tenant(
            page_index, page_size, current_user.tenant_id, search_params
        )

        data = [
            UserViewModel(
                id=entity.id,
                user_num=entity.user_num,
                user_name=entity.user_name,
                user_role=entity.user_role,
                tenant_id=entity.tenant_id,
                is_valid=entity.is_valid,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                role_name=entity.user_role.role_name if entity.user_role else ''
            )
            for entity in entities
        ]

        return data, totals

    async def get_by_id(self, id: int) -> Optional[UserViewModel]:
        query = select(User).join(UserRole, User.user_role == UserRole.role_name)
        query = query.where(User.id == id)

        result = await self._db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return None

        return UserViewModel(
            id=entity.id,
            user_num=entity.user_num,
            user_name=entity.user_name,
            user_role=entity.user_role,
            tenant_id=entity.tenant_id,
            is_valid=entity.is_valid,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            role_name=entity.user_role.role_name if entity.user_role else ''
        )

    async def create(self, data: UserCreateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        md5_password = md5_encrypt_32(data.password)
        
        entity = await self.create_with_tenant(
            current_user.tenant_id,
            user_num=data.user_num,
            user_name=data.user_name,
            user_role=data.user_role,
            auth_string=md5_password,
            is_valid=True,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: UserUpdateViewModel) -> Tuple[bool, str]:
        entity = await self._repository.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        update_data = {
            "user_num": data.user_num,
            "user_name": data.user_name,
            "user_role": data.user_role,
            "is_valid": data.is_valid,
            "last_update_time": int(datetime.now().timestamp())
        }

        if data.password:
            update_data["auth_string"] = md5_encrypt_32(data.password)

        await self.update_with_tenant(data.id, entity.tenant_id, **update_data)

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        entity = await self._repository.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        result = await self._repository.delete(id)

        if not result:
            return False, "删除失败"

        return True, "删除成功"
