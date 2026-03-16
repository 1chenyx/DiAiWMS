"""
库存查询工具
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from loguru import logger

from app.models.entities.inventory.stock import Stock


class StockQueryTool:
    """
    库存查询工具
    
    用于AI Agent查询库存信息
    """
    
    @staticmethod
    async def query_stock_by_sku(
        db: AsyncSession,
        tenant_id: str,
        sku_id: Optional[int] = None,
        sku_code: Optional[str] = None,
        goods_location_id: Optional[int] = None,
        goods_owner_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
        is_freeze: Optional[bool] = None,
        page_index: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        根据条件查询库存
        
        Args:
            db: 数据库会话
            tenant_id: 租户ID
            sku_id: SKU ID
            sku_code: SKU编码
            goods_location_id: 货位ID
            goods_owner_id: 货主ID
            warehouse_id: 仓库ID
            is_freeze: 是否冻结
            page_index: 页码
            page_size: 每页数量
            
        Returns:
            查询结果
        """
        try:
            conditions = [Stock.tenant_id == tenant_id]
            
            if sku_id:
                conditions.append(Stock.sku_id == sku_id)
            if sku_code:
                conditions.append(Stock.sku_code.like(f"%{sku_code}%"))
            if goods_location_id:
                conditions.append(Stock.goods_location_id == goods_location_id)
            if goods_owner_id:
                conditions.append(Stock.goods_owner_id == goods_owner_id)
            if warehouse_id:
                conditions.append(Stock.warehouse_id == warehouse_id)
            if is_freeze is not None:
                conditions.append(Stock.is_freeze == is_freeze)
            
            offset = (page_index - 1) * page_size
            
            stmt = (
                select(Stock)
                .where(and_(*conditions))
                .order_by(Stock.id.desc())
                .offset(offset)
                .limit(page_size)
            )
            
            result = await db.execute(stmt)
            stocks = result.scalars().all()
            
            count_stmt = select(func.count(Stock.id)).where(and_(*conditions))
            count_result = await db.execute(count_stmt)
            total = count_result.scalar() or 0
            
            stock_list = []
            for stock in stocks:
                stock_list.append({
                    "id": stock.id,
                    "sku_id": stock.sku_id,
                    "sku_code": stock.sku_code,
                    "sku_name": stock.sku_name,
                    "spu_name": stock.spu_name,
                    "goods_location_id": stock.goods_location_id,
                    "warehouse_id": stock.warehouse_id,
                    "warehouse_name": stock.warehouse_name,
                    "warehouse_area_id": stock.warehouse_area_id,
                    "warehouse_area_name": stock.warehouse_area_name,
                    "warehouse_location_name": stock.warehouse_location_name,
                    "goods_owner_id": stock.goods_owner_id,
                    "qty": float(stock.qty or 0),
                    "is_freeze": stock.is_freeze,
                    "batch_no": stock.batch_no,
                    "price": float(stock.price or 0),
                    "series_number": stock.series_number,
                    "production_date": stock.production_date,
                    "expiry_date": stock.expiry_date,
                    "putaway_date": stock.putaway_date,
                    "last_update_time": stock.last_update_time
                })
            
            return {
                "success": True,
                "data": stock_list,
                "pagination": {
                    "page_index": page_index,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                }
            }
            
        except Exception as e:
            logger.error(f"库存查询失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def get_stock_summary(
        db: AsyncSession,
        tenant_id: str,
        warehouse_id: Optional[int] = None,
        goods_owner_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取库存汇总
        
        Args:
            db: 数据库会话
            tenant_id: 租户ID
            warehouse_id: 仓库ID
            goods_owner_id: 货主ID
            
        Returns:
            汇总信息
        """
        try:
            conditions = [Stock.tenant_id == tenant_id]
            if warehouse_id:
                conditions.append(Stock.warehouse_id == warehouse_id)
            if goods_owner_id:
                conditions.append(Stock.goods_owner_id == goods_owner_id)
            
            stmt = select(
                func.count(Stock.id).label("sku_species_count"),
                func.sum(Stock.qty).label("total_qty")
            ).where(and_(*conditions))
            
            result = await db.execute(stmt)
            row = result.first()
            
            freeze_stmt = select(
                func.count(Stock.id).label("frozen_count"),
                func.sum(Stock.qty).label("frozen_qty")
            ).where(and_(*conditions, Stock.is_freeze == True))
            
            freeze_result = await db.execute(freeze_stmt)
            freeze_row = freeze_result.first()
            
            return {
                "success": True,
                "data": {
                    "sku_species_count": row.sku_species_count or 0,
                    "total_qty": float(row.total_qty or 0),
                    "frozen_count": freeze_row.frozen_count or 0,
                    "frozen_qty": float(freeze_row.frozen_qty or 0)
                }
            }
            
        except Exception as e:
            logger.error(f"获取库存汇总失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def get_stock_by_location(
        db: AsyncSession,
        tenant_id: str,
        goods_location_id: int
    ) -> Dict[str, Any]:
        """
        获取指定货位的库存
        
        Args:
            db: 数据库会话
            tenant_id: 租户ID
            goods_location_id: 货位ID
            
        Returns:
            库存列表
        """
        return await StockQueryTool.query_stock_by_sku(
            db=db,
            tenant_id=tenant_id,
            goods_location_id=goods_location_id,
            page_size=100
        )
    
    @staticmethod
    async def get_stock_by_warehouse(
        db: AsyncSession,
        tenant_id: str,
        warehouse_id: int,
        page_index: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取指定仓库的库存
        
        Args:
            db: 数据库会话
            tenant_id: 租户ID
            warehouse_id: 仓库ID
            page_index: 页码
            page_size: 每页数量
            
        Returns:
            库存列表
        """
        return await StockQueryTool.query_stock_by_sku(
            db=db,
            tenant_id=tenant_id,
            warehouse_id=warehouse_id,
            page_index=page_index,
            page_size=page_size
        )
    
    @staticmethod
    async def get_low_stock_alerts(
        db: AsyncSession,
        tenant_id: str,
        min_threshold: int = 10,
        warehouse_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取低库存预警
        
        Args:
            db: 数据库会话
            tenant_id: 租户ID
            min_threshold: 最低阈值
            warehouse_id: 仓库ID
            
        Returns:
            低库存SKU列表
        """
        try:
            conditions = [
                Stock.tenant_id == tenant_id,
                Stock.is_freeze == False,
                Stock.qty <= min_threshold
            ]
            
            if warehouse_id:
                conditions.append(Stock.warehouse_id == warehouse_id)
            
            stmt = (
                select(Stock)
                .where(and_(*conditions))
                .order_by(Stock.qty.asc())
                .limit(50)
            )
            
            result = await db.execute(stmt)
            stocks = result.scalars().all()
            
            alert_list = []
            for stock in stocks:
                alert_list.append({
                    "sku_id": stock.sku_id,
                    "sku_code": stock.sku_code,
                    "sku_name": stock.sku_name,
                    "warehouse_name": stock.warehouse_name,
                    "warehouse_location_name": stock.warehouse_location_name,
                    "qty": float(stock.qty or 0),
                    "threshold": min_threshold,
                    "alert_level": "critical" if stock.qty == 0 else "warning"
                })
            
            return {
                "success": True,
                "data": alert_list,
                "total": len(alert_list)
            }
            
        except Exception as e:
            logger.error(f"获取低库存预警失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def get_expiry_alerts(
        db: AsyncSession,
        tenant_id: str,
        days_threshold: int = 30,
        warehouse_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取效期预警
        
        Args:
            db: 数据库会话
            tenant_id: 租户ID
            days_threshold: 天数阈值
            warehouse_id: 仓库ID
            
        Returns:
            效期预警列表
        """
        try:
            import time
            current_time = int(time.time())
            threshold_time = current_time + (days_threshold * 24 * 60 * 60)
            
            conditions = [
                Stock.tenant_id == tenant_id,
                Stock.is_freeze == False,
                Stock.expiry_date > 0,
                Stock.expiry_date <= threshold_time
            ]
            
            if warehouse_id:
                conditions.append(Stock.warehouse_id == warehouse_id)
            
            stmt = (
                select(Stock)
                .where(and_(*conditions))
                .order_by(Stock.expiry_date.asc())
                .limit(50)
            )
            
            result = await db.execute(stmt)
            stocks = result.scalars().all()
            
            alert_list = []
            for stock in stocks:
                days_remaining = (stock.expiry_date - current_time) // (24 * 60 * 60)
                alert_list.append({
                    "sku_id": stock.sku_id,
                    "sku_code": stock.sku_code,
                    "sku_name": stock.sku_name,
                    "batch_no": stock.batch_no,
                    "warehouse_name": stock.warehouse_name,
                    "qty": float(stock.qty or 0),
                    "expiry_date": stock.expiry_date,
                    "days_remaining": days_remaining,
                    "alert_level": "critical" if days_remaining <= 7 else "warning"
                })
            
            return {
                "success": True,
                "data": alert_list,
                "total": len(alert_list)
            }
            
        except Exception as e:
            logger.error(f"获取效期预警失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
