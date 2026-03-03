from typing import List
from pydantic import BaseModel, Field
from app.ai.tool_registry import register_ai_tool
from app.ai.tool_category import ToolCategory


class GetStockQuery(BaseModel):
    """查询库存参数"""
    sku_code: str = Field(description="商品SKU编码")
    warehouse_id: int = Field(default=None, description="仓库ID，不传则查询所有仓库")


class CreateStockMoveParams(BaseModel):
    """创建库存移动参数"""
    sku_code: str = Field(description="商品SKU编码")
    from_location_id: int = Field(description="源库位ID")
    to_location_id: int = Field(description="目标库位ID")
    quantity: int = Field(description="移动数量")


class CreateOutboundOrderParams(BaseModel):
    """创建出库单参数"""
    customer_id: int = Field(description="客户ID")
    items: List[dict] = Field(description="出库明细列表，每个item包含sku_code和quantity")


@register_ai_tool(
    name="get_stock",
    description="查询指定商品的库存信息，包括在各个仓库的库存数量",
    category=ToolCategory.INVENTORY
)
async def get_stock(sku_code: str, warehouse_id: int = None) -> str:
    """
    查询库存
    
    Args:
        sku_code: 商品SKU编码
        warehouse_id: 仓库ID，不传则查询所有仓库
        
    Returns:
        库存信息
    """
    from sqlalchemy import select
    from app.core.database import get_tenant_db
    from app.models.entities.stock import Stock
    
    try:
        db = get_tenant_db("00000000-0000-0000-0000-000000000001")
        from app.models.entities.sku import Sku
        
        # First get SKU ID
        sku_query = select(Sku).where(Sku.sku_code == sku_code)
        sku_result = await db.execute(sku_query)
        sku = sku_result.scalar_one_or_none()
        
        if not sku:
            return f"商品 {sku_code} 不存在"
        
        query = select(Stock).where(Stock.sku_id == sku.id)
        
        if warehouse_id:
            query = query.where(Stock.goods_location_id == warehouse_id)
        
        result = await db.execute(query)
        stocks = result.scalars().all()
        
        if not stocks:
            return f"商品 {sku_code} 没有库存记录"
        
        stock_info = []
        for stock in stocks:
            stock_info.append(
                f"仓库ID: {stock.goods_location_id}, "
                f"库位ID: {stock.goods_location_id}, "
                f"库存数量: {stock.qty}, "
                f"可用数量: {stock.qty}"
            )
        
        return "\n".join(stock_info)
        
    except Exception as e:
        return f"查询库存失败: {str(e)}"


@register_ai_tool(
    name="create_stock_move",
    description="创建库存移动单据，将商品从一个库位移动到另一个库位",
    category=ToolCategory.STOCK
)
async def create_stock_move(
    sku_code: str,
    from_location_id: int,
    to_location_id: int,
    quantity: int
) -> str:
    """
    创建库存移动
    
    Args:
        sku_code: 商品SKU编码
        from_location_id: 源库位ID
        to_location_id: 目标库位ID
        quantity: 移动数量
        
    Returns:
        操作结果
    """
    try:
        return f"成功创建库存移动单据: 商品 {sku_code} 从库位 {from_location_id} 移动 {quantity} 个到库位 {to_location_id}"
    except Exception as e:
        return f"创建库存移动失败: {str(e)}"


@register_ai_tool(
    name="create_outbound_order",
    description="创建出库单，用于客户订单发货",
    category=ToolCategory.STOCK
)
async def create_outbound_order(
    customer_id: int,
    items: List[dict]
) -> str:
    """
    创建出库单
    
    Args:
        customer_id: 客户ID
        items: 出库明细列表
        
    Returns:
        操作结果
    """
    try:
        item_desc = ", ".join([f"{item['sku_code']} x {item['quantity']}" for item in items])
        return f"成功创建出库单: 客户ID {customer_id}, 商品明细: {item_desc}"
    except Exception as e:
        return f"创建出库单失败: {str(e)}"


@register_ai_tool(
    name="get_warehouse_info",
    description="获取仓库的基本信息，包括仓库名称、地址、联系方式等",
    category=ToolCategory.WAREHOUSE
)
async def get_warehouse_info(warehouse_id: int) -> str:
    """
    获取仓库信息
    
    Args:
        warehouse_id: 仓库ID
        
    Returns:
        仓库信息
    """
    try:
        return f"仓库ID {warehouse_id} 的信息: 名称=测试仓库, 地址=测试地址, 联系电话=1234567890"
    except Exception as e:
        return f"获取仓库信息失败: {str(e)}"


@register_ai_tool(
    name="get_customer_info",
    description="获取客户的基本信息，包括客户名称、联系方式、地址等",
    category=ToolCategory.CUSTOMER
)
async def get_customer_info(customer_id: int) -> str:
    """
    获取客户信息
    
    Args:
        customer_id: 客户ID
        
    Returns:
        客户信息
    """
    try:
        return f"客户ID {customer_id} 的信息: 名称=测试客户, 联系电话=9876543210, 地址=测试客户地址"
    except Exception as e:
        return f"获取客户信息失败: {str(e)}"
