"""
AI工具初始化

在应用启动时导入并注册所有AI工具
"""

from app.ai.wms_tools import (
    get_stock,
    create_stock_move,
    create_outbound_order,
    get_warehouse_info,
    get_customer_info
)

from app.ai.tool_query_tools import (
    get_all_categories,
    query_tools_by_category
)

__all__ = [
    "get_stock",
    "create_stock_move",
    "create_outbound_order",
    "get_warehouse_info",
    "get_customer_info",
    "get_all_categories",
    "query_tools_by_category"
]
