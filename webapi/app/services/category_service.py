from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Category
from app.schemas.category import CategoryViewModel, CategoryCreateViewModel, CategoryUpdateViewModel, CategoryTreeViewModel
from app.core.current_user import CurrentUser
from app.repositories.category_repository import CategoryRepository
from app.services.base_service import TenantAwareService


class CategoryService(TenantAwareService[CategoryRepository, Category]):
    """
    分类服务类
    """

    def __init__(self, db_session: AsyncSession):
        repository = CategoryRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def get_all(self, current_user: CurrentUser) -> List[CategoryViewModel]:
        categories = await self.get_by_tenant(current_user.tenant_id)
        
        return [
            CategoryViewModel(
                id=category.id,
                category_name=category.category_name,
                parent_id=category.parent_id,
                creator=category.creator,
                create_time=int(category.create_time),
                last_update_time=int(category.last_update_time),
                is_valid=category.is_valid,
                tenant_id=category.tenant_id
            )
            for category in categories
        ]

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[CategoryViewModel]:
        category = await self._repository.get_by_id(id)
        
        if category is None:
            return None
        
        if current_user and category.tenant_id != current_user.tenant_id:
            return None
        
        return CategoryViewModel(
            id=category.id,
            category_name=category.category_name,
            parent_id=category.parent_id,
            creator=category.creator,
            create_time=int(category.create_time),
            last_update_time=int(category.last_update_time),
            is_valid=category.is_valid,
            tenant_id=category.tenant_id
        )

    async def add(self, view_model: CategoryCreateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        existing = await self.get_one_by_tenant(
            current_user.tenant_id,
            filters={"category_name": view_model.category_name}
        )
        
        if existing:
            return 0, f"分类名称 '{view_model.category_name}' 已存在"
        
        category = await self.create_with_tenant(
            current_user.tenant_id,
            category_name=view_model.category_name,
            parent_id=view_model.parent_id,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            is_valid=view_model.is_valid
        )
        
        return category.id, "保存成功"

    async def update(self, id: int, view_model: CategoryUpdateViewModel, current_user: CurrentUser) -> Tuple[bool, str]:
        category = await self._repository.get_by_id(id)
        
        if category is None:
            return False, "记录不存在"
        
        if view_model.category_name is not None:
            existing = await self.get_one_by_tenant(
                category.tenant_id,
                filters={"category_name": view_model.category_name}
            )
            
            if existing and existing.id != id:
                return False, f"分类名称 '{view_model.category_name}' 已存在"
        
        update_data = {}
        if view_model.category_name is not None:
            update_data["category_name"] = view_model.category_name
        if view_model.parent_id is not None:
            update_data["parent_id"] = view_model.parent_id
        if view_model.is_valid is not None:
            update_data["is_valid"] = view_model.is_valid
            if category.parent_id > 0:
                query = select(Category).where(Category.parent_id > 0)
                result = await self._db_session.execute(query)
                all_categories = result.scalars().all()
                
                children = self._get_children(all_categories, id)
                for child in children:
                    child.is_valid = view_model.is_valid
                    child.last_update_time = int(datetime.now().timestamp())
        
        if update_data:
            await self._repository.update(id, **update_data)
        
        return True, "保存成功"

    def _get_children(self, categories: List[Category], parent_id: int) -> List[Category]:
        children = []
        for category in categories:
            if category.parent_id == parent_id:
                children.append(category)
                children.extend(self._get_children(categories, category.id))
        return children

    async def delete(self, id: int, current_user: Optional[CurrentUser] = None) -> Tuple[bool, str]:
        category = await self._repository.get_by_id(id)
        
        if category is None:
            return False, "记录不存在"
        
        if current_user and category.tenant_id != current_user.tenant_id:
            return False, "无权删除该记录"
        
        children = await self._repository.get_by_parent_id(id, category.tenant_id)
        
        if children:
            return False, "存在子分类，无法删除"
        
        result = await self._repository.delete(id)
        
        if not result:
            return False, "删除失败"
        
        return True, "删除成功"

    async def get_tree(self, current_user: CurrentUser) -> List[CategoryTreeViewModel]:
        """
        获取分类树形结构
        
        Args:
            current_user: 当前登录用户
            
        Returns:
            分类树形结构列表
        """
        categories = await self.get_by_tenant(current_user.tenant_id)
        
        # 构建树形结构
        tree_nodes = {}
        
        for category in categories:
            tree_node = CategoryTreeViewModel(
                id=category.id,
                category_name=category.category_name,
                parent_id=category.parent_id,
                creator=category.creator,
                create_time=int(category.create_time),
                last_update_time=int(category.last_update_time),
                is_valid=category.is_valid,
                tenant_id=category.tenant_id,
                children=[]
            )
            tree_nodes[category.id] = tree_node
        
        # 构建父子关系
        root_nodes = []
        for category in categories:
            node = tree_nodes[category.id]
            if category.parent_id == 0:
                root_nodes.append(node)
            else:
                parent = tree_nodes.get(category.parent_id)
                if parent:
                    parent.children.append(node)
        
        return root_nodes
