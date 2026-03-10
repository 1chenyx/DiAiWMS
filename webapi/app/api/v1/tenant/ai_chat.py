from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.api.responses import success_response, error_response
from app.ai.ai_executor import AIExecutor
from app.ai.tool_category import get_category_registry
from app.ai.tool_registry import get_tool_registry


router = APIRouter(prefix="/ai/chat", tags=["AI聊天"])


@router.post("/")
async def chat(
    config_id: Optional[int] = None,
    messages: list = None,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user = Depends(get_current_user)
):
    """
    AI聊天接口
    
    Args:
        config_id: 配置ID，为空则使用默认配置
        messages: 消息列表
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        聊天结果
    """
    if messages is None or not messages:
        return error_response("缺少messages参数")
    
    executor = AIExecutor(db)
    
    result = await executor.execute_chat(
        config_id=config_id,
        messages=messages,
        tenant_id=current_user.tenant_id
    )
    
    if result["success"]:
        return success_response({
            'content': result.get('content'),
            'usage': result.get('usage')
        })
    else:
        return error_response(result.get("error", "AI执行失败"))


@router.post("/stream")
async def chat_stream(
    config_id: Optional[int] = None,
    messages: list = None,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user = Depends(get_current_user)
):
    """
    AI聊天接口（流式输出）
    
    Args:
        config_id: 配置ID，为空则使用默认配置
        messages: 消息列表
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        流式聊天结果
    """
    if messages is None or not messages:
        return error_response("缺少messages参数")
    
    executor = AIExecutor(db)
    
    async def generate():
        try:
            result = await executor.execute_chat(
                config_id=config_id,
                messages=messages,
                tenant_id=current_user.tenant_id
            )
            
            if result["success"]:
                content = result.get('content', '')
                for char in content:
                    yield f"data: {char}\n\n"
                yield "data: [DONE]\n\n"
            else:
                yield f"data: [ERROR] {result.get('error', 'AI执行失败')}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/tool-categories")
async def get_tool_categories():
    """
    获取工具分类列表
    
    Returns:
        工具分类列表
    """
    category_registry = get_category_registry()
    categories = category_registry.get_all_categories()
    
    result = []
    for cat_info in categories:
        result.append({
            'code': cat_info.category.value,
            'name': cat_info.name,
            'description': cat_info.description,
            'examples': cat_info.examples
        })
    
    return success_response(result)


@router.get("/tools")
async def get_tools(category: Optional[str] = None):
    """
    获取工具列表
    
    Args:
        category: 工具分类代码（可选）
        
    Returns:
        工具列表
    """
    tool_registry = get_tool_registry()
    
    if category:
        from app.ai.tool_category import ToolCategory
        try:
            cat = ToolCategory(category)
            tools = tool_registry.get_tools_by_category(cat)
        except ValueError:
            return error_response("无效的分类代码")
    else:
        tools = tool_registry.get_all_tools()
    
    result = []
    for tool in tools:
        result.append({
            'name': tool.name,
            'description': tool.description,
            'args_schema': str(tool.args_schema) if tool.args_schema else None
        })
    
    return success_response(result)
