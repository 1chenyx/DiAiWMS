# AI配置管理系统使用指南

## 系统概述

本系统是一个多租户AI配置管理系统，支持租户自定义LLM配置、工具配置、技能配置和规则配置。系统采用Agent池管理器来优化Agent实例的创建和复用，提高系统性能并降低资源消耗。

## 系统架构

### 核心组件

1. **系统配置层**：管理系统支持的LLM服务商、工具和规则
2. **租户配置层**：管理租户自定义的LLM配置、工具激活、技能和规则
3. **Agent池管理器**：管理Agent实例的创建、缓存、复用和清理
4. **AI聊天接口**：提供AI对话功能

### 技术栈

- **FastAPI**：Web框架
- **SQLAlchemy**：ORM框架
- **Redis**：缓存系统
- **LangChain**：AI Agent框架（待集成）
- **Pydantic**：数据验证

## 数据库表结构

### 1. tenant_ai_config（租户LLM配置表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键 |
| tenant_id | str | 租户ID |
| config_name | str | 配置名称 |
| provider_code | str | 服务商代码 |
| model_code | str | 模型代码 |
| api_key | str | API密钥（加密存储） |
| api_endpoint | str | API端点 |
| temperature | float | 温度参数 |
| max_tokens | int | 最大token数 |
| is_default | bool | 是否默认配置 |
| is_active | bool | 是否激活 |
| is_valid | bool | 是否有效 |

### 2. tenant_ai_tool（租户工具配置表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键 |
| tenant_id | str | 租户ID |
| tool_code | str | 工具代码 |
| tool_name | str | 工具名称 |
| tool_category | str | 工具分类 |
| config | json | 工具配置 |
| is_active | bool | 是否激活 |
| is_valid | bool | 是否有效 |

### 3. tenant_ai_skill（租户技能配置表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键 |
| tenant_id | str | 租户ID |
| skill_name | str | 技能名称 |
| skill_type | str | 技能类型 |
| description | str | 技能描述 |
| config | json | 技能配置 |
| is_active | bool | 是否激活 |
| is_valid | bool | 是否有效 |

### 4. tenant_ai_rule（租户规则配置表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键 |
| tenant_id | str | 租户ID |
| rule_name | str | 规则名称 |
| rule_category | str | 规则类别 |
| priority | int | 优先级 |
| content | str | 规则内容 |
| description | str | 规则描述 |
| is_active | bool | 是否激活 |
| is_system | bool | 是否系统规则 |
| is_valid | bool | 是否有效 |

## API接口文档

### 系统配置接口

#### 1. 获取所有AI服务商

```http
GET /api/v1/ai/system/providers
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "code": "openai",
      "name": "OpenAI",
      "description": "OpenAI官方API",
      "api_base": "https://api.openai.com/v1"
    }
  ]
}
```

#### 2. 获取服务商及其模型

```http
GET /api/v1/ai/system/providers-with-models
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "code": "openai",
      "name": "OpenAI",
      "description": "OpenAI官方API",
      "api_base": "https://api.openai.com/v1",
      "models": [
        {
          "code": "gpt-4",
          "name": "GPT-4",
          "type": "chat",
          "max_tokens": 8192,
          "description": "GPT-4模型"
        }
      ]
    }
  ]
}
```

#### 3. 获取系统工具列表

```http
GET /api/v1/ai/system/tools
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "code": "web_search",
      "name": "网络搜索",
      "category": "search",
      "description": "搜索互联网信息",
      "is_active": true,
      "is_system": true,
      "config_schema": {}
    }
  ]
}
```

#### 4. 获取系统规则列表

```http
GET /api/v1/ai/system/rules
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "code": "safety",
      "name": "安全规则",
      "category": "safety",
      "priority": 100,
      "content": "禁止生成有害内容",
      "description": "确保AI回复安全",
      "is_active": true,
      "is_system": true
    }
  ]
}
```

### 租户配置接口

#### 1. 获取默认LLM配置

```http
GET /api/v1/ai/config/llm/default
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "tenant_id": "tenant_001",
    "config_name": "默认配置",
    "provider_code": "openai",
    "model_code": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "is_default": true,
    "is_active": true
  }
}
```

#### 2. 创建LLM配置

```http
POST /api/v1/ai/config/llm
Content-Type: application/json

{
  "config_name": "生产环境配置",
  "provider_code": "openai",
  "model_code": "gpt-4",
  "api_key": "sk-xxx",
  "api_endpoint": "https://api.openai.com/v1",
  "temperature": 0.7,
  "max_tokens": 2000,
  "is_default": false,
  "is_active": true
}
```

#### 3. 激活工具

```http
POST /api/v1/ai/config/tools/activate
Content-Type: application/json

{
  "tool_code": "web_search",
  "tool_name": "网络搜索",
  "tool_category": "search",
  "config": {
    "search_engine": "google",
    "max_results": 5
  },
  "description": "搜索互联网信息"
}
```

#### 4. 创建技能

```http
POST /api/v1/ai/config/skills
Content-Type: application/json

{
  "skill_name": "代码审查",
  "skill_type": "analysis",
  "description": "审查代码质量",
  "config": {
    "prompt_template": "请审查以下代码...",
    "parameters": {
      "temperature": 0.3
    }
  },
  "is_active": true
}
```

#### 5. 创建规则

```http
POST /api/v1/ai/config/rules
Content-Type: application/json

{
  "rule_name": "代码规范",
  "rule_category": "professional",
  "priority": 80,
  "content": "所有代码必须符合PEP8规范",
  "description": "确保代码质量",
  "is_active": true
}
```

### AI聊天接口

#### 1. 聊天补全

```http
POST /api/v1/ai/chat/completions
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "你好，请介绍一下你自己"
    }
  ],
  "config_id": null,
  "stream": false,
  "temperature": null,
  "max_tokens": null
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message": {
      "role": "assistant",
      "content": "你好！我是一个AI助手..."
    },
    "usage": {
      "prompt_tokens": 100,
      "completion_tokens": 50,
      "total_tokens": 150
    },
    "agent_info": {
      "provider_code": "openai",
      "model_code": "gpt-4",
      "tools_count": 2,
      "skills_count": 1,
      "rules_count": 3
    }
  }
}
```

#### 2. 获取Agent池统计信息

```http
GET /api/v1/ai/chat/pool/stats
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_tenants": 5,
    "total_agents": 12,
    "tenants": {
      "tenant_001": {
        "agent_count": 3,
        "agents": [
          {
            "config_id": 1,
            "is_busy": false,
            "use_count": 15,
            "last_used_at": "2024-01-15T10:30:00"
          }
        ]
      }
    }
  }
}
```

#### 3. 清理Agent池

```http
POST /api/v1/ai/chat/pool/clear?config_id=1
```

## Agent池管理器

### 核心特性

1. **多租户隔离**：每个租户的Agent实例完全隔离
2. **LRU缓存策略**：自动淘汰最近最少使用的Agent
3. **空闲超时清理**：自动清理长时间未使用的Agent
4. **配置版本控制**：配置更新后自动清理旧Agent
5. **内存泄漏防护**：完善的资源清理机制

### 配置参数

```python
MAX_AGENTS_PER_TENANT = 10      # 每个租户最大Agent数量
MAX_IDLE_SECONDS = 1800         # 最大空闲时间（30分钟）
CLEANUP_INTERVAL = 300          # 清理间隔（5分钟）
```

### 使用示例

```python
from app.ai.agent.agent_pool_manager import get_agent_pool_manager
from sqlalchemy.ext.asyncio import AsyncSession

async def chat_example(tenant_id: str, db: AsyncSession):
    pool_manager = get_agent_pool_manager()
    
    # 获取Agent实例
    agent, error = await pool_manager.get_agent(
        tenant_id=tenant_id,
        config_id=None,  # 使用默认配置
        db=db
    )
    
    if error:
        print(f"获取Agent失败: {error}")
        return
    
    try:
        # 使用Agent进行对话
        response = await agent.chat("你好")
        print(response)
    finally:
        # 释放Agent（标记为空闲）
        await pool_manager.release_agent(tenant_id, agent.config_id)
```

## 系统配置文件

### 1. LLM服务商配置（llm_providers.yaml）

```yaml
providers:
  openai:
    code: openai
    name: OpenAI
    description: OpenAI官方API
    api_base: https://api.openai.com/v1
    models:
      - code: gpt-4
        name: GPT-4
        type: chat
        max_tokens: 8192
        description: GPT-4模型
```

### 2. 工具配置（ai_tools.yaml）

```yaml
tools:
  - code: web_search
    name: 网络搜索
    category: search
    description: 搜索互联网信息
    is_active: true
    is_system: true
    config_schema:
      type: object
      properties:
        search_engine:
          type: string
          description: 搜索引擎
```

### 3. 规则配置（ai_rules.yaml）

```yaml
rules:
  - code: safety
    name: 安全规则
    category: safety
    priority: 100
    content: 禁止生成有害内容
    description: 确保AI回复安全
    is_active: true
    is_system: true
```

## 最佳实践

### 1. 配置管理

- 为每个租户设置默认LLM配置
- 根据业务需求激活合适的工具
- 创建特定场景的技能配置
- 设置合理的规则优先级

### 2. Agent池管理

- 定期监控Agent池状态
- 及时清理不再使用的配置
- 合理设置Agent数量限制
- 注意内存使用情况

### 3. 性能优化

- 使用Redis缓存配置信息
- 避免频繁创建和销毁Agent
- 合理设置空闲超时时间
- 监控Agent使用频率

### 4. 安全建议

- API密钥加密存储
- 实施严格的权限控制
- 定期审计配置变更
- 监控异常使用行为

## 故障排查

### 1. Agent创建失败

**可能原因**：
- LLM配置错误
- API密钥无效
- 网络连接问题

**解决方案**：
- 检查LLM配置是否正确
- 验证API密钥是否有效
- 检查网络连接

### 2. Agent池内存泄漏

**可能原因**：
- Agent未正确释放
- 清理任务未启动
- 配置版本未更新

**解决方案**：
- 确保使用try-finally释放Agent
- 检查清理任务是否运行
- 手动清理Agent池

### 3. 配置更新不生效

**可能原因**：
- 缓存未清理
- Agent池未更新
- 配置版本未变更

**解决方案**：
- 清理Redis缓存
- 清理Agent池
- 更新配置版本

## 后续开发计划

1. **集成LangChain**：实现真实的AI Agent功能
2. **流式输出**：支持SSE流式响应
3. **工具执行**：实现工具自动调用
4. **技能系统**：实现技能动态加载
5. **监控告警**：添加性能监控和告警
6. **日志审计**：完善操作日志记录

## 联系方式

如有问题或建议，请联系开发团队。
