"""
LangChain Agent Demo - 工具管理系统
提供工具注册、自动发现、版本管理和访问控制等功能
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type, Callable
from pathlib import Path
import importlib.util
import inspect
from langchain.tools import BaseTool
from langchain.schema import BaseMessage
from pydantic import BaseModel, Field
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class ToolMetadata(BaseModel):
    """工具元数据"""
    name: str = Field(..., description="工具名称")
    version: str = Field(default="1.0.0", description="工具版本")
    description: str = Field(..., description="工具描述")
    author: str = Field(default="", description="工具作者")
    category: str = Field(default="general", description="工具分类")
    enabled: bool = Field(default=True, description="是否启用")
    requires_auth: bool = Field(default=False, description="是否需要认证")
    permissions: List[str] = Field(default_factory=list, description="所需权限列表")
    tags: List[str] = Field(default_factory=list, description="工具标签")
    config: Dict[str, Any] = Field(default_factory=dict, description="工具配置")


class ToolWrapper:
    """工具包装器 - 包装LangChain工具并添加元数据"""
    
    def __init__(
        self,
        tool: BaseTool,
        metadata: ToolMetadata
    ):
        """
        初始化工具包装器
        
        Args:
            tool: LangChain工具实例
            metadata: 工具元数据
        """
        self.tool = tool
        self.metadata = metadata
        self._original_run = tool._run
        self._original_arun = tool._arun if hasattr(tool, '_arun') else None
        
        # 包装工具的执行方法以添加访问控制
        if metadata.requires_auth or metadata.permissions:
            self._wrap_with_access_control()
    
    def _wrap_with_access_control(self):
        """包装工具执行方法以添加访问控制"""
        def check_permissions(user_permissions: List[str]) -> bool:
            """检查用户权限"""
            required = set(self.metadata.permissions)
            return required.issubset(set(user_permissions))
        
        @wraps(self._original_run)
        def wrapped_run(*args, **kwargs):
            user_permissions = kwargs.pop('user_permissions', [])
            if not check_permissions(user_permissions):
                raise PermissionError(
                    f"工具 '{self.metadata.name}' 需要权限: {self.metadata.permissions}"
                )
            return self._original_run(*args, **kwargs)
        
        self.tool._run = wrapped_run
        
        if self._original_arun:
            @wraps(self._original_arun)
            async def wrapped_arun(*args, **kwargs):
                user_permissions = kwargs.pop('user_permissions', [])
                if not check_permissions(user_permissions):
                    raise PermissionError(
                        f"工具 '{self.metadata.name}' 需要权限: {self.metadata.permissions}"
                    )
                return await self._original_arun(*args, **kwargs)
            
            self.tool._arun = wrapped_arun
    
    def get_tool(self) -> BaseTool:
        """获取原始工具"""
        return self.tool
    
    def get_metadata(self) -> ToolMetadata:
        """获取工具元数据"""
        return self.metadata
    
    def is_enabled(self) -> bool:
        """检查工具是否启用"""
        return self.metadata.enabled
    
    def enable(self) -> None:
        """启用工具"""
        self.metadata.enabled = True
    
    def disable(self) -> None:
        """禁用工具"""
        self.metadata.enabled = False


class ToolRegistry:
    """工具注册表 - 管理所有已注册的工具"""
    
    def __init__(self):
        """初始化工具注册表"""
        self._tools: Dict[str, ToolWrapper] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def register(
        self,
        tool: BaseTool,
        metadata: ToolMetadata
    ) -> None:
        """
        注册工具
        
        Args:
            tool: LangChain工具实例
            metadata: 工具元数据
        """
        wrapper = ToolWrapper(tool, metadata)
        self._tools[metadata.name] = wrapper
        
        # 按分类索引
        if metadata.category not in self._categories:
            self._categories[metadata.category] = []
        self._categories[metadata.category].append(metadata.name)
        
        logger.info(f"工具已注册: {metadata.name} v{metadata.version}")
    
    def unregister(self, tool_name: str) -> bool:
        """
        注销工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            bool: 是否成功注销
        """
        if tool_name in self._tools:
            wrapper = self._tools[tool_name]
            category = wrapper.metadata.category
            self._categories[category].remove(tool_name)
            del self._tools[tool_name]
            logger.info(f"工具已注销: {tool_name}")
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            Optional[BaseTool]: 工具实例，如果不存在或未启用则返回None
        """
        wrapper = self._tools.get(tool_name)
        if wrapper and wrapper.is_enabled():
            return wrapper.get_tool()
        return None
    
    def get_tool_wrapper(self, tool_name: str) -> Optional[ToolWrapper]:
        """
        获取工具包装器
        
        Args:
            tool_name: 工具名称
        
        Returns:
            Optional[ToolWrapper]: 工具包装器实例
        """
        return self._tools.get(tool_name)
    
    def list_tools(
        self,
        category: Optional[str] = None,
        enabled_only: bool = True,
        tags: Optional[List[str]] = None
    ) -> List[str]:
        """
        列出工具
        
        Args:
            category: 工具分类（可选）
            enabled_only: 是否只列出已启用的工具
            tags: 工具标签过滤（可选）
        
        Returns:
            List[str]: 工具名称列表
        """
        tools = []
        
        if category:
            tool_names = self._categories.get(category, [])
        else:
            tool_names = list(self._tools.keys())
        
        for tool_name in tool_names:
            wrapper = self._tools[tool_name]
            
            if enabled_only and not wrapper.is_enabled():
                continue
            
            if tags:
                if not any(tag in wrapper.metadata.tags for tag in tags):
                    continue
            
            tools.append(tool_name)
        
        return tools
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """
        按分类获取工具
        
        Args:
            category: 工具分类
        
        Returns:
            List[BaseTool]: 工具实例列表
        """
        tool_names = self._categories.get(category, [])
        tools = []
        
        for tool_name in tool_names:
            tool = self.get_tool(tool_name)
            if tool:
                tools.append(tool)
        
        return tools
    
    def get_all_enabled_tools(self) -> List[BaseTool]:
        """
        获取所有已启用的工具
        
        Returns:
            List[BaseTool]: 工具实例列表
        """
        return [
            wrapper.get_tool()
            for wrapper in self._tools.values()
            if wrapper.is_enabled()
        ]
    
    def enable_tool(self, tool_name: str) -> bool:
        """
        启用工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            bool: 是否成功启用
        """
        wrapper = self._tools.get(tool_name)
        if wrapper:
            wrapper.enable()
            logger.info(f"工具已启用: {tool_name}")
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """
        禁用工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            bool: 是否成功禁用
        """
        wrapper = self._tools.get(tool_name)
        if wrapper:
            wrapper.disable()
            logger.info(f"工具已禁用: {tool_name}")
            return True
        return False
    
    def get_categories(self) -> List[str]:
        """
        获取所有工具分类
        
        Returns:
            List[str]: 分类列表
        """
        return list(self._categories.keys())


class ToolDiscovery:
    """工具发现器 - 自动发现和加载工具"""
    
    def __init__(self, registry: ToolRegistry):
        """
        初始化工具发现器
        
        Args:
            registry: 工具注册表
        """
        self.registry = registry
    
    def discover_from_directory(
        self,
        directory: str,
        pattern: str = "*.py"
    ) -> int:
        """
        从目录自动发现工具
        
        Args:
            directory: 目录路径
            pattern: 文件匹配模式
        
        Returns:
            int: 发现的工具数量
        """
        count = 0
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.warning(f"工具目录不存在: {directory}")
            return 0
        
        for file_path in dir_path.glob(pattern):
            if file_path.name.startswith("_"):
                continue
            
            count += self._load_tools_from_file(file_path)
        
        logger.info(f"从目录发现 {count} 个工具: {directory}")
        return count
    
    def _load_tools_from_file(self, file_path: Path) -> int:
        """
        从文件加载工具
        
        Args:
            file_path: 文件路径
        
        Returns:
            int: 加载的工具数量
        """
        count = 0
        
        try:
            # 动态导入模块
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return 0
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找工具类
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseTool):
                    if obj == BaseTool:
                        continue
                    
                    # 创建工具实例
                    try:
                        tool_instance = obj()
                        
                        # 获取工具元数据
                        metadata = self._extract_tool_metadata(obj, tool_instance)
                        
                        # 注册工具
                        self.registry.register(tool_instance, metadata)
                        count += 1
                    except Exception as e:
                        logger.error(f"创建工具实例失败 {name}: {e}")
        
        except Exception as e:
            logger.error(f"加载工具文件失败 {file_path}: {e}")
        
        return count
    
    def _extract_tool_metadata(
        self,
        tool_class: Type[BaseTool],
        tool_instance: BaseTool
    ) -> ToolMetadata:
        """
        从工具类提取元数据
        
        Args:
            tool_class: 工具类
            tool_instance: 工具实例
        
        Returns:
            ToolMetadata: 工具元数据
        """
        # 从类属性获取元数据
        metadata_dict = getattr(tool_class, '_tool_metadata', {})
        
        # 从实例获取基本信息
        name = metadata_dict.get('name', tool_instance.name)
        description = metadata_dict.get('description', tool_instance.description)
        
        return ToolMetadata(
            name=name,
            description=description,
            version=metadata_dict.get('version', '1.0.0'),
            author=metadata_dict.get('author', ''),
            category=metadata_dict.get('category', 'general'),
            enabled=metadata_dict.get('enabled', True),
            requires_auth=metadata_dict.get('requires_auth', False),
            permissions=metadata_dict.get('permissions', []),
            tags=metadata_dict.get('tags', []),
            config=metadata_dict.get('config', {})
        )
    
    def discover_from_module(self, module_name: str) -> int:
        """
        从模块发现工具
        
        Args:
            module_name: 模块名称
        
        Returns:
            int: 发现的工具数量
        """
        count = 0
        
        try:
            module = importlib.import_module(module_name)
            
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseTool):
                    if obj == BaseTool:
                        continue
                    
                    try:
                        tool_instance = obj()
                        metadata = self._extract_tool_metadata(obj, tool_instance)
                        self.registry.register(tool_instance, metadata)
                        count += 1
                    except Exception as e:
                        logger.error(f"创建工具实例失败 {name}: {e}")
        
        except Exception as e:
            logger.error(f"导入模块失败 {module_name}: {e}")
        
        return count


class ToolManager:
    """工具管理器 - 提供工具管理的统一接口"""
    
    def __init__(self, auto_discover: bool = True, tools_dir: str = "tools"):
        """
        初始化工具管理器
        
        Args:
            auto_discover: 是否自动发现工具
            tools_dir: 工具目录路径
        """
        self.registry = ToolRegistry()
        self.discovery = ToolDiscovery(self.registry)
        
        if auto_discover:
            self.discover_tools(tools_dir)
    
    def discover_tools(self, directory: str) -> int:
        """
        发现工具
        
        Args:
            directory: 工具目录路径
        
        Returns:
            int: 发现的工具数量
        """
        return self.discovery.discover_from_directory(directory)
    
    def register_tool(
        self,
        tool: BaseTool,
        metadata: ToolMetadata
    ) -> None:
        """
        注册工具
        
        Args:
            tool: LangChain工具实例
            metadata: 工具元数据
        """
        self.registry.register(tool, metadata)
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            Optional[BaseTool]: 工具实例
        """
        return self.registry.get_tool(tool_name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """
        获取所有已启用的工具
        
        Returns:
            List[BaseTool]: 工具实例列表
        """
        return self.registry.get_all_enabled_tools()
    
    def list_tools(self, **kwargs) -> List[str]:
        """
        列出工具
        
        Args:
            **kwargs: 过滤参数
        
        Returns:
            List[str]: 工具名称列表
        """
        return self.registry.list_tools(**kwargs)
    
    def enable_tool(self, tool_name: str) -> bool:
        """
        启用工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            bool: 是否成功
        """
        return self.registry.enable_tool(tool_name)
    
    def disable_tool(self, tool_name: str) -> bool:
        """
        禁用工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            bool: 是否成功
        """
        return self.registry.disable_tool(tool_name)


def tool_metadata(
    name: str,
    description: str,
    version: str = "1.0.0",
    author: str = "",
    category: str = "general",
    enabled: bool = True,
    requires_auth: bool = False,
    permissions: List[str] = None,
    tags: List[str] = None,
    **config
):
    """
    工具元数据装饰器
    
    Args:
        name: 工具名称
        description: 工具描述
        version: 工具版本
        author: 工具作者
        category: 工具分类
        enabled: 是否启用
        requires_auth: 是否需要认证
        permissions: 所需权限列表
        tags: 工具标签
        **config: 其他配置
    
    Returns:
        装饰器函数
    """
    def decorator(cls):
        cls._tool_metadata = {
            'name': name,
            'description': description,
            'version': version,
            'author': author,
            'category': category,
            'enabled': enabled,
            'requires_auth': requires_auth,
            'permissions': permissions or [],
            'tags': tags or [],
            'config': config
        }
        return cls
    return decorator
