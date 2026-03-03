from typing import List, Optional
from pydantic import BaseModel, Field
from app.ai.tool_registry import register_ai_tool
from app.ai.tool_category import ToolCategory


class QueryToolsByCategoryParams(BaseModel):
    """查询分类工具参数"""
    category: str = Field(description="工具分类代码，如: inventory, stock, order, customer, supplier, warehouse, report, other")


@register_ai_tool(
    name="query_tools_by_category",
    description="查询指定分类下的所有工具的详细信息，包括工具名称、描述、参数等",
    category=ToolCategory.OTHER
)
async def query_tools_by_category(category: str) -> str:
    """
    查询分类工具
    
    Args:
        category: 工具分类代码
        
    Returns:
        工具详细信息
    """
    from app.ai.tool_registry import get_tool_registry
    from app.ai.tool_category import ToolCategory
    
    try:
        cat = ToolCategory(category)
    except ValueError:
        return f"无效的分类代码: {category}。可用的分类代码: inventory, stock, order, customer, supplier, warehouse, report, other"
    
    tool_registry = get_tool_registry()
    tools = tool_registry.get_tools_by_category(cat)
    
    if not tools:
        return f"分类 {category} 下没有可用的工具"
    
    tool_info = []
    for tool in tools:
        args_desc = ""
        if tool.args_schema:
            schema = tool.args_schema
            if hasattr(schema, 'model_fields'):
                fields = []
                for field_name, field_info in schema.model_fields.items():
                    field_desc = f"  - {field_name}: {field_info.description if field_info.description else '无描述'}"
                    if field_info.default is not ...:
                        field_desc += f" (默认值: {field_info.default})"
                    fields.append(field_desc)
                args_desc = "\n参数:\n" + "\n".join(fields)
        
        tool_info.append(
            f"工具名称: {tool.name}\n"
            f"工具描述: {tool.description}\n"
            f"{args_desc}"
        )
    
    return f"分类 {category} 下的工具:\n\n" + "\n\n".join(tool_info)


@register_ai_tool(
    name="get_all_categories",
    description="获取所有可用的工具分类及其描述",
    category=ToolCategory.OTHER
)
async def get_all_categories() -> str:
    """
    获取所有分类
    
    Returns:
        分类信息
    """
    from app.ai.tool_category import get_category_registry
    
    category_registry = get_category_registry()
    categories = category_registry.get_all_categories()
    
    category_info = []
    for cat_info in categories:
        examples_str = ", ".join(cat_info.examples)
        category_info.append(
            f"- {cat_info.category.value}: {cat_info.name}\n"
            f"  描述: {cat_info.description}\n"
            f"  示例: {examples_str}"
        )
    
    return "可用的工具分类:\n\n" + "\n\n".join(category_info)
