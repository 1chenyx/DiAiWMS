from typing import Dict, List, Optional
from enum import Enum


class ToolCategory(str, Enum):
    """
    工具分类枚举
    """
    INVENTORY = "inventory"
    STOCK = "stock"
    ORDER = "order"
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    WAREHOUSE = "warehouse"
    REPORT = "report"
    OTHER = "other"


class ToolCategoryInfo:
    """
    工具分类信息
    """
    
    def __init__(
        self,
        category: ToolCategory,
        name: str,
        description: str,
        examples: List[str]
    ):
        self.category = category
        self.name = name
        self.description = description
        self.examples = examples


class ToolCategoryRegistry:
    """
    工具分类注册中心
    
    管理工具分类信息
    """
    
    def __init__(self):
        self._categories: Dict[ToolCategory, ToolCategoryInfo] = {}
        self._tools_by_category: Dict[ToolCategory, List[str]] = {}
    
    def register_category(self, category_info: ToolCategoryInfo):
        """
        注册工具分类
        
        Args:
            category_info: 分类信息
        """
        self._categories[category_info.category] = category_info
        if category_info.category not in self._tools_by_category:
            self._tools_by_category[category_info.category] = []
    
    def add_tool_to_category(self, tool_name: str, category: ToolCategory):
        """
        将工具添加到分类
        
        Args:
            tool_name: 工具名称
            category: 分类
        """
        if category not in self._tools_by_category:
            self._tools_by_category[category] = []
        
        if tool_name not in self._tools_by_category[category]:
            self._tools_by_category[category].append(tool_name)
    
    def get_category_info(self, category: ToolCategory) -> Optional[ToolCategoryInfo]:
        """
        获取分类信息
        
        Args:
            category: 分类
            
        Returns:
            分类信息
        """
        return self._categories.get(category)
    
    def get_all_categories(self) -> List[ToolCategoryInfo]:
        """
        获取所有分类
        
        Returns:
            分类列表
        """
        return list(self._categories.values())
    
    def get_tools_by_category(self, category: ToolCategory) -> List[str]:
        """
        获取分类下的工具列表
        
        Args:
            category: 分类
            
        Returns:
            工具名称列表
        """
        return self._tools_by_category.get(category, [])
    
    def get_tool_category(self, tool_name: str) -> Optional[ToolCategory]:
        """
        获取工具所属分类
        
        Args:
            tool_name: 工具名称
            
        Returns:
            分类
        """
        for category, tools in self._tools_by_category.items():
            if tool_name in tools:
                return category
        return None


_global_category_registry = ToolCategoryRegistry()


def get_category_registry() -> ToolCategoryRegistry:
    """
    获取全局分类注册中心
    
    Returns:
        分类注册中心实例
    """
    return _global_category_registry


def init_default_categories():
    """
    初始化默认分类
    """
    registry = get_category_registry()
    
    registry.register_category(ToolCategoryInfo(
        category=ToolCategory.INVENTORY,
        name="库存管理",
        description="用于查询和管理库存信息，包括库存查询、库存调整、库存移动等",
        examples=["查询商品库存", "调整库存数量", "移动库存位置"]
    ))
    
    registry.register_category(ToolCategoryInfo(
        category=ToolCategory.STOCK,
        name="库存操作",
        description="用于库存相关的操作，包括入库、出库、盘点等",
        examples=["创建入库单", "创建出库单", "库存盘点"]
    ))
    
    registry.register_category(ToolCategoryInfo(
        category=ToolCategory.ORDER,
        name="订单管理",
        description="用于订单相关的操作，包括订单查询、订单创建等",
        examples=["查询订单状态", "创建新订单", "订单详情"]
    ))
    
    registry.register_category(ToolCategoryInfo(
        category=ToolCategory.CUSTOMER,
        name="客户管理",
        description="用于客户相关的操作，包括客户查询、客户创建等",
        examples=["查询客户信息", "创建客户", "客户列表"]
    ))
    
    registry.register_category(ToolCategoryInfo(
        category=ToolCategory.SUPPLIER,
        name="供应商管理",
        description="用于供应商相关的操作，包括供应商查询、供应商创建等",
        examples=["查询供应商信息", "创建供应商", "供应商列表"]
    ))
    
    registry.register_category(ToolCategoryInfo(
        category=ToolCategory.WAREHOUSE,
        name="仓库管理",
        description="用于仓库相关的操作，包括仓库查询、仓库创建等",
        examples=["查询仓库信息", "创建仓库", "仓库列表"]
    ))
    
    registry.register_category(ToolCategoryInfo(
        category=ToolCategory.REPORT,
        name="报表管理",
        description="用于报表相关的操作，包括库存报表、订单报表等",
        examples=["生成库存报表", "生成订单报表", "报表统计"]
    ))
    
    registry.register_category(ToolCategoryInfo(
        category=ToolCategory.OTHER,
        name="其他工具",
        description="用于其他类型的工具",
        examples=["其他功能", "辅助工具"]
    ))


init_default_categories()
