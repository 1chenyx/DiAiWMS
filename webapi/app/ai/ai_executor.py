import uuid
from typing import Dict, Any, Optional, List, TypedDict, Annotated
from operator import add
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from app.models.entities.tenant_ai_config import TenantAIConfig
from app.ai.ai_providers import AIProviderFactory
from app.ai.config_loader import get_ai_config_loader
from app.ai.tool_registry import get_tool_registry
from app.ai.tool_category import get_category_registry


class AgentState(TypedDict):
    """
    Agent状态
    
    用于langgraph工作流的状态管理
    """
    messages: Annotated[List[BaseMessage], add]


class AIExecutor:
    """
    AI执行器
    
    负责AI任务的执行和管理，支持智能工具调用
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        from app.services.ai_config_service import TenantAIConfigService
        self.config_service = TenantAIConfigService(db)
        self.config_loader = get_ai_config_loader()
        self.tool_registry = get_tool_registry()
        self.category_registry = get_category_registry()
    
    async def execute_chat(
        self,
        config_id: Optional[int],
        messages: List,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行AI聊天任务
        
        Args:
            config_id: 租户AI配置ID，为空则使用默认配置
            messages: 消息列表
            tenant_id: 租户ID
            
        Returns:
            执行结果
        """
        try:
            tenant_ai_config = await self._get_tenant_config(config_id, tenant_id)
            
            if tenant_ai_config is None:
                return {
                    'success': False,
                    'error': '未找到AI配置'
                }
            
            provider_code = tenant_ai_config.provider_code
            model_code = tenant_ai_config.model_code
            api_key = tenant_ai_config.api_key
            api_endpoint = tenant_ai_config.api_endpoint
            
            result = await self._execute_chat_with_tools(
                provider_code=provider_code,
                model_code=model_code,
                api_key=api_key,
                api_endpoint=api_endpoint,
                messages=messages,
                temperature=None,
                top_p=None,
                max_tokens=None
            )
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_tenant_config(
        self,
        config_id: Optional[int],
        tenant_id: Optional[str]
    ) -> Optional[TenantAIConfig]:
        """
        获取租户AI配置
        
        Args:
            config_id: 配置ID
            tenant_id: 租户ID
            
        Returns:
            租户AI配置
        """
        if config_id:
            from sqlalchemy import select
            result = await self.db.execute(
                select(TenantAIConfig).where(TenantAIConfig.id == config_id)
            )
            return result.scalar_one_or_none()
        elif tenant_id:
            config_view = await self.config_service.get_default(tenant_id)
            if config_view:
                result = await self.db.execute(
                    select(TenantAIConfig).where(TenantAIConfig.id == config_view.id)
                )
                return result.scalar_one_or_none()
        return None
    
    async def _execute_chat_with_tools(
        self,
        provider_code: str,
        model_code: str,
        api_key: str,
        api_endpoint: Optional[str],
        messages: List,
        temperature: Optional[float],
        top_p: Optional[float],
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """
        执行带工具的聊天任务（使用langgraph）
        
        Args:
            provider_code: 提供商代码
            model_code: 模型代码
            api_key: API密钥
            api_endpoint: API端点URL
            messages: 消息列表
            temperature: 温度参数
            top_p: top_p参数
            max_tokens: 最大token数
            
        Returns:
            执行结果
        """
        if not messages:
            return {
                'success': False,
                'error': '缺少messages参数'
            }
        
        all_tools = self.tool_registry.get_all_tools()
        
        if not all_tools:
            return await self._execute_simple_chat(
                provider_code=provider_code,
                model_code=model_code,
                api_key=api_key,
                api_endpoint=api_endpoint,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
        
        query_tools = [
            tool for tool in all_tools 
            if tool.name in ['get_all_categories', 'query_tools_by_category']
        ]
        
        if not query_tools:
            return await self._execute_simple_chat(
                provider_code=provider_code,
                model_code=model_code,
                api_key=api_key,
                api_endpoint=api_endpoint,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
        
        system_message = """你是一个智能助手，可以帮助用户完成各种任务。

重要提示：
1. 你可以使用各种工具来帮助用户完成任务
2. 在使用工具之前，你需要先了解有哪些可用的工具
3. 使用 get_all_categories 工具查看所有工具分类
4. 使用 query_tools_by_category 工具查看特定分类下的工具详情
5. 查看完工具详情后，再决定使用哪些工具来完成任务
6. 可以多次调用 query_tools_by_category 来查看不同分类的工具
7. 了解工具详情后，就可以使用这些工具来完成任务

工作流程：
1. 首先调用 get_all_categories 查看所有工具分类
2. 根据用户需求，调用 query_tools_by_category 查看相关分类的工具详情
3. 了解工具的参数和用法后，调用相应的工具完成任务
4. 将工具执行结果整理后回复给用户

请按照这个流程来处理用户的请求。"""
        
        from langchain_core.messages import SystemMessage
        enhanced_messages = [SystemMessage(content=system_message)] + messages
        
        llm = self._create_llm(
            provider_code=provider_code,
            model_code=model_code,
            api_key=api_key,
            api_endpoint=api_endpoint,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        
        llm_with_tools = llm.bind_tools(all_tools)
        
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self._call_model_node(llm_with_tools))
        workflow.add_node("tools", self._call_tool_node(all_tools))
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {"tools": "tools", END: END}
        )
        workflow.add_edge("tools", "agent")
        
        app = workflow.compile()
        
        inputs = {"messages": enhanced_messages}
        
        try:
            final_state = None
            for output in app.stream(inputs):
                for key, value in output.items():
                    if 'messages' in value:
                        final_state = value
            
            if final_state and final_state['messages']:
                last_message = final_state['messages'][-1]
                content = last_message.content if hasattr(last_message, 'content') else str(last_message)
                
                return {
                    'success': True,
                    'content': content,
                    'usage': {}
                }
            else:
                return {
                    'success': False,
                    'error': 'AI执行失败，没有返回结果'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'AI执行异常: {str(e)}'
            }
    
    def _call_model_node(self, llm):
        """
        调用LLM节点
        
        Args:
            llm: LLM实例
            
        Returns:
            节点函数
        """
        def call_model(state: AgentState):
            messages = state['messages']
            response = llm.invoke(messages)
            return {"messages": [response]}
        return call_model
    
    def _call_tool_node(self, tools: List):
        """
        调用工具节点
        
        Args:
            tools: 工具列表
            
        Returns:
            节点函数
        """
        def call_tool(state: AgentState):
            last_ai_message = state['messages'][-1]
            tool_calls = last_ai_message.tool_calls
            
            tool_messages = []
            for tool_call in tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                executed_tool = next((t for t in tools if t.name == tool_name), None)
                if executed_tool:
                    try:
                        result = executed_tool.invoke(tool_args)
                        tool_messages.append(
                            ToolMessage(content=str(result), tool_call_id=tool_call['id'])
                        )
                    except Exception as e:
                        tool_messages.append(
                            ToolMessage(
                                content=f"工具执行错误: {str(e)}",
                                tool_call_id=tool_call['id']
                            )
                        )
                else:
                    tool_messages.append(
                        ToolMessage(
                            content=f"错误：未找到工具 {tool_name}",
                            tool_call_id=tool_call['id']
                        )
                    )
            return {"messages": tool_messages}
        return call_tool
    
    def _should_continue(self, state: AgentState):
        """
        判断是否继续执行
        
        Args:
            state: Agent状态
            
        Returns:
            下一步节点名称
        """
        last_message = state['messages'][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        else:
            return END
    
    def _create_llm(
        self,
        provider_code: str,
        model_code: str,
        api_key: str,
        api_endpoint: Optional[str],
        temperature: Optional[float],
        top_p: Optional[float],
        max_tokens: Optional[int]
    ):
        """
        创建LLM实例
        
        Args:
            provider_code: 提供商代码
            model_code: 模型代码
            api_key: API密钥
            api_endpoint: API端点URL
            temperature: 温度参数
            top_p: top_p参数
            max_tokens: 最大token数
            
        Returns:
            LLM实例
        """
        if provider_code == 'openai':
            return ChatOpenAI(
                model=model_code,
                api_key=api_key,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
        elif provider_code == 'anthropic':
            return ChatAnthropic(
                model=model_code,
                api_key=api_key,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
        else:
            raise ValueError(f"不支持的提供商: {provider_code}")
    
    async def _execute_simple_chat(
        self,
        provider_code: str,
        model_code: str,
        api_key: str,
        api_endpoint: Optional[str],
        messages: List,
        temperature: Optional[float],
        top_p: Optional[float],
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """
        执行简单聊天任务（不使用工具）
        
        Args:
            provider_code: 提供商代码
            model_code: 模型代码
            api_key: API密钥
            api_endpoint: API端点URL
            messages: 消息列表
            temperature: 温度参数
            top_p: top_p参数
            max_tokens: 最大token数
            
        Returns:
            执行结果
        """
        provider = AIProviderFactory.create_provider(
            provider_code=provider_code,
            api_key=api_key,
            api_endpoint=api_endpoint
        )
        
        result = await provider.chat(
            messages=messages,
            model=model_code,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        
        return result
