# LangChain Agent Demo - AI执行流程详解

## 目录
1. [系统架构概述](#系统架构概述)
2. [核心组件介绍](#核心组件介绍)
3. [初始化流程](#初始化流程)
4. [查询处理流程](#查询处理流程)
5. [工具调用流程](#工具调用流程)
6. [深度思考流程](#深度思考流程)
7. [记忆管理流程](#记忆管理流程)
8. [个人规则应用流程](#个人规则应用流程)
9. [技能执行流程](#技能执行流程)
10. [完整执行流程示例](#完整执行流程示例)

---

## 系统架构概述

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户请求                                 │
│                    (User Query/Message)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangChainAgent                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    核心协调器                              │  │
│  │  - 接收用户查询                                           │  │
│  │  - 协调各组件工作                                         │  │
│  │  - 管理执行流程                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │LLM Provider │  │Tool Manager │  │Skill Manager│            │
│  │  (LLM提供者)│  │ (工具管理器)│  │ (技能管理器)│            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │Memory Manager│ │DeepThinker │  │PersonalRules│            │
│  │ (记忆管理器) │ │(深度思考器) │  │  (个人规则) │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangChain AgentExecutor                      │
│  - 执行Agent逻辑                                                 │
│  - 管理工具调用                                                  │
│  - 处理LLM交互                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         LLM服务                                  │
│              (OpenAI/Anthropic/Azure/Ollama等)                  │
└─────────────────────────────────────────────────────────────────┘
```

### 设计理念

本系统采用**模块化、可配置、可扩展**的设计理念：

1. **模块化**：每个组件职责单一，独立开发测试
2. **可配置**：通过YAML配置文件灵活配置各组件
3. **可扩展**：支持动态添加工具、技能、LLM提供者
4. **分层架构**：配置层 → 核心层 → 执行层 → 存储层

---

## 核心组件介绍

### 1. ConfigManager（配置管理器）

**职责**：
- 加载和管理YAML配置文件
- 支持多环境配置（dev/staging/prod）
- 配置验证和默认值处理

**关键属性**：
```python
class AgentSystemConfig:
    agent: AgentConfig          # Agent配置
    llm: LLMConfig             # LLM配置
    memory: MemoryConfig       # 记忆配置
    tools: List[ToolConfig]    # 工具配置列表
    skills: List[SkillConfig]  # 技能配置列表
    system_prompt: SystemPromptConfig  # 系统提示词配置
```

### 2. LLMProvider（LLM提供者）

**职责**：
- 抽象不同LLM提供商的接口
- 支持OpenAI、Anthropic、Azure、Ollama等
- 提供统一的调用接口和错误处理

**关键方法**：
```python
class BaseLLMProvider:
    def create_llm() -> BaseChatModel  # 创建LLM实例
    def get_llm() -> BaseChatModel     # 获取LLM实例（懒加载）
    def invoke(messages) -> str        # 同步调用
    async def ainvoke(messages) -> str # 异步调用
```

### 3. ToolManager（工具管理器）

**职责**：
- 注册和管理工具
- 工具版本控制和访问控制
- 工具自动发现和加载

**关键方法**：
```python
class ToolManager:
    def register_tool(tool, metadata)     # 注册工具
    def get_tool(name) -> BaseTool       # 获取工具
    def get_all_tools() -> List[BaseTool] # 获取所有工具
    def enable_tool(name)                # 启用工具
    def disable_tool(name)               # 禁用工具
```

### 4. SkillManager（技能管理器）

**职责**：
- 管理各种技能（推理、规划、分析等）
- 技能执行和结果处理
- 技能依赖管理

**关键方法**：
```python
class SkillManager:
    def register_skill(skill)              # 注册技能
    def execute_skill(name, input, context) # 执行技能
    def enable_skill(name)                 # 启用技能
    def disable_skill(name)                # 禁用技能
```

### 5. MemoryManager（记忆管理器）

**职责**：
- 管理对话历史和上下文
- 支持多种存储后端（内存、Redis、SQLite等）
- 对话摘要和记忆清理

**关键方法**：
```python
class MemoryManager:
    def add_message(session_id, message)   # 添加消息
    def get_messages(session_id) -> List   # 获取历史消息
    def clear_session(session_id)          # 清除会话
    def summarize_session(session_id)      # 摘要会话
```

### 6. DeepThinker（深度思考器）

**职责**：
- 提供深度推理能力
- 执行规划技能
- 组合多个技能的结果

**关键方法**：
```python
class DeepThinker:
    async def think(question, context) -> Dict  # 深度思考
    def think_sync(question, context) -> Dict   # 同步思考
```

### 7. PersonalRulesManager（个人规则管理器）

**职责**：
- 管理用户的个人规则
- 规则分类和优先级管理
- 生成规则提示词

**关键方法**：
```python
class PersonalRulesManager:
    def add_rule(rule)                    # 添加规则
    def create_rule_set(name, desc)       # 创建规则集
    def to_prompt() -> str                # 生成提示词
    def activate_rule_set(name)           # 激活规则集
```

---

## 初始化流程

### 完整初始化流程图

```
开始
  │
  ├─→ 1. 加载配置文件
  │     ├─ 读取 config/default.yaml
  │     ├─ 解析配置内容
  │     └─ 验证配置有效性
  │
  ├─→ 2. 创建AgentBuilder
  │     └─ 初始化构建器
  │
  ├─→ 3. 构建LLM提供者
  │     ├─ 根据配置创建对应的Provider
  │     │   ├─ OpenAIProvider
  │     │   ├─ AnthropicProvider
  │     │   ├─ AzureProvider
  │     │   └─ OllamaProvider
  │     └─ 设置备用提供者（fallback）
  │
  ├─→ 4. 构建工具管理器
  │     ├─ 创建ToolManager实例
  │     ├─ 根据配置注册工具
  │     └─ 设置工具访问控制
  │
  ├─→ 5. 构建技能管理器
  │     ├─ 创建SkillManager实例
  │     ├─ 注册内置技能
  │     │   ├─ ReasoningSkill（推理）
  │     │   ├─ PlanningSkill（规划）
  │     │   ├─ AnalysisSkill（分析）
  │     │   └─ CreativitySkill（创造）
  │     └─ 根据配置启用/禁用技能
  │
  ├─→ 6. 构建记忆管理器
  │     ├─ 根据配置选择存储后端
  │     │   ├─ InMemoryBackend
  │     │   ├─ RedisBackend
  │     │   ├─ SQLiteBackend
  │     │   └─ PostgreSQLBackend
  │     └─ 配置摘要功能
  │
  ├─→ 7. 构建深度思考器
  │     └─ 注入SkillManager
  │
  ├─→ 8. 构建个人规则管理器
  │     ├─ 创建PersonalRulesManager实例
  │     └─ 加载已保存的规则
  │
  ├─→ 9. 创建LangChainAgent实例
  │     ├─ 注入所有组件
  │     ├─ 初始化AgentExecutor
  │     │   ├─ 选择Agent类型（ReAct/Conversational/Structured）
  │     │   ├─ 构建系统提示词
  │     │   ├─ 创建Prompt模板
  │     │   └─ 创建AgentExecutor
  │     └─ 设置回调处理器
  │
  └─→ 10. 返回Agent实例
        │
        └─→ 初始化完成，等待用户查询
```

### 初始化代码详解

#### 步骤1：加载配置

```python
# main.py
config_manager = ConfigManager(config_dir=str(project_root / "config"))
config = config_manager.load_config("default", "dev")
```

**流程说明**：
1. 创建ConfigManager实例，指定配置文件目录
2. 调用`load_config("default", "dev")`加载配置
3. 内部流程：
   - 读取`default.yaml`基础配置
   - 如果存在`default.dev.yaml`，合并环境特定配置
   - 使用Pydantic验证配置有效性
   - 返回AgentSystemConfig对象

#### 步骤2-8：构建各组件

```python
# agents/agent.py - AgentBuilder类
builder = AgentBuilder(config)

# 按顺序构建各组件
builder.build_llm_provider()        # 步骤3
builder.build_tool_manager()        # 步骤4
builder.build_skill_manager()       # 步骤5
builder.build_memory_manager()      # 步骤6
builder.build_thinker()             # 步骤7
builder.build_personal_rules_manager()  # 步骤8
```

**关键点**：
- **依赖注入**：各组件通过构造函数注入依赖
- **懒加载**：LLM实例在首次使用时才创建
- **配置驱动**：所有组件行为由配置文件控制

#### 步骤9：创建Agent实例

```python
# agents/agent.py - AgentBuilder类
agent = builder.build_agent()
```

**内部流程**：
1. 创建LangChainAgent实例，注入所有组件
2. 调用`_initialize_agent()`初始化LangChain Agent：
   ```python
   def _initialize_agent(self):
       # 获取LLM实例
       llm = self.llm_provider.get_llm()
       
       # 获取所有工具
       tools = self.tool_manager.get_all_tools()
       
       # 构建系统提示词
       system_prompt = self._build_system_prompt()
       
       # 根据配置创建不同类型的Agent
       if agent_type == ConfigAgentType.REACT:
           self._create_react_agent(llm, tools, system_prompt)
       elif agent_type == ConfigAgentType.STRUCTURED_CHAT:
           self._create_structured_chat_agent(llm, tools, system_prompt)
       # ...
   ```

3. 构建系统提示词：
   ```python
   def _build_system_prompt(self):
       prompt_parts = []
       
       # 添加角色设定
       prompt_parts.append(f"角色: {self.config.system_prompt.persona}")
       
       # 添加个人规则
       personal_rules_prompt = self.personal_rules_manager.to_prompt()
       if personal_rules_prompt:
           prompt_parts.append(f"\n{personal_rules_prompt}")
       
       # 添加系统规则
       if self.config.system_prompt.rules:
           prompt_parts.append("\n系统规则:")
           for rule in self.config.system_prompt.rules:
               prompt_parts.append(f"- {rule}")
       
       # ... 添加约束、能力等
       
       return "\n".join(prompt_parts)
   ```

---

## 查询处理流程

### 查询处理流程图

```
用户查询
  │
  ├─→ 1. 接收查询
  │     └─ agent.query(question, enable_deep_think=True)
  │
  ├─→ 2. 深度思考（可选）
  │     ├─ 判断是否启用深度思考
  │     │   ├─ 是 → 执行深度思考
  │     │   │   ├─ 推理技能（ReasoningSkill）
  │     │   │   └─ 规划技能（PlanningSkill）
  │     │   └─ 否 → 跳过
  │     └─ 返回思考结果
  │
  ├─→ 3. 加载对话历史
  │     ├─ 从MemoryManager获取历史消息
  │     ├─ 构建消息列表
  │     │   ├─ SystemMessage（系统提示词）
  │     │   ├─ 历史HumanMessage和AIMessage
  │     │   └─ 当前HumanMessage
  │     └─ 如果启用摘要，添加摘要信息
  │
  ├─→ 4. 调用AgentExecutor
  │     ├─ 将消息传递给AgentExecutor
  │     ├─ AgentExecutor执行Agent逻辑
  │     │   ├─ LLM分析问题
  │     │   ├─ 决定是否需要调用工具
  │     │   │   ├─ 需要工具 → 执行工具调用流程
  │     │   │   └─ 不需要 → 直接生成答案
  │     │   └─ 生成最终答案
  │     └─ 返回执行结果
  │
  ├─→ 5. 保存对话历史
  │     ├─ 保存用户消息到MemoryManager
  │     └─ 保存AI回复到MemoryManager
  │
  ├─→ 6. 构建返回结果
  │     ├─ answer: 最终答案
  │     ├─ thinking: 深度思考结果
  │     ├─ actions: 工具调用记录
  │     ├─ observations: 工具执行结果
  │     └─ error: 错误信息（如果有）
  │
  └─→ 7. 返回结果给用户
```

### 查询处理代码详解

#### 步骤1-2：接收查询和深度思考

```python
# agents/agent.py - LangChainAgent类
async def query(
    self,
    question: str,
    enable_deep_think: bool = True,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    异步查询
    
    Args:
        question: 用户问题
        enable_deep_think: 是否启用深度思考
        context: 上下文信息
    
    Returns:
        Dict: 查询结果
    """
    result = {
        'answer': '',
        'thinking': None,
        'actions': [],
        'observations': [],
        'error': None
    }
    
    try:
        # 步骤2：深度思考（可选）
        if enable_deep_think:
            thinking_result = await self.thinker.think(question, context)
            result['thinking'] = thinking_result
        
        # ... 继续后续步骤
```

**深度思考内部流程**：
```python
# agents/agent.py - DeepThinker类
async def think(self, question: str, context: Dict[str, Any] = None):
    context = context or {}
    
    # 执行推理技能
    reasoning_result = await self.skill_manager.execute_skill(
        'reasoning',
        question,
        context
    )
    
    # 执行规划技能
    planning_result = await self.skill_manager.execute_skill(
        'planning',
        question,
        context
    )
    
    # 组合思考结果
    return {
        'reasoning': reasoning_result.output,
        'planning': planning_result.output,
        'reasoning_time': reasoning_result.execution_time,
        'planning_time': planning_result.execution_time
    }
```

#### 步骤3：加载对话历史

```python
# agents/agent.py - LangChainAgent类
# 步骤3：加载对话历史
messages = []

# 添加系统消息
system_prompt = self._build_system_prompt()
messages.append(SystemMessage(content=system_prompt))

# 添加历史消息
history = self.memory_manager.get_messages(self.current_session_id)
for msg in history:
    if msg.role == 'user':
        messages.append(HumanMessage(content=msg.content))
    elif msg.role == 'assistant':
        messages.append(AIMessage(content=msg.content))

# 添加当前问题
messages.append(HumanMessage(content=question))
```

**MemoryManager内部流程**：
```python
# memory/memory_system.py - MemoryManager类
def get_messages(self, session_id: str, limit: Optional[int] = None):
    # 从存储后端获取消息
    messages = self.backend.get_messages(session_id, limit)
    
    # 如果启用摘要且消息数量超过阈值
    if self.enable_summarization and len(messages) > self.summarization_threshold:
        # 生成摘要
        summary = self._generate_summary(messages[:-self.summarization_threshold])
        # 只保留最近的消息
        messages = messages[-self.summarization_threshold:]
        # 添加摘要作为系统消息
        messages.insert(0, Message(
            role='system',
            content=f"对话摘要: {summary}"
        ))
    
    return messages
```

#### 步骤4：调用AgentExecutor

```python
# agents/agent.py - LangChainAgent类
# 步骤4：调用AgentExecutor
agent_output = await self._agent_executor.ainvoke(
    {'input': question, 'chat_history': messages},
    callbacks=[self.callback_handler]
)

# 提取答案
result['answer'] = agent_output.get('output', '')

# 提取工具调用记录
result['actions'] = self.callback_handler.get_actions()
result['observations'] = self.callback_handler.get_observations()
```

**AgentExecutor执行流程**：
```
AgentExecutor内部执行流程：

1. 接收输入（question + chat_history）
   │
   ├─→ 2. LLM分析输入
   │     ├─ 理解问题意图
   │     ├─ 检查是否需要工具
   │     └─ 生成思考过程（Thought）
   │
   ├─→ 3. 决策循环（ReAct模式）
   │     │
   │     ├─ Thought: 思考下一步动作
   │     │
   │     ├─ Action: 选择工具
   │     │   └─ 例如: calculator, search, time
   │     │
   │     ├─ Action Input: 工具输入参数
   │     │   └─ 例如: {"expression": "123 * 456"}
   │     │
   │     ├─ Observation: 工具执行结果
   │     │   └─ 例如: "计算结果: 56088"
   │     │
   │     └─ 判断是否完成
   │         ├─ 未完成 → 继续循环
   │         └─ 完成 → 生成Final Answer
   │
   └─→ 4. 返回最终答案
```

#### 步骤5：保存对话历史

```python
# agents/agent.py - LangChainAgent类
# 步骤5：保存对话历史
self.memory_manager.add_message(
    self.current_session_id,
    Message(role='user', content=question)
)

self.memory_manager.add_message(
    self.current_session_id,
    Message(role='assistant', content=result['answer'])
)
```

#### 步骤6-7：构建和返回结果

```python
# agents/agent.py - LangChainAgent类
# 步骤6：构建返回结果
return {
    'answer': result['answer'],
    'thinking': result['thinking'],
    'actions': result['actions'],
    'observations': result['observations'],
    'error': result['error']
}
```

---

## 工具调用流程

### 工具调用流程图

```
LLM决策需要使用工具
  │
  ├─→ 1. LLM生成工具调用指令
  │     ├─ Thought: 思考过程
  │     ├─ Action: 工具名称
  │     └─ Action Input: 工具输入参数
  │
  ├─→ 2. AgentExecutor解析工具调用
  │     ├─ 提取工具名称
  │     ├─ 提取输入参数
  │     └─ 验证参数格式
  │
  ├─→ 3. 从ToolManager获取工具
  │     ├─ 根据工具名称查找
  │     ├─ 检查工具是否启用
  │     └─ 检查访问权限
  │
  ├─→ 4. 执行工具
  │     ├─ 参数验证（使用Pydantic模型）
  │     ├─ 调用工具的_run方法
  │     │   └─ 例如: calculator._run(expression="123*456")
  │     ├─ 工具内部处理
  │     │   ├─ 解析输入
  │     │   ├─ 执行核心逻辑
  │     │   └─ 格式化输出
  │     └─ 返回执行结果
  │
  ├─→ 5. 生成Observation
  │     ├─ 记录工具执行结果
  │     └─ 添加到回调处理器
  │
  ├─→ 6. LLM继续处理
  │     ├─ 接收Observation
  │     ├─ 判断是否需要更多工具
  │     │   ├─ 需要 → 返回步骤1
  │     │   └─ 不需要 → 生成Final Answer
  │     └─ 生成最终答案
  │
  └─→ 7. 返回结果
```

### 工具调用代码详解

#### 步骤1-2：LLM生成和解析工具调用

```python
# LangChain内部处理（简化说明）
# LLM生成的输出示例：
"""
Thought: 用户想要计算数学表达式，我应该使用calculator工具
Action: calculator
Action Input: {"expression": "123 * 456 + 789"}
"""

# AgentExecutor解析
action = {
    'tool': 'calculator',
    'tool_input': {"expression": "123 * 456 + 789"},
    'log': 'Thought: 用户想要计算数学表达式...'
}
```

#### 步骤3：从ToolManager获取工具

```python
# tools/manager.py - ToolManager类
def get_tool(self, name: str) -> BaseTool:
    """获取工具"""
    if name not in self._tools:
        raise ValueError(f"工具 '{name}' 不存在")
    
    tool_wrapper = self._tools[name]
    
    # 检查工具是否启用
    if not tool_wrapper.metadata.enabled:
        raise ValueError(f"工具 '{name}' 已禁用")
    
    # 检查访问权限
    if tool_wrapper.metadata.requires_auth:
        # 验证用户权限
        # ...
    
    return tool_wrapper.tool
```

#### 步骤4：执行工具

```python
# tools/manager.py - ToolWrapper类
# 工具执行流程

# 1. 参数验证
# 使用Pydantic模型验证输入参数
input_model = tool.args_schema  # 例如: CalculatorInput
validated_input = input_model(**action_input)

# 2. 调用工具的_run方法
result = tool._run(**validated_input.dict())

# 示例：CalculatorTool
class CalculatorTool(BaseTool):
    name = "calculator"
    description = "计算数学表达式"
    args_schema = CalculatorInput
    
    def _run(self, expression: str) -> str:
        """
        执行计算
        
        Args:
            expression: 数学表达式，如 "123 * 456"
        
        Returns:
            str: 计算结果
        """
        try:
            # 安全计算表达式
            result = eval(expression, {"__builtins__": {}}, {})
            return f"计算结果: {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"
```

#### 步骤5-7：生成Observation和继续处理

```python
# agents/agent.py - ThinkingCallbackHandler类
def on_tool_end(self, output, **kwargs):
    """当工具执行结束时调用"""
    self.observations.append(output)
    logger.info(f"工具执行结果: {output}")

# AgentExecutor继续处理
# 将Observation添加到提示词中，让LLM继续思考
"""
Observation: 计算结果: 56088
Thought: 我已经得到了计算结果，现在可以回答用户的问题了
Final Answer: 123 * 456 + 789 = 56877
"""
```

### 工具调用示例

**示例1：计算器工具**

```
用户查询: "计算 123 * 456 + 789"

执行流程：
1. LLM分析: 需要使用calculator工具
2. 生成Action: calculator
3. 生成Action Input: {"expression": "123 * 456 + 789"}
4. 工具执行: 
   - 参数验证: expression是字符串，符合要求
   - 计算: eval("123 * 456 + 789") = 56877
   - 返回: "计算结果: 56877"
5. LLM生成答案: "123 * 456 + 789 = 56877"
```

**示例2：搜索工具**

```
用户查询: "搜索人工智能的最新发展"

执行流程：
1. LLM分析: 需要使用search工具
2. 生成Action: search
3. 生成Action Input: {"query": "人工智能最新发展"}
4. 工具执行:
   - 调用搜索API
   - 获取搜索结果
   - 返回: "搜索结果: 1. GPT-4发布... 2. Claude 3发布..."
5. LLM生成答案: "根据搜索结果，人工智能的最新发展包括..."
```

---

## 深度思考流程

### 深度思考流程图

```
启用深度思考
  │
  ├─→ 1. 执行推理技能（ReasoningSkill）
  │     │
  │     ├─ 输入: 用户问题 + 上下文
  │     │
  │     ├─ 推理过程:
  │     │   ├─ 分析问题结构
  │     │   ├─ 识别关键概念
  │     │   ├─ 建立逻辑关系
  │     │   └─ 生成推理链
  │     │
  │     └─ 输出: 推理结果
  │         └─ 例如: ["问题涉及...", "关键点是...", "推理步骤..."]
  │
  ├─→ 2. 执行规划技能（PlanningSkill）
  │     │
  │     ├─ 输入: 用户问题 + 推理结果
  │     │
  │     ├─ 规划过程:
  │     │   ├─ 确定目标
  │     │   ├─ 分解任务
  │     │   ├─ 制定步骤
  │     │   └─ 评估可行性
  │     │
  │     └─ 输出: 执行计划
  │         └─ 例如: [
  │               {"step": 1, "action": "收集信息", "description": "..."},
  │               {"step": 2, "action": "分析数据", "description": "..."},
  │               {"step": 3, "action": "生成答案", "description": "..."}
  │             ]
  │
  ├─→ 3. 组合思考结果
  │     ├─ 合并推理和规划结果
  │     ├─ 记录执行时间
  │     └─ 返回完整的思考结果
  │
  └─→ 4. 将思考结果注入到查询流程
        └─ 作为上下文传递给AgentExecutor
```

### 深度思考代码详解

#### 步骤1：执行推理技能

```python
# skills/skill_system.py - ReasoningSkill类
class ReasoningSkill(BaseSkill):
    """推理技能 - 提供深度推理能力"""
    
    async def execute(
        self,
        input_data: str,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        执行推理
        
        Args:
            input_data: 用户问题
            context: 上下文信息
        
        Returns:
            SkillResult: 推理结果
        """
        start_time = time.time()
        
        try:
            # 构建推理提示词
            reasoning_prompt = f"""
            请对以下问题进行深度推理分析：
            
            问题: {input_data}
            
            请按照以下步骤进行推理：
            1. 识别问题的关键要素
            2. 分析要素之间的关系
            3. 建立逻辑推理链
            4. 得出推理结论
            
            推理过程：
            """
            
            # 调用LLM进行推理
            # （实际实现中会调用LLM，这里简化）
            reasoning_steps = [
                "问题分析: 这是一个关于...的问题",
                "关键要素: 包含...等要素",
                "逻辑关系: ...与...存在...关系",
                "推理结论: 基于以上分析，可以得出..."
            ]
            
            execution_time = time.time() - start_time
            
            return SkillResult(
                success=True,
                output={'reasoning': reasoning_steps},
                execution_time=execution_time
            )
        
        except Exception as e:
            return SkillResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
```

#### 步骤2：执行规划技能

```python
# skills/skill_system.py - PlanningSkill类
class PlanningSkill(BaseSkill):
    """规划技能 - 提供任务规划能力"""
    
    async def execute(
        self,
        input_data: str,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        执行规划
        
        Args:
            input_data: 用户问题
            context: 上下文信息（包含推理结果）
        
        Returns:
            SkillResult: 规划结果
        """
        start_time = time.time()
        
        try:
            # 构建规划提示词
            planning_prompt = f"""
            基于以下推理结果，制定执行计划：
            
            问题: {input_data}
            推理结果: {context.get('reasoning', [])}
            
            请制定详细的执行计划，包括：
            1. 明确目标
            2. 分解任务
            3. 制定步骤
            4. 评估可行性
            """
            
            # 调用LLM进行规划
            # （实际实现中会调用LLM，这里简化）
            plan = [
                {
                    'step': 1,
                    'action': '收集信息',
                    'description': '收集相关的背景信息和数据'
                },
                {
                    'step': 2,
                    'action': '分析数据',
                    'description': '对收集的数据进行分析和处理'
                },
                {
                    'step': 3,
                    'action': '生成答案',
                    'description': '基于分析结果生成最终答案'
                }
            ]
            
            execution_time = time.time() - start_time
            
            return SkillResult(
                success=True,
                output=plan,
                execution_time=execution_time
            )
        
        except Exception as e:
            return SkillResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
```

#### 步骤3：组合思考结果

```python
# agents/agent.py - DeepThinker类
async def think(
    self,
    question: str,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """深度思考"""
    context = context or {}
    
    # 执行推理技能
    reasoning_result = await self.skill_manager.execute_skill(
        'reasoning',
        question,
        context
    )
    
    # 执行规划技能
    planning_result = await self.skill_manager.execute_skill(
        'planning',
        question,
        {**context, 'reasoning': reasoning_result.output}
    )
    
    # 组合思考结果
    thinking_result = {
        'reasoning': reasoning_result.output if reasoning_result.success else None,
        'planning': planning_result.output if planning_result.success else None,
        'reasoning_time': reasoning_result.execution_time,
        'planning_time': planning_result.execution_time
    }
    
    return thinking_result
```

### 深度思考示例

**示例：复杂问题分析**

```
用户问题: "如何设计一个高效的算法来解决旅行商问题？"

深度思考流程：

1. 推理技能执行:
   - 问题分析: 这是一个组合优化问题
   - 关键要素: 城市数量、距离矩阵、路径约束
   - 逻辑关系: 需要平衡效率和准确性
   - 推理结论: 可以采用近似算法或启发式算法

2. 规划技能执行:
   - 步骤1: 分析问题规模和约束条件
   - 步骤2: 选择合适的算法策略（贪心、模拟退火、遗传算法等）
   - 步骤3: 设计算法框架
   - 步骤4: 评估时间和空间复杂度
   - 步骤5: 提供优化建议

3. 思考结果注入:
   - 将推理和规划结果作为上下文
   - Agent根据思考结果生成详细答案
```

---

## 记忆管理流程

### 记忆管理流程图

```
对话开始
  │
  ├─→ 1. 创建/加载会话
  │     ├─ 检查会话ID是否存在
  │     ├─ 存在 → 加载历史消息
  │     └─ 不存在 → 创建新会话
  │
  ├─→ 2. 消息存储流程（每次对话）
  │     │
  │     ├─ 用户发送消息
  │     │   ├─ 创建Message对象
  │     │   │   ├─ role: 'user'
  │     │   │   ├─ content: 消息内容
  │     │   │   ├─ timestamp: 当前时间
  │     │   │   └─ metadata: 元数据
  │     │   └─ 调用MemoryManager.add_message()
  │     │
  │     ├─ AI回复消息
  │     │   ├─ 创建Message对象
  │     │   │   ├─ role: 'assistant'
  │     │   │   ├─ content: 回复内容
  │     │   │   ├─ timestamp: 当前时间
  │     │   │   └─ metadata: 元数据
  │     │   └─ 调用MemoryManager.add_message()
  │     │
  │     └─ 存储后端处理
  │         ├─ InMemoryBackend: 存储到内存字典
  │         ├─ RedisBackend: 存储到Redis
  │         ├─ SQLiteBackend: 存储到SQLite数据库
  │         └─ PostgreSQLBackend: 存储到PostgreSQL数据库
  │
  ├─→ 3. 消息检索流程
  │     │
  │     ├─ 调用MemoryManager.get_messages()
  │     │
  │     ├─ 从存储后端获取消息
  │     │   └─ 根据session_id查询
  │     │
  │     ├─ 检查是否需要摘要
  │     │   ├─ 消息数量 > 摘要阈值
  │     │   │   ├─ 生成摘要
  │     │   │   ├─ 保留最近N条消息
  │     │   │   └─ 添加摘要作为系统消息
  │     │   └─ 消息数量 <= 摘要阈值
  │     │       └─ 返回所有消息
  │     │
  │     └─ 返回消息列表
  │
  ├─→ 4. 会话管理
  │     ├─ 切换会话: set_session_id()
  │     ├─ 清除会话: clear_session()
  │     ├─ 删除会话: delete_session()
  │     └─ 获取所有会话: get_all_sessions()
  │
  └─→ 5. 对话摘要（可选）
        ├─ 触发条件: 消息数量超过阈值
        ├─ 摘要生成: 使用LLM生成摘要
        └─ 摘要存储: 保存到存储后端
```

### 记忆管理代码详解

#### 步骤1：创建/加载会话

```python
# agents/agent.py - LangChainAgent类
def set_session_id(self, session_id: str) -> None:
    """
    设置当前会话ID
    
    Args:
        session_id: 会话ID
    """
    self.current_session_id = session_id
    logger.info(f"切换到会话: {session_id}")
```

#### 步骤2：消息存储流程

```python
# memory/memory_system.py - MemoryManager类
class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, backend: BaseMemoryBackend):
        """
        初始化记忆管理器
        
        Args:
            backend: 存储后端
        """
        self.backend = backend
        self.enable_summarization = False
        self.summarization_threshold = 5
    
    def add_message(self, session_id: str, message: Message) -> None:
        """
        添加消息到记忆
        
        Args:
            session_id: 会话ID
            message: 消息对象
        """
        # 添加到存储后端
        self.backend.add_message(session_id, message)
        
        # 检查是否需要摘要
        messages = self.backend.get_messages(session_id)
        if self.enable_summarization and len(messages) > self.summarization_threshold:
            self._summarize_old_messages(session_id, messages)
        
        logger.debug(f"消息已添加到会话 {session_id}")
```

**存储后端实现示例**：

```python
# memory/memory_system.py - InMemoryBackend类
class InMemoryBackend(BaseMemoryBackend):
    """内存存储后端"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self._sessions: Dict[str, List[Message]] = {}
        self._summaries: Dict[str, ConversationSummary] = {}
    
    def add_message(self, session_id: str, message: Message) -> None:
        """添加消息到内存"""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        self._sessions[session_id].append(message)
        
        # 限制历史记录数量
        if len(self._sessions[session_id]) > self._max_history:
            # 保留最新的消息
            self._sessions[session_id] = self._sessions[session_id][-self._max_history:]
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """获取会话消息"""
        if session_id not in self._sessions:
            return []
        
        messages = self._sessions[session_id]
        
        if limit:
            return messages[-limit:]
        
        return messages
```

#### 步骤3：消息检索流程

```python
# memory/memory_system.py - MemoryManager类
def get_messages(
    self,
    session_id: str,
    limit: Optional[int] = None
) -> List[Message]:
    """
    获取会话消息
    
    Args:
        session_id: 会话ID
        limit: 消息数量限制
    
    Returns:
        List[Message]: 消息列表
    """
    messages = self.backend.get_messages(session_id, limit)
    
    # 如果有摘要，添加到消息列表开头
    if session_id in self.backend._summaries:
        summary = self.backend._summaries[session_id]
        summary_message = Message(
            role='system',
            content=f"之前的对话摘要: {summary.summary}",
            metadata={'type': 'summary'}
        )
        messages.insert(0, summary_message)
    
    return messages
```

#### 步骤4：会话管理

```python
# memory/memory_system.py - MemoryManager类
def clear_session(self, session_id: str) -> None:
    """清除会话记忆"""
    self.backend.clear_session(session_id)
    logger.info(f"会话 {session_id} 已清除")

def delete_session(self, session_id: str) -> bool:
    """删除会话"""
    result = self.backend.delete_session(session_id)
    if result:
        logger.info(f"会话 {session_id} 已删除")
    return result

def get_all_sessions(self) -> List[str]:
    """获取所有会话ID"""
    return self.backend.get_all_sessions()
```

#### 步骤5：对话摘要

```python
# memory/memory_system.py - MemoryManager类
def _summarize_old_messages(
    self,
    session_id: str,
    messages: List[Message]
) -> None:
    """
    摘要旧消息
    
    Args:
        session_id: 会话ID
        messages: 消息列表
    """
    # 获取需要摘要的消息（保留最近的N条）
    messages_to_summarize = messages[:-self.summarization_threshold]
    
    if not messages_to_summarize:
        return
    
    # 构建摘要提示词
    conversation_text = "\n".join([
        f"{msg.role}: {msg.content}"
        for msg in messages_to_summarize
    ])
    
    summary_prompt = f"""
    请总结以下对话的主要内容：
    
    {conversation_text}
    
    摘要：
    """
    
    # 调用LLM生成摘要
    # （实际实现中会调用LLM，这里简化）
    summary_text = "用户询问了...，AI回答了..."
    
    # 创建摘要对象
    summary = ConversationSummary(
        summary=summary_text,
        message_count=len(messages_to_summarize)
    )
    
    # 保存摘要
    self.backend._summaries[session_id] = summary
    
    # 删除已摘要的消息
    self.backend._sessions[session_id] = messages[-self.summarization_threshold:]
    
    logger.info(f"会话 {session_id} 已生成摘要")
```

### 记忆管理示例

**示例：多轮对话记忆**

```
会话ID: "user_123_session_1"

第1轮对话:
用户: "我叫小明"
AI: "你好小明！很高兴认识你。"
存储: [
  Message(role='user', content='我叫小明'),
  Message(role='assistant', content='你好小明！很高兴认识你。')
]

第2轮对话:
用户: "我的名字是什么？"
AI: "你叫小明。"
存储: [
  Message(role='user', content='我叫小明'),
  Message(role='assistant', content='你好小明！很高兴认识你。'),
  Message(role='user', content='我的名字是什么？'),
  Message(role='assistant', content='你叫小明。')
]

第3轮对话:
用户: "我喜欢编程和阅读"
AI: "编程和阅读都是很棒的爱好！..."
存储: [
  ...之前的消息...,
  Message(role='user', content='我喜欢编程和阅读'),
  Message(role='assistant', content='编程和阅读都是很棒的爱好！...')
]

检索历史:
get_messages("user_123_session_1") → 返回所有历史消息
AI可以根据历史上下文回答："你叫小明，你喜欢编程和阅读。"
```

---

## 个人规则应用流程

### 个人规则应用流程图

```
用户定义个人规则
  │
  ├─→ 1. 创建规则集
  │     ├─ 调用PersonalRulesManager.create_rule_set()
  │     ├─ 参数: name, description
  │     └─ 返回: RuleSet对象
  │
  ├─→ 2. 添加个人规则
  │     ├─ 创建PersonalRule对象
  │     │   ├─ id: 规则唯一标识
  │     │   ├─ name: 规则名称
  │     │   ├─ description: 规则描述
  │     │   ├─ category: 规则分类
  │     │   │   └─ 例如: COMMUNICATION, BEHAVIOR, STYLE
  │     │   ├─ priority: 优先级
  │     │   │   └─ 例如: HIGH, MEDIUM, LOW
  │     │   ├─ tags: 标签列表
  │     │   └─ examples: 示例列表
  │     └─ 调用PersonalRulesManager.add_rule()
  │
  ├─→ 3. 激活规则集
  │     ├─ 调用PersonalRulesManager.activate_rule_set()
  │     ├─ 设置当前激活的规则集
  │     └─ 规则集状态变为active
  │
  ├─→ 4. 生成规则提示词
  │     │
  │     ├─ 调用PersonalRulesManager.to_prompt()
  │     │
  │     ├─ 获取激活的规则集
  │     │
  │     ├─ 按优先级排序规则
  │     │   └─ HIGH > MEDIUM > LOW
  │     │
  │     ├─ 格式化规则文本
  │     │   └─ 例如:
  │     │       """
  │     │       个人规则:
  │     │       
  │     │       [高优先级]
  │     │       - 专业表达: 在工作场景中使用专业、正式的语言表达
  │     │         示例: ...
  │     │       
  │     │       [中优先级]
  │     │       - 简洁回复: 回答尽量简洁明了
  │     │       
  │     │       [低优先级]
  │     │       - 友好语气: 使用友好的语气
  │     │       """
  │     │
  │     └─ 返回规则提示词字符串
  │
  ├─→ 5. 注入到系统提示词
  │     ├─ 在Agent初始化时调用
  │     ├─ 调用_build_system_prompt()
  │     ├─ 将规则提示词添加到系统提示词中
  │     └─ LLM会根据规则生成回复
  │
  └─→ 6. 规则持久化（可选）
        ├─ 调用PersonalRulesManager.save_to_storage()
        ├─ 保存到JSON文件
        └─ 下次启动时自动加载
```

### 个人规则应用代码详解

#### 步骤1-2：创建规则集和添加规则

```python
# core/personal_rules.py - PersonalRulesManager类
class PersonalRulesManager:
    """个人规则管理器"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化个人规则管理器
        
        Args:
            storage_path: 规则存储路径
        """
        self._rule_sets: Dict[str, RuleSet] = {}
        self._active_rule_set: Optional[str] = None
        self.storage_path = storage_path
        
        # 如果有存储路径，加载已保存的规则
        if storage_path:
            self._load_from_storage()
    
    def create_rule_set(
        self,
        name: str,
        description: str = ""
    ) -> RuleSet:
        """
        创建规则集
        
        Args:
            name: 规则集名称
            description: 规则集描述
        
        Returns:
            RuleSet: 创建的规则集
        """
        rule_set = RuleSet(
            id=f"ruleset_{len(self._rule_sets)}",
            name=name,
            description=description
        )
        
        self._rule_sets[rule_set.id] = rule_set
        logger.info(f"创建规则集: {name}")
        
        return rule_set
    
    def add_rule(
        self,
        rule: PersonalRule,
        rule_set_id: Optional[str] = None
    ) -> None:
        """
        添加规则到规则集
        
        Args:
            rule: 个人规则
            rule_set_id: 规则集ID（如果为None，添加到激活的规则集）
        """
        if rule_set_id is None:
            rule_set_id = self._active_rule_set
        
        if rule_set_id is None:
            raise ValueError("没有激活的规则集")
        
        if rule_set_id not in self._rule_sets:
            raise ValueError(f"规则集 {rule_set_id} 不存在")
        
        self._rule_sets[rule_set_id].rules.append(rule)
        logger.info(f"添加规则: {rule.name} 到规则集 {rule_set_id}")
```

#### 步骤3：激活规则集

```python
# core/personal_rules.py - PersonalRulesManager类
def activate_rule_set(self, rule_set_id: str) -> None:
    """
    激活规则集
    
    Args:
        rule_set_id: 规则集ID
    """
    if rule_set_id not in self._rule_sets:
        raise ValueError(f"规则集 {rule_set_id} 不存在")
    
    # 停用当前激活的规则集
    if self._active_rule_set:
        self._rule_sets[self._active_rule_set].is_active = False
    
    # 激活新的规则集
    self._active_rule_set = rule_set_id
    self._rule_sets[rule_set_id].is_active = True
    
    logger.info(f"激活规则集: {self._rule_sets[rule_set_id].name}")
```

#### 步骤4：生成规则提示词

```python
# core/personal_rules.py - PersonalRulesManager类
def to_prompt(self) -> str:
    """
    将个人规则转换为提示词格式
    
    Returns:
        str: 规则提示词
    """
    if not self._active_rule_set:
        return ""
    
    rule_set = self._rule_sets.get(self._active_rule_set)
    if not rule_set:
        return ""
    
    # 按优先级分组
    priority_groups = {
        RulePriority.HIGH: [],
        RulePriority.MEDIUM: [],
        RulePriority.LOW: []
    }
    
    for rule in rule_set.rules:
        priority_groups[rule.priority].append(rule)
    
    # 构建提示词
    prompt_parts = ["个人规则:\n"]
    
    # 高优先级规则
    if priority_groups[RulePriority.HIGH]:
        prompt_parts.append("\n[高优先级]")
        for rule in priority_groups[RulePriority.HIGH]:
            prompt_parts.append(f"\n- {rule.name}: {rule.description}")
            if rule.examples:
                prompt_parts.append(f"  示例:")
                for example in rule.examples:
                    prompt_parts.append(f"    {example}")
    
    # 中优先级规则
    if priority_groups[RulePriority.MEDIUM]:
        prompt_parts.append("\n[中优先级]")
        for rule in priority_groups[RulePriority.MEDIUM]:
            prompt_parts.append(f"\n- {rule.name}: {rule.description}")
    
    # 低优先级规则
    if priority_groups[RulePriority.LOW]:
        prompt_parts.append("\n[低优先级]")
        for rule in priority_groups[RulePriority.LOW]:
            prompt_parts.append(f"\n- {rule.name}: {rule.description}")
    
    return "\n".join(prompt_parts)
```

#### 步骤5：注入到系统提示词

```python
# agents/agent.py - LangChainAgent类
def _build_system_prompt(self) -> str:
    """
    构建系统提示词
    
    Returns:
        str: 系统提示词
    """
    prompt_parts = []
    
    # 角色设定
    prompt_parts.append(f"角色: {self.config.system_prompt.persona}")
    
    # 个人规则（关键步骤）
    personal_rules_prompt = self.personal_rules_manager.to_prompt()
    if personal_rules_prompt:
        prompt_parts.append(f"\n{personal_rules_prompt}")
    
    # 系统规则
    if self.config.system_prompt.rules:
        prompt_parts.append("\n系统规则:")
        for rule in self.config.system_prompt.rules:
            prompt_parts.append(f"- {rule}")
    
    # 约束
    if self.config.system_prompt.constraints:
        prompt_parts.append("\n约束:")
        for constraint in self.config.system_prompt.constraints:
            prompt_parts.append(f"- {constraint}")
    
    # ... 其他部分
    
    return "\n".join(prompt_parts)
```

#### 步骤6：规则持久化

```python
# core/personal_rules.py - PersonalRulesManager类
def _save_to_storage(self) -> None:
    """保存规则到存储"""
    if not self.storage_path:
        return
    
    try:
        path = Path(self.storage_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 转换datetime为字符串（JSON序列化）
        rule_sets_data = []
        for rule_set in self._rule_sets.values():
            rule_set_dict = rule_set.dict()
            
            # 转换规则中的datetime
            for rule_dict in rule_set_dict['rules']:
                if 'created_at' in rule_dict and rule_dict['created_at']:
                    rule_dict['created_at'] = rule_dict['created_at'].isoformat()
                if 'updated_at' in rule_dict and rule_dict['updated_at']:
                    rule_dict['updated_at'] = rule_dict['updated_at'].isoformat()
            
            # 转换规则集中的datetime
            if 'created_at' in rule_set_dict and rule_set_dict['created_at']:
                rule_set_dict['created_at'] = rule_set_dict['created_at'].isoformat()
            if 'updated_at' in rule_set_dict and rule_set_dict['updated_at']:
                rule_set_dict['updated_at'] = rule_set_dict['updated_at'].isoformat()
            
            rule_sets_data.append(rule_set_dict)
        
        data = {'rule_sets': rule_sets_data}
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"规则已保存到存储: {self.storage_path}")
    
    except Exception as e:
        logger.error(f"保存规则失败: {e}")
```

### 个人规则应用示例

**示例：工作场景规则**

```python
# 创建规则管理器
manager = PersonalRulesManager(storage_path="data/personal_rules.json")

# 创建工作规则集
work_rule_set = manager.create_rule_set(
    name="工作规则",
    description="用于工作场景的个人规则"
)

# 添加高优先级规则
work_rules = [
    PersonalRule(
        id="work_001",
        name="专业表达",
        description="在工作场景中使用专业、正式的语言表达",
        category=RuleCategory.COMMUNICATION,
        priority=RulePriority.HIGH,
        tags=["工作", "专业", "表达"],
        examples=[
            "用户: 帮我写个邮件",
            "助手: 好的，我来帮您撰写一封专业的商务邮件..."
        ]
    ),
    PersonalRule(
        id="work_002",
        name="结构化输出",
        description="回答问题时使用结构化的格式，如列表、表格等",
        category=RuleCategory.STYLE,
        priority=RulePriority.MEDIUM,
        tags=["工作", "结构化"]
    ),
    PersonalRule(
        id="work_003",
        name="简洁回复",
        description="回答尽量简洁明了，避免冗长",
        category=RuleCategory.STYLE,
        priority=RulePriority.LOW,
        tags=["工作", "简洁"]
    )
]

# 添加规则到规则集
for rule in work_rules:
    manager.add_rule(rule, work_rule_set.id)

# 激活规则集
manager.activate_rule_set(work_rule_set.id)

# 生成的系统提示词示例：
"""
角色: 你是一个智能助手

个人规则:

[高优先级]

- 专业表达: 在工作场景中使用专业、正式的语言表达
  示例:
    用户: 帮我写个邮件
    助手: 好的，我来帮您撰写一封专业的商务邮件...

[中优先级]

- 结构化输出: 回答问题时使用结构化的格式，如列表、表格等

[低优先级]

- 简洁回复: 回答尽量简洁明了，避免冗长

系统规则:
- 你是一个智能助手，可以回答各种问题
- 你可以使用工具来完成任务

约束:
- 回答要准确
- 不要编造信息
"""
```

---

## 技能执行流程

### 技能执行流程图

```
技能调用请求
  │
  ├─→ 1. 接收技能调用请求
  │     └─ skill_manager.execute_skill(skill_name, input_data, context)
  │
  ├─→ 2. 查找技能
  │     ├─ 根据技能名称查找
  │     ├─ 检查技能是否存在
  │     └─ 检查技能是否启用
  │
  ├─→ 3. 检查技能依赖
  │     ├─ 获取技能依赖列表
  │     ├─ 检查依赖技能是否可用
  │     └─ 如果依赖不可用，抛出错误
  │
  ├─→ 4. 执行技能
  │     │
  │     ├─ 同步执行: skill.execute_sync(input_data, context)
  │     │
  │     ├─ 异步执行: await skill.execute(input_data, context)
  │     │
  │     └─ 技能内部流程:
  │         ├─ 验证输入数据
  │         ├─ 执行核心逻辑
  │         │   ├─ ReasoningSkill: 深度推理
  │         │   ├─ PlanningSkill: 任务规划
  │         │   ├─ AnalysisSkill: 数据分析
  │         │   └─ CreativitySkill: 创意生成
  │         ├─ 格式化输出结果
  │         └─ 返回SkillResult对象
  │
  ├─→ 5. 处理执行结果
  │     ├─ 检查执行是否成功
  │     │   ├─ 成功 → 返回output
  │     │   └─ 失败 → 记录错误，返回error
  │     ├─ 记录执行时间
  │     └─ 记录元数据
  │
  └─→ 6. 返回结果
        └─ SkillResult对象
```

### 技能执行代码详解

#### 步骤1-2：接收请求和查找技能

```python
# skills/skill_system.py - SkillManager类
class SkillManager:
    """技能管理器"""
    
    def __init__(self):
        """初始化技能管理器"""
        self._skills: Dict[str, BaseSkill] = {}
        self._register_builtin_skills()
    
    def _register_builtin_skills(self) -> None:
        """注册内置技能"""
        builtin_skills = [
            ReasoningSkill(),
            PlanningSkill(),
            AnalysisSkill(),
            CreativitySkill()
        ]
        
        for skill in builtin_skills:
            self.register_skill(skill)
    
    def register_skill(self, skill: BaseSkill) -> None:
        """
        注册技能
        
        Args:
            skill: 技能实例
        """
        metadata = skill.metadata
        self._skills[metadata.name] = skill
        logger.info(f"注册技能: {metadata.name} (v{metadata.version})")
    
    def get_skill(self, name: str) -> BaseSkill:
        """
        获取技能
        
        Args:
            name: 技能名称
        
        Returns:
            BaseSkill: 技能实例
        
        Raises:
            ValueError: 技能不存在或未启用
        """
        if name not in self._skills:
            raise ValueError(f"技能 '{name}' 不存在")
        
        skill = self._skills[name]
        
        if not skill.is_enabled():
            raise ValueError(f"技能 '{name}' 未启用")
        
        return skill
```

#### 步骤3：检查技能依赖

```python
# skills/skill_system.py - SkillManager类
def _check_dependencies(self, skill: BaseSkill) -> None:
    """
    检查技能依赖
    
    Args:
        skill: 技能实例
    
    Raises:
        ValueError: 依赖技能不可用
    """
    dependencies = skill.get_dependencies()
    
    for dep_name in dependencies:
        if dep_name not in self._skills:
            raise ValueError(
                f"技能 '{skill.metadata.name}' 依赖 '{dep_name}'，但该技能不存在"
            )
        
        dep_skill = self._skills[dep_name]
        if not dep_skill.is_enabled():
            raise ValueError(
                f"技能 '{skill.metadata.name}' 依赖 '{dep_name}'，但该技能未启用"
            )
```

#### 步骤4：执行技能

```python
# skills/skill_system.py - SkillManager类
async def execute_skill(
    self,
    name: str,
    input_data: Any,
    context: Dict[str, Any] = None
) -> SkillResult:
    """
    异步执行技能
    
    Args:
        name: 技能名称
        input_data: 输入数据
        context: 执行上下文
    
    Returns:
        SkillResult: 执行结果
    """
    try:
        # 查找技能
        skill = self.get_skill(name)
        
        # 检查依赖
        self._check_dependencies(skill)
        
        # 执行技能
        result = await skill.execute(input_data, context)
        
        logger.info(
            f"技能 '{name}' 执行完成，"
            f"耗时: {result.execution_time:.2f}秒"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"技能 '{name}' 执行失败: {e}")
        return SkillResult(
            success=False,
            error=str(e)
        )
```

#### 步骤5-6：处理和返回结果

```python
# skills/skill_system.py - BaseSkill类
class BaseSkill(ABC):
    """技能基类"""
    
    async def execute(
        self,
        input_data: Any,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        执行技能（子类实现）
        
        Args:
            input_data: 输入数据
            context: 执行上下文
        
        Returns:
            SkillResult: 执行结果
        """
        pass

# skills/skill_system.py - SkillResult类
class SkillResult(BaseModel):
    """技能执行结果"""
    success: bool = Field(..., description="是否成功")
    output: Any = Field(default=None, description="输出结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    execution_time: float = Field(default=0.0, description="执行时间（秒）")
```

### 技能执行示例

**示例1：推理技能执行**

```python
# 执行推理技能
result = await skill_manager.execute_skill(
    'reasoning',
    "如何设计一个高效的算法？",
    {'context': 'optimization'}
)

# 返回结果
SkillResult(
    success=True,
    output={
        'reasoning': [
            "问题分析: 这是一个算法设计问题",
            "关键要素: 效率、时间复杂度、空间复杂度",
            "推理结论: 可以采用分治、动态规划等策略"
        ]
    },
    execution_time=1.23
)
```

**示例2：规划技能执行**

```python
# 执行规划技能
result = await skill_manager.execute_skill(
    'planning',
    "开发一个Web应用",
    {'reasoning': reasoning_result.output}
)

# 返回结果
SkillResult(
    success=True,
    output=[
        {
            'step': 1,
            'action': '需求分析',
            'description': '明确应用的功能需求和用户需求'
        },
        {
            'step': 2,
            'action': '架构设计',
            'description': '设计应用的技术架构和数据库结构'
        },
        {
            'step': 3,
            'action': '开发实现',
            'description': '按照设计进行编码实现'
        },
        {
            'step': 4,
            'action': '测试部署',
            'description': '进行测试并部署到生产环境'
        }
    ],
    execution_time=0.89
)
```

---

## 完整执行流程示例

### 示例场景：用户查询"计算 123 * 456 并分析结果的意义"

```
┌─────────────────────────────────────────────────────────────────┐
│ 步骤1: 用户发送查询                                              │
└─────────────────────────────────────────────────────────────────┘
用户输入: "计算 123 * 456 并分析结果的意义"

┌─────────────────────────────────────────────────────────────────┐
│ 步骤2: Agent接收查询                                             │
└─────────────────────────────────────────────────────────────────┘
agent.query("计算 123 * 456 并分析结果的意义", enable_deep_think=True)

┌─────────────────────────────────────────────────────────────────┐
│ 步骤3: 深度思考（启用）                                          │
└─────────────────────────────────────────────────────────────────┘
3.1 执行推理技能
    - 分析问题: 需要计算和分析两个步骤
    - 识别关键: 数学计算、结果分析
    - 推理结论: 先计算，再分析

3.2 执行规划技能
    - 步骤1: 使用calculator工具计算 123 * 456
    - 步骤2: 分析计算结果的意义
    - 步骤3: 生成综合答案

思考结果:
{
  'reasoning': ['需要计算', '需要分析', '先计算后分析'],
  'planning': [
    {'step': 1, 'action': '计算'},
    {'step': 2, 'action': '分析'}
  ],
  'reasoning_time': 0.5,
  'planning_time': 0.3
}

┌─────────────────────────────────────────────────────────────────┐
│ 步骤4: 加载对话历史                                              │
└─────────────────────────────────────────────────────────────────┘
从MemoryManager获取历史消息:
[
  SystemMessage(content="角色: 你是一个智能助手..."),
  HumanMessage(content="你好"),
  AIMessage(content="你好！有什么可以帮助你的吗？")
]

构建完整消息列表:
[
  SystemMessage(...),
  HumanMessage("你好"),
  AIMessage("你好！..."),
  HumanMessage("计算 123 * 456 并分析结果的意义")
]

┌─────────────────────────────────────────────────────────────────┐
│ 步骤5: AgentExecutor执行                                         │
└─────────────────────────────────────────────────────────────────┘
5.1 LLM分析输入
    Thought: 用户想要计算数学表达式并分析结果
    需要使用calculator工具

5.2 第一次工具调用
    Action: calculator
    Action Input: {"expression": "123 * 456"}
    
    工具执行:
    - 参数验证: expression是字符串
    - 计算: eval("123 * 456") = 56088
    - 返回: "计算结果: 56088"
    
    Observation: 计算结果: 56088

5.3 LLM继续处理
    Thought: 已经得到计算结果56088，现在需要分析这个结果的意义
    不需要更多工具，直接生成答案

5.4 生成最终答案
    Final Answer: 
    "计算结果是 56088。
    
    这个结果的意义：
    1. 这是一个五位数，表示123和456的乘积
    2. 在数学上，这展示了乘法运算的基本性质
    3. 在实际应用中，这样的计算可能用于：
       - 面积计算（如123米 × 456米）
       - 成本计算（如123个单位 × 456元/单位）
       - 数据处理（如处理123条数据，每条456字节）"

┌─────────────────────────────────────────────────────────────────┐
│ 步骤6: 保存对话历史                                              │
└─────────────────────────────────────────────────────────────────┘
MemoryManager.add_message(
    session_id="default",
    Message(role='user', content='计算 123 * 456 并分析结果的意义')
)

MemoryManager.add_message(
    session_id="default",
    Message(role='assistant', content='计算结果是 56088...')
)

┌─────────────────────────────────────────────────────────────────┐
│ 步骤7: 构建返回结果                                              │
└─────────────────────────────────────────────────────────────────┘
{
  'answer': '计算结果是 56088。这个结果的意义...',
  'thinking': {
    'reasoning': [...],
    'planning': [...],
    'reasoning_time': 0.5,
    'planning_time': 0.3
  },
  'actions': [
    {
      'tool': 'calculator',
      'tool_input': {'expression': '123 * 456'},
      'log': 'Thought: 用户想要计算...'
    }
  ],
  'observations': ['计算结果: 56088'],
  'error': None
}

┌─────────────────────────────────────────────────────────────────┐
│ 步骤8: 返回结果给用户                                            │
└─────────────────────────────────────────────────────────────────┘
用户收到完整的回答和思考过程
```

### 时序图

```
用户          Agent         DeepThinker    SkillManager    MemoryManager    ToolManager    LLM
 │             │                │               │                │               │          │
 │──查询────→│                │               │                │               │          │
 │             │                │               │                │               │          │
 │             │──深度思考───→│               │                │               │          │
 │             │                │──推理技能──→│                │               │          │
 │             │                │               │──执行推理──→  │               │          │
 │             │                │               │←─推理结果───  │               │          │
 │             │                │──规划技能──→│                │               │          │
 │             │                │               │──执行规划──→  │               │          │
 │             │                │               │←─规划结果───  │               │          │
 │             │←─思考结果────│               │                │               │          │
 │             │                │               │                │               │          │
 │             │──加载历史───→│               │                │               │          │
 │             │                │               │                │←─历史消息───│          │
 │             │                │               │                │               │          │
 │             │──执行Agent──→│               │                │               │          │
 │             │                │               │                │               │──调用LLM→│
 │             │                │               │                │               │←─响应───│
 │             │                │               │                │               │          │
 │             │                │               │                │               │──工具调用→│
 │             │                │               │                │               │←─结果───│
 │             │                │               │                │               │          │
 │             │──保存历史───→│               │                │               │          │
 │             │                │               │                │──保存消息──→│          │
 │             │                │               │                │               │          │
 │←─返回结果──│                │               │                │               │          │
```

---

## 总结

### 核心流程总结

1. **初始化阶段**：加载配置 → 构建各组件 → 创建Agent实例
2. **查询处理阶段**：接收查询 → 深度思考 → 加载历史 → 执行Agent → 保存历史
3. **工具调用阶段**：LLM决策 → 选择工具 → 执行工具 → 返回结果
4. **记忆管理阶段**：存储消息 → 检索历史 → 摘要处理
5. **规则应用阶段**：创建规则 → 激活规则集 → 注入提示词

### 关键设计模式

1. **依赖注入模式**：各组件通过构造函数注入依赖，实现松耦合
2. **策略模式**：LLM提供者、存储后端等可插拔替换
3. **观察者模式**：回调处理器监控Agent执行过程
4. **建造者模式**：AgentBuilder逐步构建复杂Agent对象
5. **工厂模式**：LLMProviderFactory、MemoryBackendFactory创建实例

### 性能优化建议

1. **懒加载**：LLM实例在首次使用时才创建
2. **缓存策略**：配置缓存、工具元数据缓存
3. **异步执行**：支持异步查询和工具调用
4. **记忆摘要**：避免历史消息过长影响性能
5. **资源池化**：LLM连接池、数据库连接池

### 扩展点

1. **添加新LLM提供者**：继承BaseLLMProvider
2. **添加新工具**：继承BaseTool，定义args_schema
3. **添加新技能**：继承BaseSkill，实现execute方法
4. **添加新存储后端**：继承BaseMemoryBackend
5. **添加新规则类型**：扩展RuleCategory枚举

---

## 附录：关键文件索引

| 文件路径 | 功能说明 |
|---------|---------|
| `main.py` | 主程序入口，演示各种功能 |
| `core/config.py` | 配置管理，支持YAML配置 |
| `core/personal_rules.py` | 个人规则管理 |
| `agents/agent.py` | Agent核心逻辑 |
| `llm_providers/provider.py` | LLM提供者抽象层 |
| `tools/manager.py` | 工具管理系统 |
| `skills/skill_system.py` | 技能系统 |
| `memory/memory_system.py` | 记忆管理系统 |
| `examples/custom_tools.py` | 自定义工具示例 |
| `config/default.yaml` | 默认配置文件 |

---

**文档版本**: v1.0  
**最后更新**: 2024年  
**作者**: LangChain Agent Demo Team