from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.api.responses import success_response, error_response
from app.api.service_dependencies import get_service_dependency
from app.core.current_user import CurrentUser
from app.schemas.ai_config import (
    TenantAIConfigViewModel,
    TenantAIConfigCreateViewModel,
    TenantAIConfigUpdateViewModel,
    TenantAIToolViewModel,
    TenantAIToolCreateViewModel,
    TenantAIToolUpdateViewModel,
    TenantAISkillViewModel,
    TenantAISkillCreateViewModel,
    TenantAISkillUpdateViewModel,
    SkillGenerateRequest,
    TenantAIRuleViewModel,
    TenantAIRuleCreateViewModel,
    TenantAIRuleUpdateViewModel
)
from app.services.system.tenant_ai_config_service import TenantAIConfigService
from app.services.system.tenant_ai_tool_service import TenantAIToolService
from app.services.system.tenant_ai_skill_service import TenantAISkillService
from app.services.system.tenant_ai_rule_service import TenantAIRuleService
from app.ai.llm.connection_pool import get_llm_connection_pool


_tag = "AI服务-AI租户配置"
router = APIRouter(prefix="/ai/config")


# ==================== LLM配置接口 ====================

@router.get("/llm/default")
async def get_default_llm_config(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取默认LLM配置
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        默认配置信息
    """
    service = TenantAIConfigService(db)
    result = await service.get_default_config(current_user.tenant_id)
    
    if result is None:
        return error_response("未找到默认配置")
    
    return success_response(result)


@router.get("/llm/list")
async def get_llm_config_list(
    provider_code: Optional[str] = Query(None, description="服务商代码"),
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取LLM配置列表
    
    Args:
        provider_code: 服务商代码
        page_index: 页码
        page_size: 每页数量
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        配置列表
    """
    service = TenantAIConfigService(db)
    result = await service.get_config_list(current_user, provider_code, page_index, page_size)
    return success_response(result)


@router.get("/llm")
async def get_llm_config(
    config_id: int = Query(..., description="配置ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取LLM配置
    
    Args:
        config_id: 配置ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        配置信息
    """
    service = TenantAIConfigService(db)
    result = await service.get_config_by_id(config_id, current_user)
    
    if result is None:
        return error_response("配置不存在")
    
    return success_response(result)


@router.post("/llm")
async def create_llm_config(
    view_model: TenantAIConfigCreateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建LLM配置
    
    Args:
        view_model: 创建视图模型
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        创建的配置信息
    """
    service = TenantAIConfigService(db)
    config_id, msg = await service.create_config(view_model, current_user)
    
    if config_id == 0:
        return error_response(msg)
    
    result = await service.get_config_by_id(config_id, current_user)
    return success_response(result)


@router.post("/llm/update")
async def update_llm_config(
    view_model: TenantAIConfigUpdateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新LLM配置
    
    Args:
        view_model: 更新视图模型
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        更新后的配置信息
    """
    service = TenantAIConfigService(db)
    flag, msg = await service.update_config(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, view_model.id)
    
    result = await service.get_config_by_id(view_model.id, current_user)
    return success_response(result)


@router.post("/llm/delete")
async def delete_llm_config(
    config_id: int = Query(..., description="配置ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除LLM配置
    
    Args:
        config_id: 配置ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = TenantAIConfigService(db)
    flag, msg = await service.delete_config(config_id, current_user)
    
    if not flag:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, config_id)
    
    return success_response({"id": config_id})


@router.post("/llm/set-default")
async def set_default_llm_config(
    config_id: int = Query(..., description="配置ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    设置为默认LLM配置
    
    Args:
        config_id: 配置ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        设置结果
    """
    service = TenantAIConfigService(db)
    flag, msg = await service.set_as_default(config_id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response({"id": config_id})


# ==================== 工具配置接口 ====================

@router.get("/tools/active")
async def get_active_tools(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取激活的工具列表
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        激活的工具列表
    """
    service = TenantAIToolService(db)
    result = await service.get_active_tools(current_user.tenant_id)
    return success_response(result)


@router.get("/tools/list")
async def get_tool_list(
    category: Optional[str] = Query(None, description="工具分类"),
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取工具配置列表
    
    Args:
        category: 工具分类
        page_index: 页码
        page_size: 每页数量
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        工具列表
    """
    service = TenantAIToolService(db)
    result = await service.get_tool_list(current_user, category, page_index, page_size)
    return success_response(result)


@router.post("/tools/activate")
async def activate_tool(
    view_model: TenantAIToolCreateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    激活工具
    
    Args:
        view_model: 创建视图模型
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        激活的工具信息
    """
    service = TenantAIToolService(db)
    tool_id, msg = await service.activate_tool(view_model, current_user)
    
    if tool_id == 0:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, config_type="tool")
    
    tools = await service.get_active_tools(current_user.tenant_id)
    result = next((t for t in tools if t.id == tool_id), None)
    return success_response(result)


@router.post("/tools/deactivate")
async def deactivate_tool(
    tool_id: int = Query(..., description="工具ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    停用工具
    
    Args:
        tool_id: 工具ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        停用结果
    """
    service = TenantAIToolService(db)
    flag, msg = await service.deactivate_tool(tool_id, current_user)
    
    if not flag:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, config_type="tool")
    
    return success_response({"id": tool_id})


@router.post("/tools/update")
async def update_tool_config(
    view_model: TenantAIToolUpdateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新工具配置
    
    Args:
        view_model: 更新视图模型
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        更新后的工具信息
    """
    service = TenantAIToolService(db)
    flag, msg = await service.update_tool_config(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, config_type="tool")
    
    tools = await service.get_active_tools(current_user.tenant_id)
    result = next((t for t in tools if t.id == view_model.id), None)
    return success_response(result)


# ==================== 技能配置接口 ====================

@router.get("/skills/active")
async def get_active_skills(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取激活的技能列表
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        激活的技能列表
    """
    service = TenantAISkillService(db)
    result = await service.get_active_skills(current_user.tenant_id)
    return success_response(result)


@router.get("/skills/list")
async def get_skill_list(
    skill_type: Optional[str] = Query(None, description="技能类型"),
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取技能配置列表
    
    Args:
        skill_type: 技能类型
        page_index: 页码
        page_size: 每页数量
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        技能列表
    """
    service = TenantAISkillService(db)
    result = await service.get_skill_list(current_user, skill_type, page_index, page_size)
    return success_response(result)


@router.post("/skills")
async def create_skill(
    view_model: TenantAISkillCreateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建技能
    
    Args:
        view_model: 创建视图模型
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        创建的技能信息
    """
    service = TenantAISkillService(db)
    skill_id, msg = await service.create_skill(view_model, current_user)
    
    if skill_id == 0:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, config_type="skill")
    
    result = await service.get_skill_by_id(skill_id, current_user)
    return success_response(result)


@router.post("/skills/update")
async def update_skill(
    view_model: TenantAISkillUpdateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新技能
    
    Args:
        view_model: 更新视图模型
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        更新后的技能信息
    """
    service = TenantAISkillService(db)
    flag, msg = await service.update_skill(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, config_type="skill")
    
    result = await service.get_skill_by_id(view_model.id, current_user)
    return success_response(result)


@router.post("/skills/delete")
async def delete_skill(
    skill_id: int = Query(..., description="技能ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除技能
    
    Args:
        skill_id: 技能ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = TenantAISkillService(db)
    flag, msg = await service.delete_skill(skill_id, current_user)
    
    if not flag:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, config_type="skill")
    
    return success_response({"id": skill_id})


@router.post("/skills/generate")
async def generate_skill(
    request: SkillGenerateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    智能生成技能配置
    
    Args:
        request: 技能生成请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        生成的技能配置
    """
    service = TenantAISkillService(db)
    result, msg = await service.generate_skill(request, current_user)
    
    if not result:
        return error_response(msg)
    
    return success_response(result)


# ==================== 规则配置接口 ====================

@router.get("/rules/active")
async def get_active_rules(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取激活的规则列表（包括系统规则和租户自定义规则）
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        激活的规则列表
    """
    service = TenantAIRuleService(db)
    result = await service.get_active_rules(current_user.tenant_id)
    return success_response(result)


@router.get("/rules/list")
async def get_rule_list(
    category: Optional[str] = Query(None, description="规则类别"),
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取规则配置列表
    
    Args:
        category: 规则类别
        page_index: 页码
        page_size: 每页数量
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        规则列表
    """
    service = TenantAIRuleService(db)
    result = await service.get_rule_list(current_user, category, page_index, page_size)
    return success_response(result)


@router.post("/rules")
async def create_rule(
    view_model: TenantAIRuleCreateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建规则
    
    Args:
        view_model: 创建视图模型
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        创建的规则信息
    """
    service = TenantAIRuleService(db)
    rule_id, msg = await service.create_rule(view_model, current_user)
    
    if rule_id == 0:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, config_type="rule")
    
    result = await service.get_rule_by_id(rule_id, current_user)
    return success_response(result)


@router.post("/rules/update")
async def update_rule(
    view_model: TenantAIRuleUpdateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新规则
    
    Args:
        view_model: 更新视图模型
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        更新后的规则信息
    """
    service = TenantAIRuleService(db)
    flag, msg = await service.update_rule(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, config_type="rule")
    
    result = await service.get_rule_by_id(view_model.id, current_user)
    return success_response(result)


@router.post("/rules/delete")
async def delete_rule(
    rule_id: int = Query(..., description="规则ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除规则
    
    Args:
        rule_id: 规则ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = TenantAIRuleService(db)
    flag, msg = await service.delete_rule(rule_id, current_user)
    
    if not flag:
        return error_response(msg)
    
    pool = get_llm_connection_pool()
    await pool.invalidate_config(current_user.tenant_id, config_type="rule")
    
    return success_response({"id": rule_id})
