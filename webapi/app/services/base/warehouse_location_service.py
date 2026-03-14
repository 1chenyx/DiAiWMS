from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import WarehouseLocation
from app.schemas.base.warehouse_location import (
    WarehouseLocationViewModel,
    WarehouseLocationCreateViewModel,
    WarehouseLocationUpdateViewModel,
    WarehouseLocationTreeNode
)
from app.core.current_user import CurrentUser
from app.repositories.base.warehouse_location_repository import WarehouseLocationRepository
from app.services.base_service import TenantAwareService


class WarehouseLocationService(TenantAwareService[WarehouseLocationRepository, WarehouseLocation]):
    """
    仓库位置服务类（统一的三级树形结构）
    
    提供仓库、库区、库位的统一业务逻辑处理
    node_type: 1-仓库, 2-库区, 3-库位
    """
    def __init__(self, db_session: AsyncSession):
        repository = WarehouseLocationRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def get_tree(self, current_user: CurrentUser) -> List[WarehouseLocationTreeNode]:
        """
        获取完整的仓库位置树形结构
        
        Args:
            current_user: 当前登录用户
            
        Returns:
            树形结构列表
        """
        all_locations = await self.query_by_tenant(
            current_user.tenant_id,
            filters={"is_valid": True},
            order_by=(WarehouseLocation.node_type, WarehouseLocation.create_time)
        )
        
        location_map = {}
        root_nodes = []
        
        for location in all_locations:
            node = WarehouseLocationTreeNode(
                id=location.id,
                node_type=location.node_type,
                node_name=location.node_name,
                parent_id=location.parent_id,
                children=[]
            )
            location_map[location.id] = node
            
            if location.parent_id == 0:
                root_nodes.append(node)
        
        for location in all_locations:
            if location.parent_id != 0 and location.parent_id in location_map:
                parent_node = location_map[location.parent_id]
                current_node = location_map[location.id]
                parent_node.children.append(current_node)
        
        return root_nodes

    async def get_tree_by_warehouse_id(self, warehouse_id: int, current_user: CurrentUser) -> Optional[WarehouseLocationTreeNode]:
        """
        根据仓库ID获取该仓库的库区、库位树形结构
        
        Args:
            warehouse_id: 仓库ID
            current_user: 当前登录用户
            
        Returns:
            树形结构节点
        """
        warehouse = await self.get_by_id(warehouse_id, current_user)
        
        if warehouse is None:
            return None
        
        if warehouse.node_type != 1:
            return None
        
        all_locations = await self.query_by_tenant(
            current_user.tenant_id,
            filters={"is_valid": True},
            order_by=(WarehouseLocation.node_type, WarehouseLocation.create_time)
        )
        
        location_map = {}
        root_node = None
        
        for location in all_locations:
            node = WarehouseLocationTreeNode(
                id=location.id,
                node_type=location.node_type,
                node_name=location.node_name,
                parent_id=location.parent_id,
                children=[]
            )
            location_map[location.id] = node
            
            if location.id == warehouse_id:
                root_node = node
        
        if root_node is None:
            return None
        
        for location in all_locations:
            if location.parent_id != 0 and location.parent_id in location_map:
                parent_node = location_map[location.parent_id]
                current_node = location_map[location.id]
                
                if parent_node.id == warehouse_id or self._is_descendant(warehouse_id, location.parent_id, location_map):
                    parent_node.children.append(current_node)
        
        return root_node

    def _is_descendant(self, warehouse_id: int, node_id: int, location_map: dict) -> bool:
        """
        检查节点是否是仓库的后代节点
        
        Args:
            warehouse_id: 仓库ID
            node_id: 节点ID
            location_map: 节点映射
            
        Returns:
            是否是后代节点
        """
        current_id = node_id
        while current_id != 0:
            if current_id == warehouse_id:
                return True
            node = location_map.get(current_id)
            if node is None:
                break
            current_id = node.parent_id
        return False

    async def get_children(self, parent_id: int, node_type: Optional[int] = None, current_user: Optional[CurrentUser] = None) -> List[WarehouseLocationViewModel]:
        """
        获取指定父节点的子节点
        
        Args:
            parent_id: 父节点ID
            node_type: 节点类型过滤 (可选)
            current_user: 当前登录用户
            
        Returns:
            子节点列表
        """
        filters = {"parent_id": parent_id}
        if node_type is not None:
            filters["node_type"] = node_type
        
        locations = await self.query_by_tenant(current_user.tenant_id, filters=filters)
        
        return [
            WarehouseLocationViewModel(
                id=location.id,
                node_type=location.node_type,
                parent_id=location.parent_id,
                node_name=location.node_name,
                city=location.city,
                address=location.address,
                email=location.email,
                manager=location.manager,
                contact_tel=location.contact_tel,
                area_property=location.area_property,
                location_length=float(location.location_length) if location.location_length else 0,
                location_width=float(location.location_width) if location.location_width else 0,
                location_height=float(location.location_height) if location.location_height else 0,
                location_volume=float(location.location_volume) if location.location_volume else 0,
                location_load=float(location.location_load) if location.location_load else 0,
                roadway_number=location.roadway_number,
                shelf_number=location.shelf_number,
                layer_number=location.layer_number,
                tag_number=location.tag_number,
                create_time=int(location.create_time),
                last_update_time=int(location.last_update_time),
                is_valid=location.is_valid,
                tenant_id=location.tenant_id,
                creator=location.creator
            )
            for location in locations
        ]

    async def get_select_items(self, node_type: int, parent_id: int, current_user: CurrentUser) -> List[dict]:
        """
        获取指定类型的有效节点列表，用于下拉选择
        
        Args:
            node_type: 节点类型
            parent_id: 父节点ID
            current_user: 当前登录用户
            
        Returns:
            节点字典列表
        """
        filters = {
            "node_type": node_type,
            "parent_id": parent_id,
            "is_valid": True
        }
        locations = await self.query_by_tenant(current_user.tenant_id, filters=filters)
        
        type_names = {1: "warehouse", 2: "warehousearea", 3: "goodslocation"}
        type_name = type_names.get(node_type, "location")
        
        return [
            {
                "code": type_name,
                "name": location.node_name,
                "value": str(location.id),
                "comments": f"{type_name} datas"
            }
            for location in locations
        ]

    async def page_search(
        self,
        page_index: int,
        page_size: int,
        search_params: Optional[dict] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[WarehouseLocationViewModel], int]:
        """
        分页查询仓库位置列表
        
        Args:
            page_index: 页码,从1开始
            page_size: 每页数量
            search_params: 搜索参数
            current_user: 当前登录用户
            
        Returns:
            仓库位置列表和总数量
        """
        filters = {}
        if search_params:
            if "node_name" in search_params:
                filters["node_name"] = f"%{search_params['node_name']}%"
            if "node_type" in search_params:
                filters["node_type"] = search_params["node_type"]
            if "parent_id" in search_params:
                filters["parent_id"] = search_params["parent_id"]
            if "is_valid" in search_params:
                filters["is_valid"] = search_params["is_valid"]
        
        locations, totals = await self.page_query_by_tenant(
            page_index=page_index,
            page_size=page_size,
            tenant_id=current_user.tenant_id,
            filters=filters,
            order_by=(WarehouseLocation.node_type, WarehouseLocation.create_time.desc())
        )
        
        data = [
            WarehouseLocationViewModel(
                id=location.id,
                node_type=location.node_type,
                parent_id=location.parent_id,
                node_name=location.node_name,
                city=location.city,
                address=location.address,
                email=location.email,
                manager=location.manager,
                contact_tel=location.contact_tel,
                area_property=location.area_property,
                location_length=float(location.location_length) if location.location_length else 0,
                location_width=float(location.location_width) if location.location_width else 0,
                location_height=float(location.location_height) if location.location_height else 0,
                location_volume=float(location.location_volume) if location.location_volume else 0,
                location_load=float(location.location_load) if location.location_load else 0,
                roadway_number=location.roadway_number,
                shelf_number=location.shelf_number,
                layer_number=location.layer_number,
                tag_number=location.tag_number,
                create_time=int(location.create_time),
                last_update_time=int(location.last_update_time),
                is_valid=location.is_valid,
                tenant_id=location.tenant_id,
                creator=location.creator
            )
            for location in locations
        ]
        
        return data, totals

    async def get_all(self, node_type: Optional[int] = None, parent_id: Optional[int] = None, current_user: Optional[CurrentUser] = None) -> List[WarehouseLocationViewModel]:
        """
        获取所有仓库位置列表
        
        Args:
            node_type: 节点类型过滤 (可选)
            parent_id: 父节点ID过滤 (可选)
            current_user: 当前登录用户
            
        Returns:
            仓库位置列表
        """
        filters = {}
        if node_type is not None:
            filters["node_type"] = node_type
        if parent_id is not None:
            filters["parent_id"] = parent_id
        
        locations = await self.query_by_tenant(current_user.tenant_id, filters=filters)
        
        return [
            WarehouseLocationViewModel(
                id=location.id,
                node_type=location.node_type,
                parent_id=location.parent_id,
                node_name=location.node_name,
                city=location.city,
                address=location.address,
                email=location.email,
                manager=location.manager,
                contact_tel=location.contact_tel,
                area_property=location.area_property,
                location_length=float(location.location_length) if location.location_length else 0,
                location_width=float(location.location_width) if location.location_width else 0,
                location_height=float(location.location_height) if location.location_height else 0,
                location_volume=float(location.location_volume) if location.location_volume else 0,
                location_load=float(location.location_load) if location.location_load else 0,
                roadway_number=location.roadway_number,
                shelf_number=location.shelf_number,
                layer_number=location.layer_number,
                tag_number=location.tag_number,
                create_time=int(location.create_time),
                last_update_time=int(location.last_update_time),
                is_valid=location.is_valid,
                tenant_id=location.tenant_id,
                creator=location.creator
            )
            for location in locations
        ]

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[WarehouseLocationViewModel]:
        """
        根据ID获取仓库位置信息
        
        Args:
            id: 仓库位置ID
            current_user: 当前登录用户
            
        Returns:
            仓库位置视图模型,不存在则返回None
        """
        query = select(WarehouseLocation).where(WarehouseLocation.id == id)
        result = await self._db_session.execute(query)
        location = result.scalar_one_or_none()
        
        if location is None:
            return None
        
        if current_user and location.tenant_id != current_user.tenant_id:
            return None
        
        return WarehouseLocationViewModel(
            id=location.id,
            node_type=location.node_type,
            parent_id=location.parent_id,
            node_name=location.node_name,
            city=location.city,
            address=location.address,
            email=location.email,
            manager=location.manager,
            contact_tel=location.contact_tel,
            area_property=location.area_property,
            location_length=float(location.location_length) if location.location_length else 0,
            location_width=float(location.location_width) if location.location_width else 0,
            location_height=float(location.location_height) if location.location_height else 0,
            location_volume=float(location.location_volume) if location.location_volume else 0,
            location_load=float(location.location_load) if location.location_load else 0,
            roadway_number=location.roadway_number,
            shelf_number=location.shelf_number,
            layer_number=location.layer_number,
            tag_number=location.tag_number,
            create_time=int(location.create_time),
            last_update_time=int(location.last_update_time),
            is_valid=location.is_valid,
            tenant_id=location.tenant_id,
            creator=location.creator
        )

    async def add(self, view_model: WarehouseLocationCreateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        """
        创建新仓库位置
        
        Args:
            view_model: 仓库位置创建数据
            current_user: 当前登录用户
            
        Returns:
            仓库位置ID和操作结果消息
        """
        if view_model.node_type > 1:
            parent = await self.get_one_by_tenant(
                current_user.tenant_id,
                filters={"id": view_model.parent_id}
            )
            
            if parent is None:
                return 0, "父节点不存在"
            
            if parent.node_type != view_model.node_type - 1:
                return 0, "父节点类型不正确"
        
        existing = await self.get_one_by_tenant(
            current_user.tenant_id,
            filters={
                "parent_id": view_model.parent_id,
                "node_name": view_model.node_name
            }
        )
        
        if existing:
            return 0, f"节点名称 '{view_model.node_name}' 已存在"
        
        location = await self.create_with_tenant(
            current_user.tenant_id,
            node_type=view_model.node_type,
            parent_id=view_model.parent_id,
            node_name=view_model.node_name,
            city=view_model.city or "",
            address=view_model.address or "",
            email=view_model.email or "",
            manager=view_model.manager or "",
            contact_tel=view_model.contact_tel or "",
            area_property=view_model.area_property or 0,
            location_length=view_model.location_length or 0,
            location_width=view_model.location_width or 0,
            location_height=view_model.location_height or 0,
            location_volume=view_model.location_volume or 0,
            location_load=view_model.location_load or 0,
            roadway_number=view_model.roadway_number or "",
            shelf_number=view_model.shelf_number or "",
            layer_number=view_model.layer_number or "",
            tag_number=view_model.tag_number or "",
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            is_valid=view_model.is_valid
        )
        
        return location.id, ""

    async def update(self, id: int, view_model: WarehouseLocationUpdateViewModel, current_user: CurrentUser) -> Tuple[bool, str]:
        """
        更新仓库位置信息
        
        Args:
            id: 仓库位置ID
            view_model: 仓库位置更新数据
            current_user: 当前登录用户
            
        Returns:
            操作结果和消息
        """
        location = await self.get_by_id(id)
        
        if location is None:
            return False, "记录不存在"
        
        if view_model.node_name is not None:
            existing = await self.get_one_by_tenant(
                current_user.tenant_id,
                filters={
                    "parent_id": location.parent_id,
                    "node_name": view_model.node_name
                }
            )
            
            if existing and existing.id != id:
                return False, f"节点名称 '{view_model.node_name}' 已存在"
        
        update_data = {}
        if view_model.node_name is not None:
            update_data["node_name"] = view_model.node_name
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
        if view_model.area_property is not None:
            update_data["area_property"] = view_model.area_property
        if view_model.location_length is not None:
            update_data["location_length"] = view_model.location_length
        if view_model.location_width is not None:
            update_data["location_width"] = view_model.location_width
        if view_model.location_height is not None:
            update_data["location_height"] = view_model.location_height
        if view_model.location_volume is not None:
            update_data["location_volume"] = view_model.location_volume
        if view_model.location_load is not None:
            update_data["location_load"] = view_model.location_load
        if view_model.roadway_number is not None:
            update_data["roadway_number"] = view_model.roadway_number
        if view_model.shelf_number is not None:
            update_data["shelf_number"] = view_model.shelf_number
        if view_model.layer_number is not None:
            update_data["layer_number"] = view_model.layer_number
        if view_model.tag_number is not None:
            update_data["tag_number"] = view_model.tag_number
        if view_model.is_valid is not None:
            update_data["is_valid"] = view_model.is_valid
        
        update_data["last_update_time"] = int(datetime.now().timestamp())
        
        await self.update_with_tenant(id, current_user.tenant_id, **update_data)
        
        return True, ""

    async def delete(self, id: int, current_user: Optional[CurrentUser] = None) -> Tuple[bool, str]:
        """
        删除仓库位置
        
        Args:
            id: 仓库位置ID
            current_user: 当前登录用户
            
        Returns:
            操作结果和消息
        """
        location = await self.get_by_id(id, current_user)
        
        if location is None:
            return False, "记录不存在"
        
        query = select(WarehouseLocation).where(WarehouseLocation.parent_id == id)
        result = await self._db_session.execute(query)
        children = result.scalars().all()
        
        if children:
            return False, "存在子节点，无法删除"
        
        query = select(WarehouseLocation).where(WarehouseLocation.id == id)
        result = await self._db_session.execute(query)
        location = result.scalar_one_or_none()
        
        if location is None:
            return False, "记录不存在"
        
        await self._db_session.delete(location)
        await self._db_session.commit()
        
        return True, ""
