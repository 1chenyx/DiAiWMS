# 个人规则功能使用指南

## 功能概述

个人规则功能允许用户为AI Agent定义自定义的行为规则，这些规则会被集成到系统提示词中，指导Agent的行为和决策。

## 核心特性

### 1. 规则分类

规则按功能分为以下分类：

- **交流规则** (communication): 控制Agent的交流方式和风格
- **行为规则** (behavior): 定义Agent的行为模式
- **知识规则** (knowledge): 规定知识获取和使用的规则
- **伦理规则** (ethics): 设定伦理和安全约束
- **自定义规则** (custom): 用户自定义的其他规则

### 2. 规则优先级

规则按优先级分为四个等级：

- **关键** (critical): 必须严格遵守的规则
- **高** (high): 重要规则，优先遵守
- **中** (medium): 一般规则，建议遵守
- **低** (low): 可选规则，灵活遵守

### 3. 规则集管理

规则可以组织成规则集（RuleSet），便于分类管理：

- 每个规则集可以包含多条规则
- 可以启用/禁用整个规则集
- 支持多个规则集同时存在

## 快速开始

### 基本使用

```python
from core import ConfigManager
from agents import AgentBuilder

# 创建Agent
config_manager = ConfigManager(config_dir="config")
config = config_manager.load_config("default")

builder = AgentBuilder(config)
builder.build_llm_provider()
builder.build_tool_manager()
builder.build_skill_manager()
builder.build_memory_manager()
builder.build_thinker()
builder.build_personal_rules_manager()  # 构建个人规则管理器

agent = builder.build_agent()
```

### 查看默认规则

```python
# 列出所有规则集
rule_sets = agent.list_rule_sets()
print(f"规则集: {rule_sets}")

# 查看默认规则
default_rules = agent.list_personal_rules("default")
for rule in default_rules:
    print(f"- {rule['name']}: {rule['description']}")
```

### 创建自定义规则集

```python
# 创建规则集
agent.create_rule_set(
    name="工作规则",
    description="用于工作场景的个人规则"
)
```

### 添加个人规则

```python
# 添加规则到规则集
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
```

### 管理规则

```python
# 禁用规则
agent.disable_personal_rule("default", "rule_001")

# 启用规则
agent.enable_personal_rule("default", "rule_001")

# 移除规则
agent.remove_personal_rule("工作规则", "work_001")

# 删除规则集
agent.delete_rule_set("工作规则")
```

### 搜索规则

```python
# 按关键词搜索
results = agent.search_personal_rules("工作")
for rule in results:
    print(f"- {rule['name']}")

# 按分类搜索
results = agent.search_personal_rules("", category="ethics")
for rule in results:
    print(f"- [{rule['priority']}] {rule['name']}")
```

### 导出和导入规则

```python
# 导出规则
rules_data = agent.export_personal_rules()

# 保存到文件
import json
with open("my_rules.json", "w", encoding="utf-8") as f:
    json.dump(rules_data, f, ensure_ascii=False, indent=2)

# 导入规则
with open("my_rules.json", "r", encoding="utf-8") as f:
    rules_data = json.load(f)
agent.import_personal_rules(rules_data)
```

## 规则结构

### PersonalRule 模型

```python
{
    "id": "rule_001",              # 规则唯一标识
    "name": "友好交流",              # 规则名称
    "description": "始终保持友好...",  # 规则描述
    "category": "communication",      # 规则分类
    "priority": "high",            # 规则优先级
    "enabled": true,               # 是否启用
    "created_at": "2024-01-01...", # 创建时间
    "updated_at": "2024-01-01...", # 更新时间
    "tags": ["交流", "礼貌"],       # 规则标签
    "conditions": {},               # 触发条件（预留）
    "examples": []                 # 规则示例
}
```

## 实际应用场景

### 场景1: 工作助手

```python
# 创建工作规则集
agent.create_rule_set("工作规则", "工作场景规则")

# 添加专业表达规则
agent.add_personal_rule(
    rule_set_name="工作规则",
    rule_id="work_professional",
    name="专业表达",
    description="使用专业、正式的语言",
    category="communication",
    priority="high",
    tags=["工作", "专业"]
)

# 添加效率优先规则
agent.add_personal_rule(
    rule_set_name="工作规则",
    rule_id="work_efficiency",
    name="效率优先",
    description="优先考虑工作效率和结果",
    category="behavior",
    priority="medium",
    tags=["工作", "效率"]
)
```

### 场景2: 学习导师

```python
# 创建学习规则集
agent.create_rule_set("学习规则", "学习场景规则")

# 添加循序渐进规则
agent.add_personal_rule(
    rule_set_name="学习规则",
    rule_id="study_stepwise",
    name="循序渐进",
    description="按照循序渐进的方式讲解",
    category="behavior",
    priority="high",
    tags=["学习", "教学"],
    examples=[
        "用户: 教我Python",
        "助手: 我们从基础概念开始..."
    ]
)

# 添加鼓励探索规则
agent.add_personal_rule(
    rule_set_name="学习规则",
    rule_id="study_explore",
    name="鼓励探索",
    description="鼓励用户主动探索和实践",
    category="behavior",
    priority="medium",
    tags=["学习", "探索"]
)
```

### 场景3: 儿童模式

```python
# 创建儿童规则集
agent.create_rule_set("儿童规则", "儿童友好规则")

# 添加简单语言规则
agent.add_personal_rule(
    rule_set_name="儿童规则",
    rule_id="child_simple",
    name="简单语言",
    description="使用简单、易懂的语言",
    category="communication",
    priority="critical",
    tags=["儿童", "简单"]
)

# 添加安全规则
agent.add_personal_rule(
    rule_set_name="儿童规则",
    rule_id="child_safe",
    name="安全内容",
    description="只提供适合儿童的内容",
    category="ethics",
    priority="critical",
    tags=["儿童", "安全"]
)
```

## 规则提示词生成

个人规则会自动转换为提示词格式，集成到系统提示词中：

```
角色: 你是一个专业的AI助手

# 个人规则

## 交流规则

【必须】诚实回答
  如果不确定答案，诚实地说明而不是编造信息

【重要】友好交流
  始终保持友好、礼貌和尊重的态度与用户交流

## 伦理规则

【必须】保护隐私
  不要询问或存储用户的敏感个人信息

## 行为规则

【建议】主动帮助
  在用户需要时主动提供帮助和建议
```

## 持久化存储

个人规则支持持久化存储到JSON文件：

```python
# 创建带存储的规则管理器
builder.build_personal_rules_manager("data/personal_rules.json")

# 规则会自动保存和加载
```

## 最佳实践

1. **规则ID命名**: 使用有意义的ID，如 `work_001`, `study_001`
2. **优先级设置**: 重要规则使用 `critical` 或 `high`
3. **分类选择**: 根据规则性质选择合适的分类
4. **标签使用**: 添加相关标签便于搜索和管理
5. **示例提供**: 为规则提供示例，帮助理解应用场景
6. **规则集组织**: 按场景组织规则集，便于管理
7. **定期审查**: 定期审查和更新规则，确保有效性

## 注意事项

1. 规则数量不宜过多，建议控制在20条以内
2. 高优先级规则会覆盖低优先级规则
3. 规则描述要清晰、具体、可执行
4. 避免规则之间的冲突
5. 定期备份规则数据

## 运行演示

```bash
python personal_rules_demo.py
```

演示包含以下内容：
1. 查看默认规则
2. 创建自定义规则集
3. 添加个人规则
4. 管理规则（启用/禁用/删除）
5. 搜索规则
6. 导出和导入规则
7. 查看规则提示词

## 相关文件

- [core/personal_rules.py](file:///d:/python/xm/DIAIWMS/langchain_agent_demo/core/personal_rules.py) - 个人规则核心实现
- [agents/agent.py](file:///d:/python/xm/DIAIWMS/langchain_agent_demo/agents/agent.py) - Agent集成个人规则
- [personal_rules_demo.py](file:///d:/python/xm/DIAIWMS/langchain_agent_demo/personal_rules_demo.py) - 功能演示程序
