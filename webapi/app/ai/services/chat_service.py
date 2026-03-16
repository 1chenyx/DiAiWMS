"""
AI聊天服务
"""
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.ai.llm.client import LLMClient
from app.ai.llm.connection_pool import get_llm_connection_pool
from app.ai.llm.base import ChatMessage, ToolDefinition
from app.ai.tools.executor import ToolExecutor
from app.services.system.tenant_ai_config_service import TenantAIConfigService
from app.services.system.tenant_ai_tool_service import TenantAIToolService
from app.services.system.tenant_ai_skill_service import TenantAISkillService
from app.services.system.tenant_ai_rule_service import TenantAIRuleService
from app.schemas.ai_config import (
    TenantAIConfigViewModel,
    TenantAIToolViewModel,
    TenantAISkillViewModel,
    TenantAIRuleViewModel
)


class AIChatService:
    """
    AI聊天服务
    
    整合LLM客户端、工具、技能和规则，提供完整的AI聊天功能
    """
    
    MAX_TOOL_CALL_ITERATIONS = 5
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.config_service = TenantAIConfigService(db)
        self.tool_service = TenantAIToolService(db)
        self.skill_service = TenantAISkillService(db)
        self.rule_service = TenantAIRuleService(db)
        self.tool_executor = ToolExecutor()
    
    async def chat(
        self,
        tenant_id: str,
        messages: List[Dict[str, str]],
        config_id: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        执行AI聊天
        
        Args:
            tenant_id: 租户ID
            messages: 消息列表
            config_id: 配置ID
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            聊天响应
        """
        config = await self._get_config(tenant_id, config_id)
        if not config:
            return {
                "success": False,
                "error": "未找到AI配置，请先配置LLM"
            }
        
        tools = await self.tool_service.get_active_tools(tenant_id)
        skills = await self.skill_service.get_active_skills(tenant_id)
        rules = await self.rule_service.get_active_rules(tenant_id)
        
        tools_data = [tool.dict() for tool in tools]
        skills_data = [skill.dict() for skill in skills]
        rules_data = [rule.dict() for rule in rules]
        
        connection_pool = get_llm_connection_pool()
        client, is_new = await connection_pool.get_client(
            tenant_id=tenant_id,
            config_id=config.id,
            provider_code=config.provider_code,
            model_code=config.model_code,
            api_key=config.api_key,
            api_endpoint=config.api_endpoint,
            tools=tools_data,
            skills=skills_data,
            rules=rules_data
        )
        
        chat_messages = self._build_messages(messages, skills, rules)
        tool_definitions = self._build_tool_definitions(tools)
        
        final_temperature = temperature if temperature is not None else (config.temperature or 0.7)
        final_max_tokens = max_tokens if max_tokens is not None else (config.max_tokens or 2000)
        
        try:
            result = await self._execute_with_tools(
                client=client,
                messages=chat_messages,
                model=config.model_code,
                temperature=final_temperature,
                max_tokens=final_max_tokens,
                tools=tool_definitions,
                tenant_id=tenant_id
            )
            return result
        finally:
            await connection_pool.release_client(tenant_id, config.id)
    
    async def _get_config(
        self,
        tenant_id: str,
        config_id: Optional[int]
    ) -> Optional[TenantAIConfigViewModel]:
        """
        获取AI配置
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID
            
        Returns:
            AI配置
        """
        if config_id:
            config = await self.config_service.get_by_id(config_id)
            if config and config.tenant_id == tenant_id:
                return await self.config_service._to_view_model(config)
            return None
        return await self.config_service.get_default_config(tenant_id)
    
    def _build_messages(
        self,
        user_messages: List[Dict[str, str]],
        skills: List[TenantAISkillViewModel],
        rules: List[TenantAIRuleViewModel]
    ) -> List[ChatMessage]:
        """
        构建消息列表
        
        Args:
            user_messages: 用户消息
            skills: 技能列表
            rules: 规则列表
            
        Returns:
            消息列表
        """
        messages = []
        
        system_content = self._build_system_prompt(skills, rules)
        if system_content:
            messages.append(ChatMessage(role="system", content=system_content))
        
        for msg in user_messages:
            messages.append(ChatMessage(
                role=msg.get("role", "user"),
                content=msg.get("content", "")
            ))
        
        return messages
    
    def _build_system_prompt(
        self,
        skills: List[TenantAISkillViewModel],
        rules: List[TenantAIRuleViewModel]
    ) -> str:
        """
        构建系统提示词
        
        Args:
            skills: 技能列表
            rules: 规则列表
            
        Returns:
            系统提示词
        """
        parts = []
        
        parts.append("你是一个智能仓库管理助手，帮助用户处理仓库相关的查询和操作。")
        
        if rules:
            sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)
            rule_contents = []
            for rule in sorted_rules:
                if rule.content:
                    rule_contents.append(f"- {rule.content}")
            if rule_contents:
                parts.append("\n## 行为规则\n" + "\n".join(rule_contents))
        
        if skills:
            skill_descriptions = []
            for skill in skills:
                try:
                    config = json.loads(skill.config) if skill.config else {}
                    prompt = config.get("prompt", skill.description)
                    if prompt:
                        skill_descriptions.append(f"- {skill.skill_name}: {prompt}")
                except:
                    if skill.description:
                        skill_descriptions.append(f"- {skill.skill_name}: {skill.description}")
            if skill_descriptions:
                parts.append("\n## 技能说明\n" + "\n".join(skill_descriptions))
        
        return "\n".join(parts)
    
    def _build_tool_definitions(
        self,
        tools: List[TenantAIToolViewModel]
    ) -> List[ToolDefinition]:
        """
        构建工具定义
        
        Args:
            tools: 工具列表
            
        Returns:
            工具定义列表
        """
        definitions = []
        
        tool_schemas = {
            "stock_query": {
                "name": "stock_query",
                "description": "查询库存信息，包括SKU、数量、位置等",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["query_by_sku", "get_summary", "get_by_location", "get_by_warehouse", "get_low_stock_alerts", "get_expiry_alerts"],
                            "description": "操作类型"
                        },
                        "params": {
                            "type": "object",
                            "description": "查询参数"
                        }
                    },
                    "required": ["action"]
                }
            }
        }
        
        for tool in tools:
            if tool.tool_code in tool_schemas:
                definitions.append(ToolDefinition(
                    type="function",
                    function=tool_schemas[tool.tool_code]
                ))
        
        return definitions
    
    async def _execute_with_tools(
        self,
        client: LLMClient,
        messages: List[ChatMessage],
        model: str,
        temperature: float,
        max_tokens: int,
        tools: List[ToolDefinition],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        执行带工具调用的聊天
        
        Args:
            client: LLM客户端
            messages: 消息列表
            model: 模型代码
            temperature: 温度参数
            max_tokens: 最大token数
            tools: 工具列表
            tenant_id: 租户ID
            
        Returns:
            聊天响应
        """
        iteration = 0
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        while iteration < self.MAX_TOOL_CALL_ITERATIONS:
            iteration += 1
            
            try:
                response = await client.chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else None
                )
            except Exception as e:
                logger.error(f"LLM调用失败: {e}")
                return {
                    "success": False,
                    "error": f"LLM调用失败: {str(e)}"
                }
            
            if response.usage:
                total_usage["prompt_tokens"] += response.usage.get("prompt_tokens", 0)
                total_usage["completion_tokens"] += response.usage.get("completion_tokens", 0)
                total_usage["total_tokens"] += response.usage.get("total_tokens", 0)
            
            if not response.choices:
                return {
                    "success": False,
                    "error": "LLM返回空响应"
                }
            
            choice = response.choices[0]
            message = choice.get("message", {})
            finish_reason = choice.get("finish_reason", "")
            
            if finish_reason == "tool_calls" or message.get("tool_calls"):
                tool_calls = message.get("tool_calls", [])
                
                messages.append(ChatMessage(
                    role="assistant",
                    content=message.get("content", ""),
                    tool_calls=tool_calls
                ))
                
                for tool_call in tool_calls:
                    tool_result = await self._execute_tool_call(
                        tool_call, tenant_id
                    )
                    
                    messages.append(ChatMessage(
                        role="tool",
                        content=json.dumps(tool_result, ensure_ascii=False),
                        tool_call_id=tool_call.get("id", "")
                    ))
                
                continue
            
            assistant_content = message.get("content", "")
            
            return {
                "success": True,
                "message": {
                    "role": "assistant",
                    "content": assistant_content
                },
                "usage": total_usage,
                "iterations": iteration
            }
        
        return {
            "success": False,
            "error": "工具调用次数超过限制"
        }
    
    async def _execute_tool_call(
        self,
        tool_call: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        执行工具调用
        
        Args:
            tool_call: 工具调用信息
            tenant_id: 租户ID
            
        Returns:
            工具执行结果
        """
        function = tool_call.get("function", {})
        tool_name = function.get("name", "")
        
        try:
            arguments = json.loads(function.get("arguments", "{}"))
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "工具参数解析失败"
            }
        
        action = arguments.get("action", "")
        params = arguments.get("params", {})
        
        logger.info(f"执行工具: {tool_name}, action: {action}, params: {params}")
        
        result = await self.tool_executor.execute(
            tool_code=tool_name,
            db=self.db,
            tenant_id=tenant_id,
            action=action,
            params=params
        )
        
        return result
