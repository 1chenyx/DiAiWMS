from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.entities.system import TenantAISkill
from app.repositories.system.tenant_ai_skill_repository import TenantAISkillRepository
from app.services.tenant_aware_service import TenantAwareService
from app.schemas.ai_config import (
    TenantAISkillViewModel,
    TenantAISkillCreateViewModel,
    TenantAISkillUpdateViewModel,
    SkillGenerateRequest
)
from app.utils.cache_manager import CacheManager
from app.core.current_user import CurrentUser
from loguru import logger
import json


class TenantAISkillService(TenantAwareService[TenantAISkillRepository, TenantAISkill]):
    """
    租户AI技能配置服务
    
    提供租户技能配置的管理功能
    """
    
    CACHE_KEY_PREFIX = "ai_skill"
    CACHE_EXPIRE_MINUTES = 60
    
    def __init__(self, db_session: AsyncSession):
        repository = TenantAISkillRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session
        self._cache = CacheManager()
    
    def _get_cache_key(self, tenant_id: str) -> str:
        """
        获取缓存key
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            缓存key
        """
        return f"ModernWMS:{tenant_id}:{self.CACHE_KEY_PREFIX}:list"
    
    def _clear_cache(self, tenant_id: str):
        """
        清理缓存
        
        Args:
            tenant_id: 租户ID
        """
        cache_key = self._get_cache_key(tenant_id)
        self._cache.remove(cache_key)
    
    async def get_active_skills(self, tenant_id: str) -> List[TenantAISkillViewModel]:
        """
        获取租户激活的技能列表
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            激活的技能列表
        """
        cache_key = self._get_cache_key(tenant_id)
        cached_skills = self._cache.get(cache_key)
        if cached_skills:
            return cached_skills
        
        result = await self._db_session.execute(
            select(TenantAISkill).where(
                and_(
                    TenantAISkill.tenant_id == tenant_id,
                    TenantAISkill.is_active == True,
                    TenantAISkill.is_valid == True
                )
            ).order_by(TenantAISkill.skill_type, TenantAISkill.skill_name)
        )
        skills = result.scalars().all()
        
        view_models = [await self._to_view_model(skill) for skill in skills]
        self._cache.set_absolute_expire(cache_key, view_models, self.CACHE_EXPIRE_MINUTES)
        
        return view_models
    
    async def get_skill_by_id(
        self,
        skill_id: int,
        current_user: CurrentUser
    ) -> Optional[TenantAISkillViewModel]:
        """
        根据ID获取技能
        
        Args:
            skill_id: 技能ID
            current_user: 当前用户
            
        Returns:
            技能视图模型
        """
        skill = await self.get_by_id(skill_id)
        if skill is None or skill.tenant_id != current_user.tenant_id:
            return None
        
        return await self._to_view_model(skill)
    
    async def get_skill_list(
        self,
        current_user: CurrentUser,
        skill_type: str = None,
        page_index: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取技能配置列表
        
        Args:
            current_user: 当前用户
            skill_type: 技能类型（可选）
            page_index: 页码
            page_size: 每页数量
            
        Returns:
            分页结果
        """
        filters = {"is_valid": True}
        if skill_type:
            filters["skill_type"] = skill_type
        
        skills, total = await self.page_query_by_tenant(
            page_index,
            page_size,
            current_user.tenant_id,
            filters,
            TenantAISkill.last_update_time.desc()
        )
        
        view_models = [await self._to_view_model(skill) for skill in skills]
        
        return {
            "data": view_models,
            "totals": total,
            "page_index": page_index,
            "page_size": page_size
        }
    
    async def create_skill(
        self,
        view_model: TenantAISkillCreateViewModel,
        current_user: CurrentUser
    ) -> tuple[int, str]:
        """
        创建技能
        
        Args:
            view_model: 创建视图模型
            current_user: 当前用户
            
        Returns:
            (技能ID, 错误消息)
        """
        try:
            skill = await self.create_with_tenant(
                tenant_id=current_user.tenant_id,
                skill_name=view_model.skill_name,
                skill_type=view_model.skill_type,
                description=view_model.description,
                config=view_model.config,
                is_active=view_model.is_active,
                is_valid=True,
                creator=current_user.user_name
            )
            
            self._clear_cache(current_user.tenant_id)
            
            return skill.id, ""
        except Exception as e:
            logger.error(f"创建技能失败: {e}")
            return 0, str(e)
    
    async def update_skill(
        self,
        skill_id: int,
        view_model: TenantAISkillUpdateViewModel,
        current_user: CurrentUser
    ) -> tuple[bool, str]:
        """
        更新技能
        
        Args:
            skill_id: 技能ID
            view_model: 更新视图模型
            current_user: 当前用户
            
        Returns:
            (是否成功, 错误消息)
        """
        try:
            skill = await self.get_by_id(skill_id)
            if skill is None or skill.tenant_id != current_user.tenant_id:
                return False, "技能不存在或无权限"
            
            update_data = {}
            if view_model.skill_name is not None:
                update_data["skill_name"] = view_model.skill_name
            if view_model.skill_type is not None:
                update_data["skill_type"] = view_model.skill_type
            if view_model.description is not None:
                update_data["description"] = view_model.description
            if view_model.config is not None:
                update_data["config"] = view_model.config
            if view_model.is_active is not None:
                update_data["is_active"] = view_model.is_active
            
            if update_data:
                await self.update_with_tenant(skill_id, current_user.tenant_id, **update_data)
            
            self._clear_cache(current_user.tenant_id)
            
            return True, ""
        except Exception as e:
            logger.error(f"更新技能失败: {e}")
            return False, str(e)
    
    async def delete_skill(
        self,
        skill_id: int,
        current_user: CurrentUser
    ) -> tuple[bool, str]:
        """
        删除技能（软删除）
        
        Args:
            skill_id: 技能ID
            current_user: 当前用户
            
        Returns:
            (是否成功, 错误消息)
        """
        try:
            skill = await self.get_by_id(skill_id)
            if skill is None or skill.tenant_id != current_user.tenant_id:
                return False, "技能不存在或无权限"
            
            await self.update_with_tenant(
                skill_id,
                current_user.tenant_id,
                is_valid=False
            )
            
            self._clear_cache(current_user.tenant_id)
            
            return True, ""
        except Exception as e:
            logger.error(f"删除技能失败: {e}")
            return False, str(e)
    
    async def generate_skill(
        self,
        request: SkillGenerateRequest,
        current_user: CurrentUser
    ) -> tuple[Dict[str, Any], str]:
        """
        智能生成技能配置
        
        Args:
            request: 技能生成请求
            current_user: 当前用户
            
        Returns:
            (生成的技能配置, 错误消息)
        """
        try:
            skill_config = {
                "skill_name": f"自定义{request.skill_type}技能",
                "skill_type": request.skill_type,
                "description": request.skill_description,
                "config": {
                    "prompt_template": f"根据用户需求: {request.skill_description}，执行相应的操作",
                    "context": request.context,
                    "parameters": {
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                }
            }
            
            return skill_config, ""
        except Exception as e:
            logger.error(f"生成技能配置失败: {e}")
            return {}, str(e)
    
    async def _to_view_model(self, skill: TenantAISkill) -> TenantAISkillViewModel:
        """
        转换为视图模型
        
        Args:
            skill: 技能实体
            
        Returns:
            技能视图模型
        """
        return TenantAISkillViewModel(
            id=skill.id,
            tenant_id=skill.tenant_id,
            skill_name=skill.skill_name,
            skill_type=skill.skill_type,
            description=skill.description,
            config=skill.config,
            is_active=skill.is_active,
            is_valid=skill.is_valid,
            creator=skill.creator,
            create_time=skill.create_time,
            last_update_time=skill.last_update_time
        )
