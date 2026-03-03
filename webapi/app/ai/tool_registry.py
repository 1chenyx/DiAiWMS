from typing import Callable, Dict, Any, List, Optional
from functools import wraps
from langchain_core.tools import BaseTool
from app.ai.tool_category import ToolCategory, get_category_registry


class AIToolRegistry:
    """
    AI工具注册中心
    
    用于管理和注册AI可调用的工具
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_functions: Dict[str, Callable] = {}
        self._tool_categories: Dict[str, ToolCategory] = {}
        self._category_registry = get_category_registry()
    
    def register(self, tool: BaseTool, category: Optional[ToolCategory] = None):
        """
        注册工具
        
        Args:
            tool: 工具实例
            category: 工具分类
        """
        self._tools[tool.name] = tool
        self._tool_functions[tool.name] = tool.func
        
        if category:
            self._tool_categories[tool.name] = category
            self._category_registry.add_tool_to_category(tool.name, category)
    
    def register_function(
        self,
        name: str,
        description: str,
        func: Callable,
        args_schema: Any = None,
        category: Optional[ToolCategory] = None
    ):
        """
        注册函数为工具
        
        Args:
            name: 工具名称
            description: 工具描述
            func: 工具函数
            args_schema: 参数schema
            category: 工具分类
        """
        from langchain_core.tools import StructuredTool
        
        tool = StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
            args_schema=args_schema
        )
        
        self.register(tool, category)
    
    def get_tool(self, name: str) -> BaseTool:
        """
        获取工具
        
        Args:
            name: 工具名称
            
        Returns:
            工具实例
        """
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """
        获取所有工具
        
        Returns:
            工具列表
        """
        return list(self._tools.values())
    
    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """
        根据分类获取工具
        
        Args:
            category: 分类
            
        Returns:
            工具列表
        """
        tool_names = self._category_registry.get_tools_by_category(category)
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_tool_category(self, tool_name: str) -> Optional[ToolCategory]:
        """
        获取工具所属分类
        
        Args:
            tool_name: 工具名称
            
        Returns:
            分类
        """
        return self._tool_categories.get(tool_name)
    
    def has_tool(self, name: str) -> bool:
        """
        检查工具是否存在
        
        Args:
            name: 工具名称
            
        Returns:
            是否存在
        """
        return name in self._tools
    
    def remove_tool(self, name: str):
        """
        移除工具
        
        Args:
            name: 工具名称
        """
        category = self._tool_categories.get(name)
        if category:
            self._category_registry._tools_by_category[category].remove(name)
        
        if name in self._tools:
            del self._tools[name]
        if name in self._tool_functions:
            del self._tool_functions[name]
        if name in self._tool_categories:
            del self._tool_categories[name]
    
    def clear(self):
        """
        清空所有工具
        """
        self._tools.clear()
        self._tool_functions.clear()
        self._tool_categories.clear()
        for category in self._category_registry._tools_by_category:
            self._category_registry._tools_by_category[category].clear()


_global_registry = AIToolRegistry()


def register_ai_tool(
    name: str,
    description: str,
    args_schema: Any = None,
    category: Optional[ToolCategory] = None
):
    """
    AI工具注册装饰器
    
    Args:
        name: 工具名称
        description: 工具描述
        args_schema: 参数schema
        category: 工具分类
        
    Returns:
        装饰器函数
        
    Example:
        @register_ai_tool(
            name="get_weather",
            description="获取某个城市的当前天气",
            category=ToolCategory.INVENTORY
        )
        def get_weather(city: str) -> str:
            return f"{city}的天气是晴天"
    """
    def decorator(func: Callable):
        _global_registry.register_function(
            name=name,
            description=description,
            func=func,
            args_schema=args_schema,
            category=category
        )
        return func
    return decorator


def get_tool_registry() -> AIToolRegistry:
    """
    获取全局工具注册中心
    
    Returns:
        工具注册中心实例
    """
    return _global_registry
