from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import WarehouseLocation
from app.schemas.warehouse_location import (
    WarehouseLocationViewModel,
    WarehouseLocationCreateViewModel,
    WarehouseLocationUpdateViewModel,
    WarehouseLocationTreeNode
)
from app.core.current_user import CurrentUser


class WarehouseLocationService:
    """
    仓库位置服务类（统一的三级树形结构）
    
    提供仓库、库区、库位的统一业务逻辑处理
    node_type: 1-仓库, 2-库区, 3-库位
    """
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_tree(self, current_user: CurrentUser) -> List[WarehouseLocationTreeNode]:
        """
        获取完整的仓库位置树形结构
        
        Args:
            current_user: 当前登录用户
            
        Returns:
            树形结构列表
        """
        query = select(WarehouseLocation).where(
            WarehouseLocation.tenant_id == current_user.tenant_id,
            WarehouseLocation.is_valid == True
        ).order_by(WarehouseLocation.node_type, WarehouseLocation.create_time)
        
        result = await self.db_session.execute(query)
        all_locations = result.scalars().all()
        
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
        query = select(WarehouseLocation).where(
            WarehouseLocation.parent_id == parent_id,
            WarehouseLocation.tenant_id == current_user.tenant_id
        )
        
        if node_type is not None:
            query = query.where(WarehouseLocation.node_type == node_type)
        
        result = await self.db_session.execute(query)
        locations = result.scalars().all()
        
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
        query = select(WarehouseLocation).where(
            WarehouseLocation.node_type == node_type,
            WarehouseLocation.parent_id == parent_id,
            WarehouseLocation.is_valid == True,
            WarehouseLocation.tenant_id == current_user.tenant_id
        )
        result = await self.db_session.execute(query)
        locations = result.scalars().all()
        
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
        query = select(WarehouseLocation).where(WarehouseLocation.tenant_id == current_user.tenant_id)
        
        if search_params:
            if "node_name" in search_params:
                query = query.where(WarehouseLocation.node_name.like(f"%{search_params['node_name']}%"))
            if "node_type" in search_params:
                query = query.where(WarehouseLocation.node_type == search_params["node_type"])
            if "parent_id" in search_params:
                query = query.where(WarehouseLocation.parent_id == search_params["parent_id"])
            if "is_valid" in search_params:
                query = query.where(WarehouseLocation.is_valid == search_params["is_valid"])
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db_session.execute(total_query)
        totals = total_result.scalar()
        
        query = query.order_by(WarehouseLocation.node_type, WarehouseLocation.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self.db_session.execute(query)
        locations = result.scalars().all()
        
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
        query = select(WarehouseLocation).where(WarehouseLocation.tenant_id == current_user.tenant_id)
        
        if node_type is not None:
            query = query.where(WarehouseLocation.node_type == node_type)
        if parent_id is not None:
            query = query.where(WarehouseLocation.parent_id == parent_id)
        
        result = await self.db_session.execute(query)
        locations = result.scalars().all()
        
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

    async def get_by_id(self, id: int) -> Optional[WarehouseLocationViewModel]:
        """
        根据ID获取仓库位置信息
        
        Args:
            id: 仓库位置ID
            
        Returns:
            仓库位置视图模型,不存在则返回None
        """
        query = select(WarehouseLocation).where(WarehouseLocation.id == id)
        result = await self.db_session.execute(query)
        location = result.scalar_one_or_none()
        
        if location is None:
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
            query = select(WarehouseLocation).where(
                WarehouseLocation.id == view_model.parent_id,
                WarehouseLocation.tenant_id == current_user.tenant_id
            )
            result = await self.db_session.execute(query)
            parent = result.scalar_one_or_none()
            
            if parent is None:
                return 0, "父节点不存在"
            
            if parent.node_type != view_model.node_type - 1:
                return 0, "父节点类型不正确"
        
        query = select(WarehouseLocation).where(
            WarehouseLocation.parent_id == view_model.parent_id,
            WarehouseLocation.node_name == view_model.node_name,
            WarehouseLocation.tenant_id == current_user.tenant_id
        )
        result = await self.db_session.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return 0, f"节点名称 '{view_model.node_name}' 已存在"
        
        location = WarehouseLocation(
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
            is_valid=view_model.is_valid,
            tenant_id=current_user.tenant_id
        )
        
        self.db_session.add(location)
        await self.db_session.commit()
        await self.db_session.refresh(location)
        
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
        query = select(WarehouseLocation).where(WarehouseLocation.id == id)
        result = await self.db_session.execute(query)
        location = result.scalar_one_or_none()
        
        if location is None:
            return False, "记录不存在"
        
        if view_model.node_name is not None:
            query = select(WarehouseLocation).where(
                WarehouseLocation.id != id,
                WarehouseLocation.parent_id == location.parent_id,
                WarehouseLocation.node_name == view_model.node_name,
                WarehouseLocation.tenant_id == current_user.tenant_id
            )
            result = await self.db_session.execute(query)
            existing = result.scalar_one_or_none()
            
            if existing:
                return False, f"节点名称 '{view_model.node_name}' 已存在"
        
        if view_model.node_name is not None:
            location.node_name = view_model.node_name
        if view_model.city is not None:
            location.city = view_model.city
        if view_model.address is not None:
            location.address = view_model.address
        if view_model.email is not None:
            location.email = view_model.email
        if view_model.manager is not None:
            location.manager = view_model.manager
        if view_model.contact_tel is not None:
            location.contact_tel = view_model.contact_tel
        if view_model.area_property is not None:
            location.area_property = view_model.area_property
        if view_model.location_length is not None:
            location.location_length = view_model.location_length
        if view_model.location_width is not None:
            location.location_width = view_model.location_width
        if view_model.location_height is not None:
            location.location_height = view_model.location_height
        if view_model.location_volume is not None:
            location.location_volume = view_model.location_volume
        if view_model.location_load is not None:
            location.location_load = view_model.location_load
        if view_model.roadway_number is not None:
            location.roadway_number = view_model.roadway_number
        if view_model.shelf_number is not None:
            location.shelf_number = view_model.shelf_number
        if view_model.layer_number is not None:
            location.layer_number = view_model.layer_number
        if view_model.tag_number is not None:
            location.tag_number = view_model.tag_number
        if view_model.is_valid is not None:
            location.is_valid = view_model.is_valid
        
        location.last_update_time = int(datetime.now().timestamp())
        
        await self.db_session.commit()
        
        return True, ""

    async def delete(self, id: int) -> Tuple[bool, str]:
        """
        删除仓库位置
        
        Args:
            id: 仓库位置ID
            
        Returns:
            操作结果和消息
        """
        query = select(WarehouseLocation).where(WarehouseLocation.parent_id == id)
        result = await self.db_session.execute(query)
        children = result.scalars().all()
        
        if children:
            return False, "存在子节点，无法删除"
        
        query = select(WarehouseLocation).where(WarehouseLocation.id == id)
        result = await self.db_session.execute(query)
        location = result.scalar_one_or_none()
        
        if location is None:
            return False, "记录不存在"
        
        await self.db_session.delete(location)
        await self.db_session.commit()
        
        return True, ""
