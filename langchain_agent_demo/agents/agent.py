"""
LangChain Agent Demo - Agent核心逻辑
实现Agent的核心功能，包括深度思考、工具调用、技能使用等
"""
from typing import Dict, List, Optional, Any, Callable
from langchain.agents import AgentExecutor, create_react_agent, create_structured_chat_agent
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
import logging
import asyncio

from ..core.config import AgentSystemConfig, AgentType as ConfigAgentType
from ..core.personal_rules import PersonalRulesManager
from ..llm_providers import LLMProviderFactory, BaseLLMProvider
from ..tools import ToolManager
from ..skills import SkillManager
from ..memory import MemoryManager, MemoryBackendFactory

logger = logging.getLogger(__name__)


class ThinkingCallbackHandler(BaseCallbackHandler):
    """思考过程回调处理器 - 用于记录Agent的思考过程"""
    
    def __init__(self):
        """初始化回调处理器"""
        super().__init__()
        self.thoughts: List[str] = []
        self.actions: List[Dict[str, Any]] = []
        self.observations: List[str] = []
    
    def on_agent_action(self, action, **kwargs) -> Any:
        """当Agent执行动作时调用"""
        action_info = {
            'tool': action.tool,
            'tool_input': action.tool_input,
            'log': action.log
        }
        self.actions.append(action_info)
        logger.info(f"Agent执行动作: {action.tool} with input: {action.tool_input}")
    
    def on_agent_finish(self, finish, **kwargs) -> Any:
        """当Agent完成时调用"""
        logger.info(f"Agent完成: {finish.return_values}")
    
    def on_llm_start(self, serialized, prompts, **kwargs) -> Any:
        """当LLM开始生成时调用"""
        logger.debug(f"LLM开始生成: {prompts}")
    
    def on_llm_new_token(self, token, **kwargs) -> Any:
        """当LLM生成新token时调用"""
        pass
    
    def on_llm_end(self, response, **kwargs) -> Any:
        """当LLM结束时调用"""
        logger.debug(f"LLM生成结束")
    
    def on_llm_error(self, error, **kwargs) -> Any:
        """当LLM出错时调用"""
        logger.error(f"LLM错误: {error}")
    
    def on_tool_start(self, serialized, input_str, **kwargs) -> Any:
        """当工具开始执行时调用"""
        logger.info(f"工具开始执行: {serialized.get('name', 'unknown')}")
    
    def on_tool_end(self, output, **kwargs) -> Any:
        """当工具执行结束时调用"""
        logger.info(f"工具执行结束")
    
    def on_tool_error(self, error, **kwargs) -> Any:
        """当工具出错时调用"""
        logger.error(f"工具错误: {error}")
    
    def get_thoughts(self) -> List[str]:
        """获取思考过程"""
        return self.thoughts
    
    def get_actions(self) -> List[Dict[str, Any]]:
        """获取动作列表"""
        return self.actions
    
    def get_observations(self) -> List[str]:
        """获取观察列表"""
        return self.observations


class DeepThinker:
    """深度思考器 - 提供深度思考能力"""
    
    def __init__(self, skill_manager: SkillManager):
        """
        初始化深度思考器
        
        Args:
            skill_manager: 技能管理器
        """
        self.skill_manager = skill_manager
    
    async def think(
        self,
        question: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        深度思考
        
        Args:
            question: 问题
            context: 上下文
        
        Returns:
            Dict[str, Any]: 思考结果
        """
        context = context or {}
        
        # 使用推理技能
        reasoning_result = await self.skill_manager.execute_skill(
            'reasoning',
            question,
            context
        )
        
        # 使用规划技能
        planning_result = await self.skill_manager.execute_skill(
            'planning',
            question,
            context
        )
        
        # 组合思考结果
        thinking_result = {
            'reasoning': reasoning_result.output if reasoning_result.success else None,
            'planning': planning_result.output if planning_result.success else None,
            'reasoning_time': reasoning_result.execution_time,
            'planning_time': planning_result.execution_time
        }
        
        return thinking_result
    
    def think_sync(
        self,
        question: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        同步深度思考
        
        Args:
            question: 问题
            context: 上下文
        
        Returns:
            Dict[str, Any]: 思考结果
        """
        return asyncio.run(self.think(question, context))


class AgentBuilder:
    """Agent构建器 - 用于构建LangChain Agent"""
    
    def __init__(self, config: AgentSystemConfig):
        """
        初始化Agent构建器
        
        Args:
            config: Agent系统配置
        """
        self.config = config
        self.llm_provider: Optional[BaseLLMProvider] = None
        self.tool_manager: Optional[ToolManager] = None
        self.skill_manager: Optional[SkillManager] = None
        self.memory_manager: Optional[MemoryManager] = None
        self.thinker: Optional[DeepThinker] = None
        self.personal_rules_manager: Optional[PersonalRulesManager] = None
    
    def build_llm_provider(self) -> BaseLLMProvider:
        """
        构建LLM提供者
        
        Returns:
            BaseLLMProvider: LLM提供者实例
        """
        self.llm_provider = LLMProviderFactory.create_provider(self.config.llm)
        logger.info(f"LLM提供者已创建: {self.config.llm.provider}")
        return self.llm_provider
    
    def build_tool_manager(self) -> ToolManager:
        """
        构建工具管理器
        
        Returns:
            ToolManager: 工具管理器实例
        """
        self.tool_manager = ToolManager(auto_discover=False)
        
        # 根据配置注册工具
        for tool_config in self.config.tools:
            if tool_config.enabled:
                # 这里可以动态加载工具
                # 简化实现，实际应用中需要更复杂的工具加载逻辑
                pass
        
        logger.info(f"工具管理器已创建")
        return self.tool_manager
    
    def build_skill_manager(self) -> SkillManager:
        """
        构建技能管理器
        
        Returns:
            SkillManager: 技能管理器实例
        """
        self.skill_manager = SkillManager()
        
        # 根据配置启用/禁用技能
        for skill_config in self.config.skills:
            if skill_config.enabled:
                self.skill_manager.enable_skill(skill_config.name)
            else:
                self.skill_manager.disable_skill(skill_config.name)
        
        logger.info(f"技能管理器已创建")
        return self.skill_manager
    
    def build_memory_manager(self) -> MemoryManager:
        """
        构建记忆管理器
        
        Returns:
            MemoryManager: 记忆管理器实例
        """
        backend = MemoryBackendFactory.create_backend(
            self.config.memory.backend.value,
            self.config.memory.dict()
        )
        
        self.memory_manager = MemoryManager(backend)
        
        # 设置摘要配置
        if self.config.memory.enable_summarization:
            self.memory_manager.set_summarization(
                enabled=True,
                threshold=self.config.memory.summarization_threshold
            )
        
        logger.info(f"记忆管理器已创建: {self.config.memory.backend}")
        return self.memory_manager
    
    def build_thinker(self) -> DeepThinker:
        """
        构建深度思考器
        
        Returns:
            DeepThinker: 深度思考器实例
        """
        if not self.skill_manager:
            self.build_skill_manager()
        
        self.thinker = DeepThinker(self.skill_manager)
        logger.info("深度思考器已创建")
        return self.thinker
    
    def build_personal_rules_manager(
        self,
        storage_path: Optional[str] = None
    ) -> PersonalRulesManager:
        """
        构建个人规则管理器
        
        Args:
            storage_path: 规则存储路径
        
        Returns:
            PersonalRulesManager: 个人规则管理器实例
        """
        self.personal_rules_manager = PersonalRulesManager(storage_path)
        logger.info("个人规则管理器已创建")
        return self.personal_rules_manager
    
    def build_agent(self) -> 'LangChainAgent':
        """
        构建完整的Agent
        
        Returns:
            LangChainAgent: Agent实例
        """
        # 构建所有组件
        if not self.llm_provider:
            self.build_llm_provider()
        if not self.tool_manager:
            self.build_tool_manager()
        if not self.skill_manager:
            self.build_skill_manager()
        if not self.memory_manager:
            self.build_memory_manager()
        if not self.thinker:
            self.build_thinker()
        if not self.personal_rules_manager:
            self.build_personal_rules_manager()
        
        # 创建Agent实例
        agent = LangChainAgent(
            config=self.config,
            llm_provider=self.llm_provider,
            tool_manager=self.tool_manager,
            skill_manager=self.skill_manager,
            memory_manager=self.memory_manager,
            thinker=self.thinker,
            personal_rules_manager=self.personal_rules_manager
        )
        
        logger.info("Agent构建完成")
        return agent


class LangChainAgent:
    """LangChain Agent - 核心Agent类"""
    
    def __init__(
        self,
        config: AgentSystemConfig,
        llm_provider: BaseLLMProvider,
        tool_manager: ToolManager,
        skill_manager: SkillManager,
        memory_manager: MemoryManager,
        thinker: DeepThinker,
        personal_rules_manager: PersonalRulesManager
    ):
        """
        初始化Agent
        
        Args:
            config: Agent系统配置
            llm_provider: LLM提供者
            tool_manager: 工具管理器
            skill_manager: 技能管理器
            memory_manager: 记忆管理器
            thinker: 深度思考器
            personal_rules_manager: 个人规则管理器
        """
        self.config = config
        self.llm_provider = llm_provider
        self.tool_manager = tool_manager
        self.skill_manager = skill_manager
        self.memory_manager = memory_manager
        self.thinker = thinker
        self.personal_rules_manager = personal_rules_manager
        
        # 当前会话ID
        self.current_session_id: str = "default"
        
        # 回调处理器
        self.callback_handler = ThinkingCallbackHandler()
        
        # LangChain Agent执行器
        self._agent_executor: Optional[AgentExecutor] = None
        
        # 初始化Agent
        self._initialize_agent()
    
    def _initialize_agent(self) -> None:
        """初始化LangChain Agent"""
        # 获取LLM实例
        llm = self.llm_provider.get_llm()
        
        # 获取工具列表
        tools = self.tool_manager.get_all_tools()
        
        # 创建系统提示词
        system_prompt = self._build_system_prompt()
        
        # 根据配置创建不同类型的Agent
        agent_type = self.config.agent.type
        
        if agent_type == ConfigAgentType.REACT:
            self._create_react_agent(llm, tools, system_prompt)
        elif agent_type == ConfigAgentType.STRUCTURED_CHAT:
            self._create_structured_chat_agent(llm, tools, system_prompt)
        elif agent_type == ConfigAgentType.CONVERSATIONAL:
            self._create_conversational_agent(llm, tools, system_prompt)
        else:
            self._create_react_agent(llm, tools, system_prompt)
    
    def _build_system_prompt(self) -> str:
        """
        构建系统提示词
        
        Returns:
            str: 系统提示词
        """
        prompt_parts = []
        
        # 角色设定
        prompt_parts.append(f"角色: {self.config.system_prompt.persona}")
        
        # 个人规则
        personal_rules_prompt = self.personal_rules_manager.to_prompt()
        if personal_rules_prompt:
            prompt_parts.append(f"\n{personal_rules_prompt}")
        
        # 规则
        if self.config.system_prompt.rules:
            prompt_parts.append("\n系统规则:")
            for rule in self.config.system_prompt.rules:
                prompt_parts.append(f"- {rule}")
        
        # 约束
        if self.config.system_prompt.constraints:
            prompt_parts.append("\n约束:")
            for constraint in self.config.system_prompt.constraints:
                prompt_parts.append(f"- {constraint}")
        
        # 能力
        if self.config.system_prompt.capabilities:
            prompt_parts.append("\n能力:")
            for capability in self.config.system_prompt.capabilities:
                prompt_parts.append(f"- {capability}")
        
        # 自定义指令
        if self.config.system_prompt.custom_instructions:
            prompt_parts.append(f"\n{self.config.system_prompt.custom_instructions}")
        
        return "\n".join(prompt_parts)
    
    def _create_react_agent(
        self,
        llm,
        tools: List,
        system_prompt: str
    ) -> None:
        """创建ReAct Agent"""
        # ReAct提示词模板
        template = f"""{system_prompt}

你有以下工具可用:
{{tools}}

使用以下格式:

Question: 输入的问题
Thought: 你应该思考做什么
Action: 要采取的动作，应该是 [{{tool_names}}] 中的一个
Action Input: 动作的输入
Observation: 动作执行的结果
... (这个 Thought/Action/Action Input/Observation 可以重复N次)
Thought: 我现在知道最终答案了
Final Answer: 对原始输入问题的最终答案

开始!

Question: {{input}}
Thought: {{agent_scratchpad}}"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
        
        # 创建Agent
        agent = create_react_agent(llm, tools, prompt)
        
        # 创建Agent执行器
        self._agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=self.config.agent.verbose,
            max_iterations=self.config.agent.max_iterations,
            early_stopping_method=self.config.agent.early_stopping_method,
            handle_parsing_errors=self.config.agent.handle_parsing_errors,
            return_intermediate_steps=self.config.agent.return_intermediate_steps,
            callbacks=[self.callback_handler]
        )
    
    def _create_structured_chat_agent(
        self,
        llm,
        tools: List,
        system_prompt: str
    ) -> None:
        """创建结构化聊天Agent"""
        from langchain.agents import create_structured_chat_agent
        
        # 结构化聊天提示词模板
        template = f"""{system_prompt}

你有以下工具可用:
{{tools}}

使用以下格式:

Question: 输入的问题
Thought: 你应该思考做什么
Action: 要采取的动作，应该是 [{{tool_names}}] 中的一个
Action Input: 动作的输入
Observation: 动作执行的结果
... (这个 Thought/Action/Action Input/Observation 可以重复N次)
Thought: 我现在知道最终答案了
Final Answer: 对原始输入问题的最终答案

开始!

Question: {{input}}
Thought: {{agent_scratchpad}}"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
        
        # 创建Agent
        agent = create_structured_chat_agent(llm, tools, prompt)
        
        # 创建Agent执行器
        self._agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=self.config.agent.verbose,
            max_iterations=self.config.agent.max_iterations,
            early_stopping_method=self.config.agent.early_stopping_method,
            handle_parsing_errors=self.config.agent.handle_parsing_errors,
            return_intermediate_steps=self.config.agent.return_intermediate_steps,
            callbacks=[self.callback_handler]
        )
    
    def _create_conversational_agent(
        self,
        llm,
        tools: List,
        system_prompt: str
    ) -> None:
        """创建对话式Agent"""
        # 使用initialize_agent创建对话式Agent
        self._agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=self.config.agent.verbose,
            max_iterations=self.config.agent.max_iterations,
            early_stopping_method=self.config.agent.early_stopping_method,
            handle_parsing_errors=self.config.agent.handle_parsing_errors,
            return_intermediate_steps=self.config.agent.return_intermediate_steps,
            callbacks=[self.callback_handler]
        )
    
    def set_session_id(self, session_id: str) -> None:
        """
        设置当前会话ID
        
        Args:
            session_id: 会话ID
        """
        self.current_session_id = session_id
    
    async def query(self, question: str, enable_deep_think: bool = True) -> Dict[str, Any]:
        """
        查询Agent
        
        Args:
            question: 问题
            enable_deep_think: 是否启用深度思考
        
        Returns:
            Dict[str, Any]: 查询结果
        """
        result = {
            'question': question,
            'answer': None,
            'thinking': None,
            'actions': [],
            'error': None
        }
        
        try:
            # 保存用户消息到记忆
            self.memory_manager.add_message(
                self.current_session_id,
                'user',
                question
            )
            
            # 深度思考
            if enable_deep_think:
                thinking_result = await self.thinker.think(question)
                result['thinking'] = thinking_result
            
            # 执行Agent
            response = await self._agent_executor.ainvoke({"input": question})
            
            result['answer'] = response.get('output', '')
            result['actions'] = self.callback_handler.get_actions()
            
            # 保存助手消息到记忆
            self.memory_manager.add_message(
                self.current_session_id,
                'assistant',
                result['answer']
            )
            
            # 检查是否需要生成摘要
            if self.memory_manager.should_summarize(self.current_session_id):
                # 这里可以添加摘要生成逻辑
                pass
        
        except Exception as e:
            logger.error(f"Agent查询失败: {e}")
            result['error'] = str(e)
        
        return result
    
    def query_sync(self, question: str, enable_deep_think: bool = True) -> Dict[str, Any]:
        """
        同步查询Agent
        
        Args:
            question: 问题
            enable_deep_think: 是否启用深度思考
        
        Returns:
            Dict[str, Any]: 查询结果
        """
        return asyncio.run(self.query(question, enable_deep_think))
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[str]:
        """
        获取对话历史
        
        Args:
            limit: 消息数量限制
        
        Returns:
            List[str]: 对话历史
        """
        messages = self.memory_manager.get_messages(self.current_session_id, limit)
        return [f"{msg.role}: {msg.content}" for msg in messages]
    
    def clear_conversation(self) -> None:
        """清除对话历史"""
        self.memory_manager.clear_session(self.current_session_id)
        logger.info(f"会话已清除: {self.current_session_id}")
    
    def get_available_tools(self) -> List[str]:
        """
        获取可用工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        return self.tool_manager.list_tools()
    
    def get_available_skills(self) -> List[str]:
        """
        获取可用技能列表
        
        Returns:
            List[str]: 技能名称列表
        """
        return self.skill_manager.list_skills()
    
    def enable_tool(self, tool_name: str) -> bool:
        """
        启用工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            bool: 是否成功
        """
        return self.tool_manager.enable_tool(tool_name)
    
    def disable_tool(self, tool_name: str) -> bool:
        """
        禁用工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            bool: 是否成功
        """
        return self.tool_manager.disable_tool(tool_name)
    
    def enable_skill(self, skill_name: str) -> bool:
        """
        启用技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            bool: 是否成功
        """
        return self.skill_manager.enable_skill(skill_name)
    
    def disable_skill(self, skill_name: str) -> bool:
        """
        禁用技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            bool: 是否成功
        """
        return self.skill_manager.disable_skill(skill_name)
    
    # 个人规则管理方法
    
    def create_rule_set(
        self,
        name: str,
        description: str = ""
    ):
        """
        创建规则集
        
        Args:
            name: 规则集名称
            description: 规则集描述
        """
        return self.personal_rules_manager.create_rule_set(name, description)
    
    def list_rule_sets(self) -> List[str]:
        """
        列出所有规则集
        
        Returns:
            List[str]: 规则集名称列表
        """
        return self.personal_rules_manager.list_rule_sets()
    
    def delete_rule_set(self, name: str) -> bool:
        """
        删除规则集
        
        Args:
            name: 规则集名称
        
        Returns:
            bool: 是否成功删除
        """
        return self.personal_rules_manager.delete_rule_set(name)
    
    def add_personal_rule(
        self,
        rule_set_name: str,
        rule_id: str,
        name: str,
        description: str,
        category: str = "custom",
        priority: str = "medium",
        tags: List[str] = None,
        examples: List[str] = None
    ) -> None:
        """
        添加个人规则
        
        Args:
            rule_set_name: 规则集名称
            rule_id: 规则ID
            name: 规则名称
            description: 规则描述
            category: 规则分类
            priority: 规则优先级
            tags: 规则标签
            examples: 规则示例
        """
        from ..core.personal_rules import PersonalRule, RuleCategory, RulePriority
        
        rule = PersonalRule(
            id=rule_id,
            name=name,
            description=description,
            category=RuleCategory(category),
            priority=RulePriority(priority),
            tags=tags or [],
            examples=examples or []
        )
        
        self.personal_rules_manager.add_rule(rule_set_name, rule)
    
    def remove_personal_rule(
        self,
        rule_set_name: str,
        rule_id: str
    ) -> bool:
        """
        移除个人规则
        
        Args:
            rule_set_name: 规则集名称
            rule_id: 规则ID
        
        Returns:
            bool: 是否成功移除
        """
        return self.personal_rules_manager.remove_rule(rule_set_name, rule_id)
    
    def enable_personal_rule(
        self,
        rule_set_name: str,
        rule_id: str
    ) -> bool:
        """
        启用个人规则
        
        Args:
            rule_set_name: 规则集名称
            rule_id: 规则ID
        
        Returns:
            bool: 是否成功启用
        """
        return self.personal_rules_manager.enable_rule(rule_set_name, rule_id)
    
    def disable_personal_rule(
        self,
        rule_set_name: str,
        rule_id: str
    ) -> bool:
        """
        禁用个人规则
        
        Args:
            rule_set_name: 规则集名称
            rule_id: 规则ID
        
        Returns:
            bool: 是否成功禁用
        """
        return self.personal_rules_manager.disable_rule(rule_set_name, rule_id)
    
    def list_personal_rules(
        self,
        rule_set_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        列出个人规则
        
        Args:
            rule_set_name: 规则集名称（可选，不指定则列出所有）
        
        Returns:
            List[Dict[str, Any]]: 规则列表
        """
        if rule_set_name:
            rule_set = self.personal_rules_manager.get_rule_set(rule_set_name)
            if not rule_set:
                return []
            return [rule.dict() for rule in rule_set.rules]
        else:
            return [rule.dict() for rule in self.personal_rules_manager.get_all_enabled_rules()]
    
    def search_personal_rules(
        self,
        keyword: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索个人规则
        
        Args:
            keyword: 搜索关键词
            category: 规则分类（可选）
        
        Returns:
            List[Dict[str, Any]]: 匹配的规则列表
        """
        from ..core.personal_rules import RuleCategory
        
        category_enum = RuleCategory(category) if category else None
        rules = self.personal_rules_manager.search_rules(keyword, category_enum)
        
        return [rule.dict() for rule in rules]
    
    def get_personal_rules_prompt(self) -> str:
        """
        获取个人规则的提示词格式
        
        Returns:
            str: 提示词格式的规则
        """
        return self.personal_rules_manager.to_prompt()
    
    def import_personal_rules(self, rules_data: Dict[str, Any]) -> None:
        """
        导入个人规则
        
        Args:
            rules_data: 规则数据
        """
        self.personal_rules_manager.import_rules(rules_data)
    
    def export_personal_rules(self) -> Dict[str, Any]:
        """
        导出个人规则
        
        Returns:
            Dict[str, Any]: 规则数据
        """
        return self.personal_rules_manager.export_rules()
