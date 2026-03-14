from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import Stock
from app.schemas.inventory.stock import StockViewModel, StockCreateViewModel, StockUpdateViewModel
from app.core.current_user import CurrentUser
from app.repositories.inventory.stock_repository import StockRepository
from app.services.base_service import TenantAwareService


class StockService(TenantAwareService[StockRepository, Stock]):
    """
    库存服务类
    
    提供库存相关的业务逻辑处理,包括库存查询、创建、更新、删除等操作
    """
    def __init__(self, db_session: AsyncSession):
        repository = StockRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def page_search(
        self,
        page_index: int,
        page_size: int,
        search_params: Optional[dict] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[StockViewModel], int]:
        """
        分页查询库存列表
        
        Args:
            page_index: 页码,从1开始
            page_size: 每页数量
            search_params: 搜索参数
            current_user: 当前登录用户
            
        Returns:
            库存列表和总数量
        """
        query = select(Stock).where(Stock.tenant_id == current_user.tenant_id)
        
        if search_params:
            if "sku_id" in search_params:
                query = query.where(Stock.sku_id == search_params["sku_id"])
            if "goods_location_id" in search_params:
                query = query.where(Stock.goods_location_id == search_params["goods_location_id"])
            if "is_freeze" in search_params:
                query = query.where(Stock.is_freeze == search_params["is_freeze"])
            if "goods_owner_id" in search_params:
                query = query.where(Stock.goods_owner_id == search_params["goods_owner_id"])
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        totals = total_result.scalar()
        
        query = query.order_by(Stock.last_update_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        rows = result.scalars().all()
        
        data = [
            StockViewModel(
                id=stock.id,
                sku_id=stock.sku_id,
                goods_location_id=stock.goods_location_id,
                qty=stock.qty,
                goods_owner_id=stock.goods_owner_id,
                is_freeze=stock.is_freeze,
                last_update_time=int(stock.last_update_time),
                tenant_id=stock.tenant_id,
                series_number=stock.series_number,
                expiry_date=int(stock.expiry_date),
                price=float(stock.price),
                putaway_date=int(stock.putaway_date),
                warehouse_id=stock.warehouse_id,
                warehouse_name=stock.warehouse_name,
                warehouse_area_id=stock.warehouse_area_id,
                warehouse_area_name=stock.warehouse_area_name,
                warehouse_location_name=stock.warehouse_location_name,
                spu_name=stock.spu_name,
                sku_code=stock.sku_code,
                sku_name=stock.sku_name,
                batch_no=stock.batch_no,
                production_date=int(stock.production_date)
            )
            for stock in rows
        ]
        
        return data, totals

    async def get_all(self, current_user: CurrentUser) -> List[StockViewModel]:
        """
        获取所有库存列表
        
        Args:
            current_user: 当前登录用户
            
        Returns:
            库存列表
        """
        stocks = await self.get_by_tenant(current_user.tenant_id)
        
        return [
            StockViewModel(
                id=stock.id,
                sku_id=stock.sku_id,
                goods_location_id=stock.goods_location_id,
                qty=stock.qty,
                goods_owner_id=stock.goods_owner_id,
                is_freeze=stock.is_freeze,
                last_update_time=int(stock.last_update_time),
                tenant_id=stock.tenant_id,
                series_number=stock.series_number,
                expiry_date=int(stock.expiry_date),
                price=float(stock.price),
                putaway_date=int(stock.putaway_date),
                warehouse_id=stock.warehouse_id,
                warehouse_name=stock.warehouse_name,
                warehouse_area_id=stock.warehouse_area_id,
                warehouse_area_name=stock.warehouse_area_name,
                warehouse_location_name=stock.warehouse_location_name,
                spu_name=stock.spu_name,
                sku_code=stock.sku_code,
                sku_name=stock.sku_name,
                batch_no=stock.batch_no,
                production_date=int(stock.production_date)
            )
            for stock in stocks
        ]

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[StockViewModel]:
        """
        根据ID获取库存信息
        
        Args:
            id: 库存ID
            current_user: 当前登录用户
            
        Returns:
            库存视图模型,不存在则返回None
        """
        stock = await self._repository.get_by_id(id)
        
        if stock is None:
            return None
        
        if current_user and stock.tenant_id != current_user.tenant_id:
            return None
        
        return StockViewModel(
            id=stock.id,
            sku_id=stock.sku_id,
            goods_location_id=stock.goods_location_id,
            qty=stock.qty,
            goods_owner_id=stock.goods_owner_id,
            is_freeze=stock.is_freeze,
            last_update_time=int(stock.last_update_time),
            tenant_id=stock.tenant_id,
            series_number=stock.series_number,
            expiry_date=int(stock.expiry_date),
            price=float(stock.price),
            putaway_date=int(stock.putaway_date),
            warehouse_id=stock.warehouse_id,
            warehouse_name=stock.warehouse_name,
            warehouse_area_id=stock.warehouse_area_id,
            warehouse_area_name=stock.warehouse_area_name,
            warehouse_location_name=stock.warehouse_location_name,
            spu_name=stock.spu_name,
            sku_code=stock.sku_code,
            sku_name=stock.sku_name,
            batch_no=stock.batch_no,
            production_date=int(stock.production_date)
        )

    async def add(self, view_model: StockCreateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        """
        创建新库存
        
        Args:
            view_model: 库存创建数据
            current_user: 当前登录用户
            
        Returns:
            库存ID和操作结果消息
        """
        stock = await self.create_with_tenant(
            current_user.tenant_id,
            sku_id=view_model.sku_id,
            goods_location_id=view_model.goods_location_id,
            qty=view_model.qty,
            goods_owner_id=view_model.goods_owner_id,
            is_freeze=view_model.is_freeze,
            series_number=view_model.series_number,
            expiry_date=datetime.fromtimestamp(view_model.expiry_date) if view_model.expiry_date else datetime(1900, 1, 1),
            price=view_model.price,
            putaway_date=datetime.fromtimestamp(view_model.putaway_date) if view_model.putaway_date else datetime.now(),
            last_update_time=int(datetime.now().timestamp())
        )
        
        return stock.id, "保存成功"

    async def update(self, id: int, view_model: StockUpdateViewModel, current_user: CurrentUser) -> Tuple[bool, str]:
        """
        更新库存信息
        
        Args:
            id: 库存ID
            view_model: 库存更新数据
            current_user: 当前登录用户
            
        Returns:
            是否成功和操作结果消息
        """
        stock = await self._repository.get_by_id(id)
        
        if stock is None:
            return False, "记录不存在"
        
        update_data = {}
        if view_model.sku_id is not None:
            update_data["sku_id"] = view_model.sku_id
        if view_model.goods_location_id is not None:
            update_data["goods_location_id"] = view_model.goods_location_id
        if view_model.qty is not None:
            update_data["qty"] = view_model.qty
        if view_model.goods_owner_id is not None:
            update_data["goods_owner_id"] = view_model.goods_owner_id
        if view_model.is_freeze is not None:
            update_data["is_freeze"] = view_model.is_freeze
        if view_model.series_number is not None:
            update_data["series_number"] = view_model.series_number
        if view_model.expiry_date is not None:
            update_data["expiry_date"] = datetime.fromtimestamp(view_model.expiry_date)
        if view_model.price is not None:
            update_data["price"] = view_model.price
        if view_model.putaway_date is not None:
            update_data["putaway_date"] = datetime.fromtimestamp(view_model.putaway_date)
        
        update_data["last_update_time"] = int(datetime.now().timestamp())
        
        if update_data:
            await self.update_with_tenant(id, stock.tenant_id, **update_data)
        
        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        """
        删除库存
        
        Args:
            id: 库存ID
            
        Returns:
            是否成功和操作结果消息
        """
        stock = await self._repository.get_by_id(id)
        
        if stock is None:
            return False, "记录不存在"
        
        result = await self._repository.delete(id)
        
        if not result:
            return False, "删除失败"
        
        return True, "删除成功"

    async def update_qty(self, id: int, qty_change: int) -> Tuple[bool, str]:
        """
        更新库存数量
        
        Args:
            id: 库存ID
            qty_change: 数量变化量(正数增加,负数减少)
            
        Returns:
            是否成功和操作结果消息
        """
        stock = await self._repository.get_by_id(id)
        
        if stock is None:
            return False, "记录不存在"
        
        new_qty = stock.qty + qty_change
        if new_qty < 0:
            return False, "库存不足"
        
        await self._repository.update(id, qty=new_qty, last_update_time=int(datetime.now().timestamp()))
        
        return True, "更新成功"
