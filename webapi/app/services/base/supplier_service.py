from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.entities.base.supplier import Supplier
from app.schemas.base.supplier import SupplierCreate, SupplierUpdate, SupplierViewModel
from app.core.current_user import CurrentUser
from app.repositories.base.supplier_repository import SupplierRepository
from app.services.base_service import TenantAwareService


class SupplierService(TenantAwareService[SupplierRepository, Supplier]):
    def __init__(self, db_session: AsyncSession):
        repository = SupplierRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        supplier_name: Optional[str] = None,
        is_valid: Optional[bool] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[SupplierViewModel], int]:
        search_params = {}
        if supplier_name:
            search_params["supplier_name"] = supplier_name
        if is_valid is not None:
            search_params["is_valid"] = is_valid
        
        entities, totals = await self._repository.search_by_tenant(
            page_index, page_size, current_user.tenant_id, search_params
        )

        data = [
            SupplierViewModel(
                id=entity.id,
                supplier_name=entity.supplier_name,
                city=entity.city,
                address=entity.address,
                manager=entity.manager,
                email=entity.email,
                contact_tel=entity.contact_tel,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                is_valid=entity.is_valid,
                tenant_id=entity.tenant_id
            )
            for entity in entities
        ]

        return data, totals

    async def get_all(self, current_user: CurrentUser) -> List[SupplierViewModel]:
        entities = await self.get_by_tenant(current_user.tenant_id)

        return [
            SupplierViewModel(
                id=entity.id,
                supplier_name=entity.supplier_name,
                city=entity.city,
                address=entity.address,
                manager=entity.manager,
                email=entity.email,
                contact_tel=entity.contact_tel,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                is_valid=entity.is_valid,
                tenant_id=entity.tenant_id
            )
            for entity in entities
        ]

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[SupplierViewModel]:
        entity = await self._repository.get_by_id(id)

        if entity is None:
            return None
        
        if current_user and entity.tenant_id != current_user.tenant_id:
            return None

        return SupplierViewModel(
            id=entity.id,
            supplier_name=entity.supplier_name,
            city=entity.city,
            address=entity.address,
            manager=entity.manager,
            email=entity.email,
            contact_tel=entity.contact_tel,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            is_valid=entity.is_valid,
            tenant_id=entity.tenant_id
        )

    async def create(self, data: SupplierCreate, current_user: CurrentUser) -> Tuple[int, str]:
        existing = await self.get_one_by_tenant(
            current_user.tenant_id,
            filters={"supplier_name": data.supplier_name}
        )

        if existing:
            return 0, f"供应商名称 {data.supplier_name} 已存在"

        entity = await self.create_with_tenant(
            current_user.tenant_id,
            supplier_name=data.supplier_name,
            city=data.city,
            address=data.address,
            manager=data.manager,
            email=data.email,
            contact_tel=data.contact_tel,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            is_valid=True
        )

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: SupplierUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self._repository.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"
        
        if current_user and entity.tenant_id != current_user.tenant_id:
            return False, "无权修改此记录"

        existing = await self.get_one_by_tenant(
            current_user.tenant_id,
            filters={"supplier_name": data.supplier_name}
        )

        if existing and existing.id != data.id:
            return False, f"供应商名称 {data.supplier_name} 已存在"

        await self.update_with_tenant(
            data.id,
            current_user.tenant_id,
            supplier_name=data.supplier_name,
            city=data.city,
            address=data.address,
            manager=data.manager,
            email=data.email,
            contact_tel=data.contact_tel,
            last_update_time=int(datetime.now().timestamp())
        )

        return True, "保存成功"

    async def delete(self, id: int, current_user: Optional[CurrentUser] = None) -> Tuple[bool, str]:
        entity = await self._repository.get_by_id(id)

        if entity is None:
            return False, "记录不存在"
        
        if current_user and entity.tenant_id != current_user.tenant_id:
            return False, "无权删除此记录"

        result = await self._repository.delete(id)

        if not result:
            return False, "删除失败"

        return True, "删除成功"
