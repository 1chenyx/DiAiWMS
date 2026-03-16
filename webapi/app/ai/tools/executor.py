"""
工具执行器
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.ai.tools.stock_query import StockQueryTool


class ToolExecutor:
    """
    工具执行器
    
    统一管理和执行所有AI工具
    """
    
    _tools = {
        "stock_query": StockQueryTool,
    }
    
    @classmethod
    async def execute(
        cls,
        tool_code: str,
        db: AsyncSession,
        tenant_id: str,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行工具
        
        Args:
            tool_code: 工具代码
            db: 数据库会话
            tenant_id: 租户ID
            action: 操作类型
            params: 参数
            
        Returns:
            执行结果
        """
        try:
            if tool_code not in cls._tools:
                return {
                    "success": False,
                    "error": f"未知的工具: {tool_code}"
                }
            
            tool_class = cls._tools[tool_code]
            
            if tool_code == "stock_query":
                return await cls._execute_stock_query(
                    tool_class, db, tenant_id, action, params
                )
            
            return {
                "success": False,
                "error": f"工具 {tool_code} 未实现"
            }
            
        except Exception as e:
            logger.error(f"工具执行失败: {tool_code}, action: {action}, error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    async def _execute_stock_query(
        cls,
        tool_class,
        db: AsyncSession,
        tenant_id: str,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行库存查询工具
        
        Args:
            tool_class: 工具类
            db: 数据库会话
            tenant_id: 租户ID
            action: 操作类型
            params: 参数
            
        Returns:
            查询结果
        """
        if action == "query_by_sku":
            return await tool_class.query_stock_by_sku(
                db=db,
                tenant_id=tenant_id,
                sku_id=params.get("sku_id"),
                sku_code=params.get("sku_code"),
                goods_location_id=params.get("goods_location_id"),
                goods_owner_id=params.get("goods_owner_id"),
                warehouse_id=params.get("warehouse_id"),
                is_freeze=params.get("is_freeze"),
                page_index=params.get("page_index", 1),
                page_size=params.get("page_size", 20)
            )
        
        elif action == "get_summary":
            return await tool_class.get_stock_summary(
                db=db,
                tenant_id=tenant_id,
                warehouse_id=params.get("warehouse_id"),
                goods_owner_id=params.get("goods_owner_id")
            )
        
        elif action == "get_by_location":
            return await tool_class.get_stock_by_location(
                db=db,
                tenant_id=tenant_id,
                goods_location_id=params.get("goods_location_id")
            )
        
        elif action == "get_by_warehouse":
            return await tool_class.get_stock_by_warehouse(
                db=db,
                tenant_id=tenant_id,
                warehouse_id=params.get("warehouse_id"),
                page_index=params.get("page_index", 1),
                page_size=params.get("page_size", 20)
            )
        
        elif action == "get_low_stock_alerts":
            return await tool_class.get_low_stock_alerts(
                db=db,
                tenant_id=tenant_id,
                min_threshold=params.get("min_threshold", 10),
                warehouse_id=params.get("warehouse_id")
            )
        
        elif action == "get_expiry_alerts":
            return await tool_class.get_expiry_alerts(
                db=db,
                tenant_id=tenant_id,
                days_threshold=params.get("days_threshold", 30),
                warehouse_id=params.get("warehouse_id")
            )
        
        else:
            return {
                "success": False,
                "error": f"未知的操作: {action}"
            }
    
    @classmethod
    def get_available_tools(cls) -> Dict[str, Any]:
        """
        获取可用工具列表
        
        Returns:
            工具列表
        """
        return {
            "stock_query": {
                "name": "库存查询",
                "actions": [
                    {
                        "code": "query_by_sku",
                        "name": "按SKU查询库存",
                        "params": ["sku_id", "sku_code", "goods_location_id", "goods_owner_id", "warehouse_id", "is_freeze", "page_index", "page_size"]
                    },
                    {
                        "code": "get_summary",
                        "name": "获取库存汇总",
                        "params": ["warehouse_id", "goods_owner_id"]
                    },
                    {
                        "code": "get_by_location",
                        "name": "按货位查询库存",
                        "params": ["goods_location_id"]
                    },
                    {
                        "code": "get_by_warehouse",
                        "name": "按仓库查询库存",
                        "params": ["warehouse_id", "page_index", "page_size"]
                    },
                    {
                        "code": "get_low_stock_alerts",
                        "name": "获取低库存预警",
                        "params": ["min_threshold", "warehouse_id"]
                    },
                    {
                        "code": "get_expiry_alerts",
                        "name": "获取效期预警",
                        "params": ["days_threshold", "warehouse_id"]
                    }
                ]
            }
        }


def get_tool_executor() -> ToolExecutor:
    """
    获取工具执行器
    
    Returns:
        工具执行器实例
    """
    return ToolExecutor()
