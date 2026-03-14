from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Spu, Category, Sku
from app.schemas.base.spu import SpuViewModel, SpuCreateViewModel, SpuUpdateViewModel
from app.schemas.base.sku import SkuCreateViewModel, SkuUpdateViewModel, SpuSkuCreateViewModel
from app.core.current_user import CurrentUser
from app.repositories.base.spu_repository import SpuRepository
from app.services.base_service import TenantAwareService


class SpuService(TenantAwareService[SpuRepository, Spu]):
    """
    SPU服务类
    
    提供SPU相关的业务逻辑处理，包括SPU查询、创建、更新、删除等操作
    """

    def __init__(self, db_session: AsyncSession):
        repository = SpuRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def page_search(
        self,
        page_index: int,
        page_size: int,
        search_params: Optional[dict] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[SpuViewModel], int]:
        """
        分页查询SPU列表
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            search_params: 搜索参数
            current_user: 当前登录用户
            
        Returns:
            SPU列表和总数量
        """
        query = select(Spu, Category).join(
            Category, Spu.category_id == Category.id
        ).where(Spu.tenant_id == current_user.tenant_id)
        
        if search_params:
            if "spu_code" in search_params:
                query = query.where(Spu.spu_code.like(f"%{search_params['spu_code']}%"))
            if "spu_name" in search_params:
                query = query.where(Spu.spu_name.like(f"%{search_params['spu_name']}%"))
            if "category_id" in search_params:
                query = query.where(Spu.category_id == search_params["category_id"])
            if "is_valid" in search_params:
                query = query.where(Spu.is_valid == search_params["is_valid"])
        
        from sqlalchemy import func
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        totals = total_result.scalar()
        
        query = query.order_by(Spu.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        rows = result.all()
        
        data = [
            SpuViewModel(
                id=spu.id,
                spu_code=spu.spu_code,
                spu_name=spu.spu_name,
                category_id=spu.category_id,
                spu_description=spu.spu_description,
                supplier_id=spu.supplier_id,
                supplier_name=spu.supplier_name,
                brand=spu.brand,
                origin=spu.origin,
                length_unit=spu.length_unit,
                volume_unit=spu.volume_unit,
                weight_unit=spu.weight_unit,
                creator=spu.creator,
                create_time=int(spu.create_time),
                last_update_time=int(spu.last_update_time),
                is_valid=spu.is_valid,
                tenant_id=spu.tenant_id
            )
            for spu, category in rows
        ]
        
        return data, totals

    async def get_all(self, current_user: CurrentUser) -> List[SpuViewModel]:
        """
        获取所有SPU
        
        Args:
            current_user: 当前登录用户
            
        Returns:
            SPU视图模型列表
        """
        spus = await self.get_by_tenant(current_user.tenant_id)
        
        return [
            SpuViewModel(
                id=spu.id,
                spu_code=spu.spu_code,
                spu_name=spu.spu_name,
                category_id=spu.category_id,
                spu_description=spu.spu_description,
                supplier_id=spu.supplier_id,
                supplier_name=spu.supplier_name,
                brand=spu.brand,
                origin=spu.origin,
                length_unit=spu.length_unit,
                volume_unit=spu.volume_unit,
                weight_unit=spu.weight_unit,
                creator=spu.creator,
                create_time=int(spu.create_time),
                last_update_time=int(spu.last_update_time),
                is_valid=spu.is_valid,
                tenant_id=spu.tenant_id
            )
            for spu in spus
        ]

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[SpuViewModel]:
        """
        根据ID获取SPU
        
        Args:
            id: SPU ID
            current_user: 当前登录用户
            
        Returns:
            SPU视图模型，不存在则返回None
        """
        spu = await self._repository.get_by_id(id)
        
        if spu is None:
            return None
        
        if current_user and spu.tenant_id != current_user.tenant_id:
            return None
        
        return SpuViewModel(
            id=spu.id,
            spu_code=spu.spu_code,
            spu_name=spu.spu_name,
            category_id=spu.category_id,
            spu_description=spu.spu_description,
            supplier_id=spu.supplier_id,
            supplier_name=spu.supplier_name,
            brand=spu.brand,
            origin=spu.origin,
            length_unit=spu.length_unit,
            volume_unit=spu.volume_unit,
            weight_unit=spu.weight_unit,
            creator=spu.creator,
            create_time=int(spu.create_time),
            last_update_time=int(spu.last_update_time),
            is_valid=spu.is_valid,
            tenant_id=spu.tenant_id
        )

    async def add(self, view_model: SpuCreateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        """
        创建SPU
        
        Args:
            view_model: SPU创建视图模型
            current_user: 当前登录用户
            
        Returns:
            (SPU ID, 消息)
        """
        existing = await self.get_one_by_tenant(
            current_user.tenant_id,
            filters={"spu_code": view_model.spu_code}
        )
        
        if existing:
            return 0, f"SPU编码 '{view_model.spu_code}' 已存在"
        
        supplier_name = ""
        if view_model.supplier_id and view_model.supplier_id > 0:
            from app.models.entities.base.supplier import Supplier
            query = select(Supplier).where(Supplier.id == view_model.supplier_id)
            result = await self._db_session.execute(query)
            supplier = result.scalar_one_or_none()
            if supplier:
                supplier_name = supplier.supplier_name
        
        spu = await self.create_with_tenant(
            current_user.tenant_id,
            spu_code=view_model.spu_code,
            spu_name=view_model.spu_name,
            category_id=view_model.category_id,
            spu_description=view_model.spu_description,
            supplier_id=view_model.supplier_id,
            supplier_name=supplier_name,
            brand=view_model.brand,
            origin=view_model.origin,
            length_unit=view_model.length_unit,
            volume_unit=view_model.volume_unit,
            weight_unit=view_model.weight_unit,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            is_valid=view_model.is_valid
        )
        
        if view_model.skus:
            for sku_data in view_model.skus:
                sku = Sku(
                    tenant_id=current_user.tenant_id,
                    spu_id=spu.id,
                    sku_code=sku_data.sku_code,
                    sku_name=sku_data.sku_name,
                    bar_code=sku_data.bar_code,
                    weight=sku_data.weight,
                    lenght=sku_data.lenght,
                    width=sku_data.width,
                    height=sku_data.height,
                    volume=sku_data.volume,
                    unit=sku_data.unit,
                    cost=sku_data.cost,
                    price=sku_data.price,
                    create_time=int(datetime.now().timestamp()),
                    last_update_time=int(datetime.now().timestamp())
                )
                self._db_session.add(sku)
            
            await self._db_session.commit()
        
        return spu.id, "保存成功"

    async def update(self, id: int, view_model: SpuUpdateViewModel, current_user: CurrentUser) -> Tuple[bool, str]:
        """
        更新SPU
        
        Args:
            id: SPU ID
            view_model: SPU更新视图模型
            current_user: 当前登录用户
            
        Returns:
            (是否成功, 消息)
        """
        spu = await self._repository.get_by_id(id)
        
        if spu is None:
            return False, "记录不存在"
        
        if view_model.spu_code is not None:
            existing = await self.get_one_by_tenant(
                spu.tenant_id,
                filters={"spu_code": view_model.spu_code}
            )
            
            if existing and existing.id != id:
                return False, f"SPU编码 '{view_model.spu_code}' 已存在"
        
        update_data = {}
        if view_model.spu_code is not None:
            update_data["spu_code"] = view_model.spu_code
        if view_model.spu_name is not None:
            update_data["spu_name"] = view_model.spu_name
        if view_model.category_id is not None:
            update_data["category_id"] = view_model.category_id
        if view_model.spu_description is not None:
            update_data["spu_description"] = view_model.spu_description
        if view_model.supplier_id is not None:
            update_data["supplier_id"] = view_model.supplier_id
            if view_model.supplier_id > 0:
                from app.models.entities.base.supplier import Supplier
                query = select(Supplier).where(Supplier.id == view_model.supplier_id)
                result = await self._db_session.execute(query)
                supplier = result.scalar_one_or_none()
                if supplier:
                    update_data["supplier_name"] = supplier.supplier_name
            else:
                update_data["supplier_name"] = ""
        if view_model.brand is not None:
            update_data["brand"] = view_model.brand
        if view_model.origin is not None:
            update_data["origin"] = view_model.origin
        if view_model.length_unit is not None:
            update_data["length_unit"] = view_model.length_unit
        if view_model.volume_unit is not None:
            update_data["volume_unit"] = view_model.volume_unit
        if view_model.weight_unit is not None:
            update_data["weight_unit"] = view_model.weight_unit
        if view_model.is_valid is not None:
            update_data["is_valid"] = view_model.is_valid
        
        if update_data:
            await self._repository.update(id, **update_data)
        
        if view_model.skus:
            for sku_data in view_model.skus:
                if sku_data.id:
                    sku = await self.get_one_entity_by_tenant(
                        Sku,
                        spu.tenant_id,
                        filters={"id": sku_data.id}
                    )
                    
                    if sku:
                        if sku_data.sku_code is not None:
                            sku.sku_code = sku_data.sku_code
                        if sku_data.sku_name is not None:
                            sku.sku_name = sku_data.sku_name
                        if sku_data.bar_code is not None:
                            sku.bar_code = sku_data.bar_code
                        if sku_data.weight is not None:
                            sku.weight = sku_data.weight
                        if sku_data.lenght is not None:
                            sku.lenght = sku_data.lenght
                        if sku_data.width is not None:
                            sku.width = sku_data.width
                        if sku_data.height is not None:
                            sku.height = sku_data.height
                        if sku_data.volume is not None:
                            sku.volume = sku_data.volume
                        if sku_data.unit is not None:
                            sku.unit = sku_data.unit
                        if sku_data.cost is not None:
                            sku.cost = sku_data.cost
                        if sku_data.price is not None:
                            sku.price = sku_data.price
                        
                        sku.last_update_time = int(datetime.now().timestamp())
                else:
                    sku = Sku(
                        tenant_id=current_user.tenant_id,
                        spu_id=spu.id,
                        sku_code=sku_data.sku_code,
                        sku_name=sku_data.sku_name,
                        bar_code=sku_data.bar_code,
                        weight=sku_data.weight,
                        lenght=sku_data.lenght,
                        width=sku_data.width,
                        height=sku_data.height,
                        volume=sku_data.volume,
                        unit=sku_data.unit,
                        cost=sku_data.cost,
                        price=sku_data.price,
                        create_time=int(datetime.now().timestamp()),
                        last_update_time=int(datetime.now().timestamp())
                    )
                    self._db_session.add(sku)
            
            await self._db_session.commit()
        
        if view_model.delete_sku_ids:
            for sku_id in view_model.delete_sku_ids:
                sku = await self.get_one_entity_by_tenant(
                    Sku,
                    spu.tenant_id,
                    filters={"id": sku_id}
                )
                
                if sku and sku.spu_id == spu.id:
                    await self._db_session.delete(sku)
            
            await self._db_session.commit()
        
        return True, "保存成功"

    async def delete(self, id: int, current_user: Optional[CurrentUser] = None) -> Tuple[bool, str]:
        """
        删除SPU
        
        Args:
            id: SPU ID
            current_user: 当前登录用户
            
        Returns:
            (是否成功, 消息)
        """
        spu = await self._repository.get_by_id(id)
        
        if spu is None:
            return False, "记录不存在"
        
        if current_user and spu.tenant_id != current_user.tenant_id:
            return False, "无权删除此记录"
        
        result = await self._repository.delete(id)
        
        if not result:
            return False, "记录不存在"
        
        return True, "删除成功"
