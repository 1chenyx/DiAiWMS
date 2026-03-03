from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Warehouse
from app.schemas.warehouse import WarehouseViewModel, WarehouseCreateViewModel, WarehouseUpdateViewModel
from app.core.current_user import CurrentUser
from app.repositories.warehouse_repository import WarehouseRepository
from app.services.base_service import TenantAwareService


class WarehouseService(TenantAwareService[WarehouseRepository, Warehouse]):
    """
    仓库服务类
    
    提供仓库相关的业务逻辑处理，包括仓库查询、创建、更新、删除等操作
    """

    def __init__(self, db_session: AsyncSession):
        repository = WarehouseRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def get_select_items(self, current_user: CurrentUser) -> List[dict]:
        """
        获取有效的仓库列表，用于下拉选择
        
        Args:
            current_user: 当前登录用户
            
        Returns:
            仓库字典列表
        """
        warehouses = await self._repository.get_by_tenant(current_user.tenant_id, is_valid=True)
        
        return [
            {
                "code": "warehouse_name",
                "name": warehouse.warehouse_name,
                "value": str(warehouse.id),
                "comments": "warehouse datas"
            }
            for warehouse in warehouses
        ]

    async def page_search(
        self,
        page_index: int,
        page_size: int,
        search_params: Optional[dict] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[WarehouseViewModel], int]:
        """
        分页查询仓库列表
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            search_params: 搜索参数
            current_user: 当前登录用户
            
        Returns:
            仓库列表和总数量
        """
        warehouses, totals = await self._repository.page_search_by_tenant(
            page_index, page_size, current_user.tenant_id, search_params
        )
        
        data = [
            WarehouseViewModel(
                id=warehouse.id,
                warehouse_name=warehouse.warehouse_name,
                city=warehouse.city,
                address=warehouse.address,
                email=warehouse.email,
                manager=warehouse.manager,
                contact_tel=warehouse.contact_tel,
                creator=warehouse.creator,
                create_time=int(warehouse.create_time),
                last_update_time=int(warehouse.last_update_time),
                is_valid=warehouse.is_valid,
                tenant_id=warehouse.tenant_id
            )
            for warehouse in warehouses
        ]
        
        return data, totals

    async def get_all(self, current_user: CurrentUser) -> List[WarehouseViewModel]:
        """
        获取所有仓库列表
        
        Args:
            current_user: 当前登录用户
            
        Returns:
            仓库列表
        """
        warehouses = await self._repository.get_by_tenant(current_user.tenant_id)
        
        return [
            WarehouseViewModel(
                id=warehouse.id,
                warehouse_name=warehouse.warehouse_name,
                city=warehouse.city,
                address=warehouse.address,
                email=warehouse.email,
                manager=warehouse.manager,
                contact_tel=warehouse.contact_tel,
                creator=warehouse.creator,
                create_time=int(warehouse.create_time),
                last_update_time=int(warehouse.last_update_time),
                is_valid=warehouse.is_valid,
                tenant_id=warehouse.tenant_id
            )
            for warehouse in warehouses
        ]

    async def get_by_id(self, id: int) -> Optional[WarehouseViewModel]:
        """
        根据ID获取仓库信息
        
        Args:
            id: 仓库ID
            
        Returns:
            仓库视图模型，不存在则返回None
        """
        warehouse = await self._repository.get_by_id(id)
        
        if warehouse is None:
            return None
        
        return WarehouseViewModel(
            id=warehouse.id,
            warehouse_name=warehouse.warehouse_name,
            city=warehouse.city,
            address=warehouse.address,
            email=warehouse.email,
            manager=warehouse.manager,
            contact_tel=warehouse.contact_tel,
            creator=warehouse.creator,
            create_time=int(warehouse.create_time),
            last_update_time=int(warehouse.last_update_time),
            is_valid=warehouse.is_valid,
            tenant_id=warehouse.tenant_id
        )

    async def add(self, view_model: WarehouseCreateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        """
        创建新仓库
        
        Args:
            view_model: 仓库创建数据
            current_user: 当前登录用户
            
        Returns:
            仓库ID和操作结果消息
        """
        existing = await self._repository.exists_by_fields({
            "warehouse_name": view_model.warehouse_name,
            "tenant_id": current_user.tenant_id
        })
        
        if existing:
            return 0, f"仓库名称 '{view_model.warehouse_name}' 已存在"
        
        warehouse = await self._repository.create(
            warehouse_name=view_model.warehouse_name,
            city=view_model.city,
            address=view_model.address,
            email=view_model.email,
            manager=view_model.manager,
            contact_tel=view_model.contact_tel,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            is_valid=view_model.is_valid,
            tenant_id=current_user.tenant_id
        )
        
        return warehouse.id, ""

    async def update(self, id: int, view_model: WarehouseUpdateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        """
        更新仓库信息
        
        Args:
            id: 仓库ID
            view_model: 仓库更新数据
            current_user: 当前登录用户
            
        Returns:
            仓库ID和操作结果消息
        """
        warehouse = await self._repository.get_by_id(id)
        
        if warehouse is None:
            return 0, "仓库不存在"
        
        if view_model.warehouse_name is not None and view_model.warehouse_name != warehouse.warehouse_name:
            existing = await self._repository.exists_by_fields({
                "warehouse_name": view_model.warehouse_name,
                "tenant_id": warehouse.tenant_id
            })
            
            if existing:
                return 0, f"仓库名称 '{view_model.warehouse_name}' 已存在"
        
        update_data = {}
        if view_model.warehouse_name is not None:
            update_data["warehouse_name"] = view_model.warehouse_name
        if view_model.city is not None:
            update_data["city"] = view_model.city
        if view_model.address is not None:
            update_data["address"] = view_model.address
        if view_model.email is not None:
            update_data["email"] = view_model.email
        if view_model.manager is not None:
            update_data["manager"] = view_model.manager
        if view_model.contact_tel is not None:
            update_data["contact_tel"] = view_model.contact_tel
        if view_model.is_valid is not None:
            update_data["is_valid"] = view_model.is_valid
        
        if update_data:
            await self._repository.update(id, **update_data)
        
        return id, ""

    async def delete(self, id: int) -> Tuple[int, str]:
        """
        删除仓库
        
        Args:
            id: 仓库ID
            
        Returns:
            仓库ID和操作结果消息
        """
        result = await self._repository.delete(id)
        
        if not result:
            return 0, "仓库不存在"
        
        return id, ""
