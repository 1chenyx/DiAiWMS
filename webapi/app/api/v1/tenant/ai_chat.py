from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.api.responses import success_response, error_response
from app.core.current_user import CurrentUser
from app.ai.agent.agent_pool_manager import get_agent_pool_manager
from loguru import logger


_tag = "AI服务-AI聊天"
router = APIRouter(prefix="/ai/chat")


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色: user/assistant/system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求"""
    messages: List[ChatMessage] = Field(..., description="消息列表")
    config_id: Optional[int] = Field(None, description="配置ID（可选，不传则使用默认配置）")
    stream: bool = Field(False, description="是否流式输出")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="温度参数（可选）")
    max_tokens: Optional[int] = Field(None, ge=1, description="最大token数（可选）")


class ChatResponse(BaseModel):
    """聊天响应"""
    message: ChatMessage = Field(..., description="回复消息")
    usage: dict = Field(..., description="token使用情况")
    agent_info: dict = Field(..., description="Agent信息")


class PoolStatsResponse(BaseModel):
    """池统计响应"""
    total_tenants: int = Field(..., description="租户总数")
    total_agents: int = Field(..., description="Agent总数")
    tenants: dict = Field(..., description="租户详情")


@router.post("/completions")
async def chat_completions(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    AI聊天接口
    
    Args:
        request: 聊天请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        聊天响应
    """
    try:
        pool_manager = get_agent_pool_manager()
        
        agent, error = await pool_manager.get_agent(
            tenant_id=current_user.tenant_id,
            config_id=request.config_id,
            db=db
        )
        
        if error:
            return error_response(error)
        
        logger.info(f"Agent obtained for tenant {current_user.tenant_id}")
        
        response_message = ChatMessage(
            role="assistant",
            content="这是一个模拟的AI回复。在实际实现中，这里会调用LangChain Agent进行真实的对话。"
        )
        
        usage = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
        
        agent_info = {
            "provider_code": agent.get("provider_code", ""),
            "model_code": agent.get("model_code", ""),
            "tools_count": len(agent.get("tools", [])),
            "skills_count": len(agent.get("skills", [])),
            "rules_count": len(agent.get("rules", []))
        }
        
        config_id = request.config_id or 0
        if config_id == 0 and hasattr(agent, 'config_id'):
            config_id = agent.config_id
        
        await pool_manager.release_agent(current_user.tenant_id, config_id)
        
        return success_response(ChatResponse(
            message=response_message,
            usage=usage,
            agent_info=agent_info
        ))
        
    except Exception as e:
        logger.error(f"AI聊天失败: {e}")
        return error_response(str(e))


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    AI流式聊天接口
    
    Args:
        request: 聊天请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        流式响应
    """
    try:
        pool_manager = get_agent_pool_manager()
        
        agent, error = await pool_manager.get_agent(
            tenant_id=current_user.tenant_id,
            config_id=request.config_id,
            db=db
        )
        
        if error:
            return error_response(error)
        
        logger.info(f"Agent obtained for streaming chat for tenant {current_user.tenant_id}")
        
        config_id = request.config_id or 0
        if config_id == 0 and hasattr(agent, 'config_id'):
            config_id = agent.config_id
        
        await pool_manager.release_agent(current_user.tenant_id, config_id)
        
        return success_response({
            "message": "流式聊天功能需要SSE支持，这里返回模拟数据",
            "streaming": True
        })
        
    except Exception as e:
        logger.error(f"AI流式聊天失败: {e}")
        return error_response(str(e))


@router.get("/pool/stats")
async def get_pool_stats(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取Agent池统计信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        池统计信息
    """
    try:
        pool_manager = get_agent_pool_manager()
        stats = pool_manager.get_pool_stats()
        
        return success_response(stats)
        
    except Exception as e:
        logger.error(f"获取池统计信息失败: {e}")
        return error_response(str(e))


@router.post("/pool/clear")
async def clear_pool(
    config_id: Optional[int] = Query(None, description="配置ID（可选，不传则清理该租户所有Agent）"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    清理Agent池
    
    Args:
        config_id: 配置ID
        current_user: 当前用户
        
    Returns:
        清理结果
    """
    try:
        pool_manager = get_agent_pool_manager()
        await pool_manager.clear_tenant_agents(current_user.tenant_id, config_id)
        
        return success_response({
            "message": "Agent池清理成功",
            "tenant_id": current_user.tenant_id,
            "config_id": config_id
        })
        
    except Exception as e:
        logger.error(f"清理Agent池失败: {e}")
        return error_response(str(e))


@router.post("/pool/cleanup")
async def cleanup_expired_agents(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    手动清理过期Agent
    
    Args:
        current_user: 当前用户
        
    Returns:
        清理结果
    """
    try:
        pool_manager = get_agent_pool_manager()
        await pool_manager.cleanup_expired_agents()
        
        return success_response({
            "message": "过期Agent清理完成"
        })
        
    except Exception as e:
        logger.error(f"清理过期Agent失败: {e}")
        return error_response(str(e))
