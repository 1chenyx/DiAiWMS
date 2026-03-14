# LangChain Agent Demo 项目结构说明

## 目录结构

```
langchain_agent_demo/
├── core/                      # 核心配置模块
│   ├── __init__.py           # 模块导出
│   └── config.py             # 配置管理系统（YAML配置、环境变量、验证）
│
├── llm_providers/             # LLM提供者抽象层
│   ├── __init__.py           # 模块导出
│   └── provider.py           # LLM提供者实现（OpenAI、Anthropic、Azure等）
│
├── tools/                     # 工具管理系统
│   ├── __init__.py           # 模块导出
│   └── manager.py            # 工具注册、自动发现、版本管理、访问控制
│
├── skills/                    # 技能系统
│   ├── __init__.py           # 模块导出
│   └── skill_system.py       # 技能管理、技能执行、技能组合
│
├── memory/                    # 记忆管理系统
│   ├── __init__.py           # 模块导出
│   └── memory_system.py      # 记忆存储后端（内存、Redis、SQLite等）
│
├── agents/                    # Agent核心逻辑
│   ├── __init__.py           # 模块导出
│   └── agent.py              # Agent实现（深度思考、工具调用、多会话）
│
├── examples/                  # 示例和演示
│   ├── example_tools.py      # 示例工具（计算器、搜索、日期时间等）
│   └── custom_tools.py       # 自定义工具示例（带元数据装饰器）
│
├── config/                    # 配置文件
│   └── default.yaml          # 默认配置文件
│
├── utils/                     # 工具函数（预留）
│
├── main.py                    # 主程序入口（完整演示）
├── simple_example.py          # 简单使用示例
├── requirements.txt           # 依赖包列表
├── README.md                  # 项目说明文档
├── QUICKSTART.md              # 快速开始指南
└── PROJECT_STRUCTURE.md       # 本文件 - 项目结构说明
```

## 核心模块说明

### 1. core/config.py - 配置管理系统

**功能：**
- YAML配置文件加载和解析
- 环境变量替换
- 配置验证（使用Pydantic）
- 多环境配置支持

**主要类：**
- `LLMConfig`: LLM配置模型
- `MemoryConfig`: 记忆配置模型
- `AgentConfig`: Agent配置模型
- `SystemPromptConfig`: 系统提示词配置
- `AgentSystemConfig`: 总配置模型
- `ConfigManager`: 配置管理器

### 2. llm_providers/provider.py - LLM提供者抽象层

**功能：**
- 统一的LLM接口
- 支持多种LLM提供者（OpenAI、Anthropic、Azure、HuggingFace、Ollama）
- 备用提供者机制
- 错误处理和重试

**主要类：**
- `BaseLLMProvider`: LLM提供者基类
- `OpenAIProvider`: OpenAI提供者
- `AnthropicProvider`: Anthropic提供者
- `AzureOpenAIProvider`: Azure OpenAI提供者
- `HuggingFaceProvider`: HuggingFace提供者
- `OllamaProvider`: Ollama提供者
- `LLMProviderFactory`: 提供者工厂
- `LLMManager`: LLM管理器

### 3. tools/manager.py - 工具管理系统

**功能：**
- 工具注册和注销
- 工具自动发现
- 工具版本管理
- 工具访问控制
- 工具分类和标签

**主要类：**
- `ToolMetadata`: 工具元数据
- `ToolWrapper`: 工具包装器
- `ToolRegistry`: 工具注册表
- `ToolDiscovery`: 工具发现器
- `ToolManager`: 工具管理器
- `tool_metadata`: 工具元数据装饰器

### 4. skills/skill_system.py - 技能系统

**功能：**
- 技能注册和管理
- 技能执行（同步/异步）
- 技能组合（链式执行）
- 内置技能（推理、规划、分析、创造性）

**主要类：**
- `SkillType`: 技能类型枚举
- `SkillMetadata`: 技能元数据
- `SkillResult`: 技能执行结果
- `BaseSkill`: 技能基类
- `ReasoningSkill`: 推理技能
- `PlanningSkill`: 规划技能
- `AnalysisSkill`: 分析技能
- `CreativitySkill`: 创造性技能
- `SkillRegistry`: 技能注册表
- `SkillManager`: 技能管理器

### 5. memory/memory_system.py - 记忆管理系统

**功能：**
- 多种存储后端支持
- 消息存储和检索
- 会话管理
- 对话摘要（可选）

**主要类：**
- `Message`: 消息模型
- `ConversationSummary`: 对话摘要模型
- `BaseMemoryBackend`: 记忆存储后端基类
- `InMemoryBackend`: 内存存储后端
- `RedisBackend`: Redis存储后端
- `SQLiteBackend`: SQLite存储后端
- `MemoryManager`: 记忆管理器
- `MemoryBackendFactory`: 后端工厂

### 6. agents/agent.py - Agent核心逻辑

**功能：**
- Agent构建和初始化
- 深度思考（链式思考）
- 工具自动调用
- 多会话管理
- 思考过程记录

**主要类：**
- `ThinkingCallbackHandler`: 思考过程回调处理器
- `DeepThinker`: 深度思考器
- `AgentBuilder`: Agent构建器
- `LangChainAgent`: LangChain Agent核心类

## 示例文件说明

### examples/example_tools.py

包含7个示例工具：
1. `CalculatorTool`: 计算器工具
2. `SearchTool`: 搜索工具
3. `DateTimeTool`: 日期时间工具
4. `CodeExecutorTool`: 代码执行器工具
5. `TextAnalyzerTool`: 文本分析器工具
6. `WeatherTool`: 天气查询工具
7. `UnitConverterTool`: 单位转换工具

### examples/custom_tools.py

包含5个自定义工具示例（带元数据装饰器）：
1. `PasswordGeneratorTool`: 密码生成器
2. `ColorConverterTool`: 颜色转换器
3. `QrCodeGeneratorTool`: 二维码生成器
4. `JsonFormatterTool`: JSON格式化器
5. `UrlEncoderTool`: URL编码器

## 配置文件说明

### config/default.yaml

包含以下配置：
- `llm`: LLM配置（提供者、模型、参数）
- `memory`: 记忆配置（后端、历史记录数）
- `agent`: Agent配置（类型、迭代次数、日志）
- `system_prompt`: 系统提示词（角色、规则、约束）
- `tools`: 工具配置列表
- `skills`: 技能配置列表

## 入口文件说明

### main.py

完整的演示程序，包含8个演示：
1. 基本查询
2. 工具使用
3. 深度思考
4. 对话记忆
5. 技能管理
6. 工具管理
7. 多会话管理
8. 异步查询

### simple_example.py

简化的使用示例，适合快速上手。

## 扩展指南

### 添加新的LLM提供者

1. 在 `llm_providers/provider.py` 中创建新类，继承 `BaseLLMProvider`
2. 实现 `create_llm()` 和 `get_model_name()` 方法
3. 在 `LLMProviderFactory._provider_classes` 中注册

### 添加新的工具

1. 创建工具类，继承 `BaseTool`
2. 定义输入模型（继承 `BaseModel`）
3. 实现 `_run()` 和 `_arun()` 方法
4. 使用 `@tool_metadata` 装饰器添加元数据
5. 在Agent中注册工具

### 添加新的技能

1. 创建技能类，继承 `BaseSkill`
2. 实现 `_get_metadata()` 和 `execute()` 方法
3. 在SkillManager中注册技能

### 添加新的记忆后端

1. 创建后端类，继承 `BaseMemoryBackend`
2. 实现所有抽象方法
3. 在 `MemoryBackendFactory.create_backend()` 中添加支持

## 设计原则

1. **模块化**: 各组件高度解耦，易于替换和扩展
2. **可配置**: 所有行为都可通过配置文件控制
3. **可扩展**: 提供清晰的扩展点，支持自定义组件
4. **类型安全**: 使用Pydantic进行数据验证
5. **异步支持**: 核心功能支持异步操作
6. **错误处理**: 完善的错误处理和日志记录

## 最佳实践

1. 使用虚拟环境隔离依赖
2. 在生产环境中使用Redis或PostgreSQL作为记忆后端
3. 根据需求调整LLM参数（温度、最大token等）
4. 合理设置记忆历史记录数，避免内存溢出
5. 使用工具元数据装饰器规范工具定义
6. 定期备份重要的配置文件
7. 监控LLM API调用成本和速率限制

## 学习路径

1. 运行 `simple_example.py` 了解基本用法
2. 阅读 `config/default.yaml` 理解配置系统
3. 查看 `examples/example_tools.py` 学习工具开发
4. 研究 `agents/agent.py` 理解Agent核心逻辑
5. 运行 `main.py` 查看完整演示
6. 根据需求修改和扩展系统
