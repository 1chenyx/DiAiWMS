from fastapi import APIRouter, Depends, Query
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.api.responses import success_response, error_response
from app.core.current_user import CurrentUser
from app.ai.services.chat_service import AIChatService
from app.ai.tools.executor import ToolExecutor
from app.ai.llm.connection_pool import get_llm_connection_pool
from app.schemas.ai_config import ChatMessage, ChatRequest, ChatResponse
from loguru import logger


_tag = "AI服务-AI聊天"
router = APIRouter(prefix="/ai/chat")


class ToolExecuteRequest(BaseModel):
    """工具执行请求"""
    tool_code: str = Field(..., description="工具代码")
    action: str = Field(..., description="操作类型")
    params: Dict[str, Any] = Field(default_factory=dict, description="参数")


@router.post("/completions")
async def chat_completions(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    AI聊天接口
    
    根据租户配置的LLM、工具、技能和规则执行AI对话。
    支持Function Calling，自动调用配置的工具。
    
    Args:
        request: 聊天请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        聊天响应
    """
    try:
        chat_service = AIChatService(db)
        
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        result = await chat_service.chat(
            tenant_id=current_user.tenant_id,
            messages=messages,
            config_id=request.config_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        if not result.get("success"):
            return error_response(result.get("error", "AI聊天失败"))
        
        response_message = ChatMessage(
            role=result["message"]["role"],
            content=result["message"]["content"]
        )
        
        return success_response(ChatResponse(
            message=response_message,
            usage=result.get("usage", {}),
            agent_info={
                "iterations": result.get("iterations", 1)
            }
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
        return error_response("流式聊天功能暂未实现")
        
    except Exception as e:
        logger.error(f"AI流式聊天失败: {e}")
        return error_response(str(e))


@router.post("/tool/execute")
async def execute_tool(
    request: ToolExecuteRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    执行AI工具
    
    直接执行指定的AI工具，用于测试或手动调用。
    
    Args:
        request: 工具执行请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        执行结果
    """
    try:
        executor = ToolExecutor()
        result = await executor.execute(
            tool_code=request.tool_code,
            db=db,
            tenant_id=current_user.tenant_id,
            action=request.action,
            params=request.params
        )
        
        return success_response(result)
        
    except Exception as e:
        logger.error(f"工具执行失败: {e}")
        return error_response(str(e))


@router.get("/tool/list")
async def list_tools(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取可用工具列表
    
    Args:
        current_user: 当前用户
        
    Returns:
        工具列表
    """
    try:
        executor = ToolExecutor()
        tools = executor.get_available_tools()
        
        return success_response(tools)
        
    except Exception as e:
        logger.error(f"获取工具列表失败: {e}")
        return error_response(str(e))


@router.get("/pool/stats")
async def get_pool_stats(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取LLM连接池统计信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        连接池统计信息
    """
    try:
        pool = get_llm_connection_pool()
        stats = pool.get_pool_stats()
        
        return success_response(stats)
        
    except Exception as e:
        logger.error(f"获取连接池统计信息失败: {e}")
        return error_response(str(e))


@router.post("/pool/clear")
async def clear_pool(
    config_id: Optional[int] = Query(None, description="配置ID（可选，不传则清理该租户所有连接）"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    清理LLM连接池
    
    Args:
        config_id: 配置ID
        current_user: 当前用户
        
    Returns:
        清理结果
    """
    try:
        pool = get_llm_connection_pool()
        await pool.clear_tenant_connections(current_user.tenant_id, config_id)
        
        return success_response({
            "message": "LLM连接池清理成功",
            "tenant_id": current_user.tenant_id,
            "config_id": config_id
        })
        
    except Exception as e:
        logger.error(f"清理连接池失败: {e}")
        return error_response(str(e))


@router.post("/pool/cleanup")
async def cleanup_expired_connections(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    手动清理过期连接
    
    Args:
        current_user: 当前用户
        
    Returns:
        清理结果
    """
    try:
        pool = get_llm_connection_pool()
        await pool.cleanup_expired_connections()
        
        return success_response({
            "message": "过期连接清理完成"
        })
        
    except Exception as e:
        logger.error(f"清理过期连接失败: {e}")
        return error_response(str(e))
