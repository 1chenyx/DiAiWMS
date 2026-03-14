# LangChain Agent Demo

一个高度可扩展、可配置的LangChain AI Agent演示系统，展示了如何构建企业级的AI Agent应用。

## 特性

### 核心特性

- **多LLM提供者支持**: 支持OpenAI、Anthropic、Azure OpenAI、HuggingFace、Ollama等多种LLM
- **灵活的配置系统**: 基于YAML的配置文件，支持环境变量替换和多环境配置
- **工具管理系统**: 支持工具注册、自动发现、版本管理和访问控制
- **技能系统**: 可配置的技能系统，支持推理、规划、分析、创造性思维等
- **个人规则系统**: 支持自定义个人规则，按优先级和分类管理，集成到系统提示词
- **记忆管理**: 支持多种存储后端（内存、Redis、SQLite、PostgreSQL）
- **深度思考**: 集成链式思考和任务规划能力
- **多会话管理**: 支持多个独立的对话会话
- **异步支持**: 完整的异步API支持

### 架构设计

系统采用模块化设计，各组件高度解耦：

```
langchain_agent_demo/
├── core/              # 核心配置模块
├── llm_providers/     # LLM提供者抽象层
├── tools/             # 工具管理系统
├── skills/            # 技能系统
├── memory/            # 记忆管理系统
├── agents/            # Agent核心逻辑
├── examples/          # 示例工具和代码
├── config/            # 配置文件
└── main.py           # 主程序入口
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

设置OpenAI API密钥（或其他LLM提供者的密钥）：

```bash
export OPENAI_API_KEY='your-api-key-here'
```

或者在 `config/default.yaml` 中配置其他LLM提供者。

### 3. 运行演示

```bash
python main.py
```

## 配置说明

### LLM配置

在 `config/default.yaml` 中配置LLM：

```yaml
llm:
  provider: openai  # 可选: openai, anthropic, azure, huggingface, ollama
  model_name: gpt-3.5-turbo
  temperature: 0.7
  max_tokens: 2000
  api_key: ${OPENAI_API_KEY}  # 从环境变量读取
  fallback_providers: []  # 备用提供者
```

### 记忆配置

配置记忆存储后端：

```yaml
memory:
  backend: in_memory  # 可选: in_memory, redis, sqlite, postgresql
  max_history: 10
  enable_summarization: false
  summarization_threshold: 5
```

### Agent配置

配置Agent类型和行为：

```yaml
agent:
  name: "LangChain学习助手"
  type: react  # 可选: react, conversational, structured_chat, plan_and_execute
  verbose: true
  max_iterations: 10
```

### 系统提示词配置

自定义Agent的角色和规则：

```yaml
system_prompt:
  persona: "你是一个专业的AI助手"
  rules:
    - "始终以专业和友好的方式回答"
    - "在使用工具前，先分析问题"
  constraints:
    - "不要编造信息"
    - "保护用户隐私"
```

## 使用示例

### 基本查询

```python
from core import ConfigManager
from agents import AgentBuilder

# 加载配置
config_manager = ConfigManager(config_dir="config")
config = config_manager.load_config("default")

# 构建Agent
builder = AgentBuilder(config)
agent = builder.build_agent()

# 查询
result = agent.query_sync("你好，请介绍一下你自己")
print(result['answer'])
```

### 使用工具

```python
# Agent会自动调用工具
result = agent.query_sync("计算 123 * 456")
print(result['answer'])

result = agent.query_sync("现在是什么时间？")
print(result['answer'])
```

### 深度思考

```python
# 启用深度思考
result = agent.query_sync(
    "如何设计一个高效的算法？",
    enable_deep_think=True
)

# 查看思考过程
if result['thinking']:
    print("推理结果:", result['thinking']['reasoning'])
    print("规划结果:", result['thinking']['planning'])
```

### 多会话管理

```python
# 切换会话
agent.set_session_id("user_123")
agent.query_sync("我叫小明")

agent.set_session_id("user_456")
agent.query_sync("我叫小红")

# 查看会话历史
history = agent.get_conversation_history()
for msg in history:
    print(msg)
```

### 自定义工具

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    text: str = Field(description="输入文本")

class MyTool(BaseTool):
    name = "my_tool"
    description = "我的自定义工具"
    args_schema = MyToolInput
    
    def _run(self, text: str) -> str:
        return f"处理结果: {text}"

# 注册工具
agent.tool_manager.register_tool(
    MyTool(),
    agent.tool_manager.registry.ToolMetadata(
        name="my_tool",
        description="我的自定义工具",
        category="custom"
    )
)
```

### 自定义技能

```python
from skills import BaseSkill, SkillMetadata, SkillResult, SkillType

class MySkill(BaseSkill):
    def _get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="my_skill",
            type=SkillType.CUSTOM,
            description="我的自定义技能"
        )
    
    async def execute(self, input_data, context=None) -> SkillResult:
        # 实现技能逻辑
        return SkillResult(
            success=True,
            output="技能执行结果"
        )

# 注册技能
agent.skill_manager.register_skill(MySkill())
```

### 个人规则管理

```python
# 创建规则集
agent.create_rule_set(
    name="工作规则",
    description="用于工作场景的个人规则"
)

# 添加个人规则
agent.add_personal_rule(
    rule_set_name="工作规则",
    rule_id="work_001",
    name="专业表达",
    description="在工作场景中使用专业、正式的语言表达",
    category="communication",
    priority="high",
    tags=["工作", "专业", "表达"],
    examples=[
        "用户: 帮我写个邮件",
        "助手: 好的，我来帮您撰写一封专业的商务邮件..."
    ]
)

# 查看所有规则
rules = agent.list_personal_rules()
for rule in rules:
    print(f"- {rule['name']}: {rule['description']}")

# 搜索规则
results = agent.search_personal_rules("工作")
for rule in results:
    print(f"- {rule['name']}")

# 启用/禁用规则
agent.enable_personal_rule("工作规则", "work_001")
agent.disable_personal_rule("工作规则", "work_001")

# 导出规则
rules_data = agent.export_personal_rules()

# 导入规则
agent.import_personal_rules(rules_data)
```

## 扩展开发

### 添加新的LLM提供者

1. 在 `llm_providers/provider.py` 中创建新的提供者类，继承 `BaseLLMProvider`
2. 实现 `create_llm()` 和 `get_model_name()` 方法
3. 在 `LLMProviderFactory._provider_classes` 中注册

### 添加新的记忆后端

1. 在 `memory/memory_system.py` 中创建新的后端类，继承 `BaseMemoryBackend`
2. 实现所有抽象方法
3. 在 `MemoryBackendFactory.create_backend()` 中添加支持

### 添加新的Agent类型

在 `agents/agent.py` 的 `_initialize_agent()` 方法中添加新的Agent类型创建逻辑。

## 项目结构

```
langchain_agent_demo/
├── core/
│   ├── __init__.py
│   └── config.py              # 配置管理系统
├── llm_providers/
│   ├── __init__.py
│   └── provider.py            # LLM提供者抽象层
├── tools/
│   ├── __init__.py
│   └── manager.py             # 工具管理系统
├── skills/
│   ├── __init__.py
│   └── skill_system.py        # 技能系统
├── memory/
│   ├── __init__.py
│   └── memory_system.py       # 记忆管理系统
├── agents/
│   ├── __init__.py
│   └── agent.py               # Agent核心逻辑
├── examples/
│   └── example_tools.py       # 示例工具
├── config/
│   └── default.yaml           # 默认配置文件
├── main.py                    # 主程序入口
└── requirements.txt           # 依赖包列表
```

## 技术栈

- **LangChain**: AI Agent框架
- **Pydantic**: 数据验证和配置管理
- **PyYAML**: YAML配置文件解析
- **Redis**: 可选的分布式记忆存储
- **SQLite**: 可选的本地记忆存储

## 注意事项

1. 确保已设置正确的API密钥
2. 根据需要调整配置文件中的参数
3. 在生产环境中使用Redis或PostgreSQL作为记忆后端
4. 注意LLM API的调用成本和速率限制

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 学习资源

- [LangChain官方文档](https://langchain-doc.cn/v1/python/langchain/overview.html)
- [LangChain教程](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI API文档](https://platform.openai.com/docs)

## 联系方式

如有问题或建议，请通过Issue联系我们。
