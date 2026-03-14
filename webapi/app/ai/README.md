# AI配置管理系统

## 快速开始

### 1. 运行数据库迁移

```bash
cd d:\python\xm\DIAIWMS\webapi
alembic upgrade head
```

### 2. 运行测试脚本

```bash
cd d:\python\xm\DIAIWMS\webapi
python -m app.ai.test_ai_config
```

### 3. 启动Web服务

```bash
cd d:\python\xm\DIAIWMS\webapi
python -m uvicorn app.main:app --reload
```

### 4. 访问API文档

打开浏览器访问：http://localhost:8000/docs

## 系统架构

```
webapi/app/ai/
├── config/                    # 配置文件目录
│   ├── llm_providers.yaml     # LLM服务商配置
│   ├── ai_tools.yaml          # AI工具配置
│   ├── ai_rules.yaml          # AI规则配置
│   └── config_loader.py       # 配置加载器
├── agent/                     # Agent模块
│   ├── agent_pool_manager.py  # Agent池管理器
│   └── __init__.py
├── AI_CONFIG_GUIDE.md         # 使用指南
├── test_ai_config.py          # 测试脚本
└── __init__.py
```

## 核心功能

### 1. 系统配置管理

- **LLM服务商配置**：管理系统支持的所有LLM服务商
- **工具配置**：管理系统提供的所有工具
- **规则配置**：管理系统内置的所有规则

### 2. 租户配置管理

- **LLM配置**：租户可以配置自己的LLM服务
- **工具激活**：租户可以激活需要的工具
- **技能配置**：租户可以创建自定义技能
- **规则配置**：租户可以添加自定义规则

### 3. Agent池管理

- **自动缓存**：Agent实例自动缓存和复用
- **LRU淘汰**：自动淘汰最近最少使用的Agent
- **空闲清理**：自动清理长时间未使用的Agent
- **配置版本**：配置更新后自动清理旧Agent

## API接口

### 系统配置接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/v1/ai/system/providers | GET | 获取所有服务商 |
| /api/v1/ai/system/providers-with-models | GET | 获取服务商及模型 |
| /api/v1/ai/system/tools | GET | 获取所有工具 |
| /api/v1/ai/system/rules | GET | 获取所有规则 |

### 租户配置接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/v1/ai/config/llm/default | GET | 获取默认LLM配置 |
| /api/v1/ai/config/llm | POST | 创建LLM配置 |
| /api/v1/ai/config/tools/activate | POST | 激活工具 |
| /api/v1/ai/config/skills | POST | 创建技能 |
| /api/v1/ai/config/rules | POST | 创建规则 |

### AI聊天接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/v1/ai/chat/completions | POST | AI聊天补全 |
| /api/v1/ai/chat/pool/stats | GET | 获取池统计信息 |
| /api/v1/ai/chat/pool/clear | POST | 清理Agent池 |

## 配置示例

### 创建LLM配置

```json
POST /api/v1/ai/config/llm
{
  "config_name": "生产环境配置",
  "provider_code": "openai",
  "model_code": "gpt-4",
  "api_key": "sk-xxx",
  "api_endpoint": "https://api.openai.com/v1",
  "temperature": "0.7",
  "max_tokens": 2000,
  "is_default": true,
  "is_active": true
}
```

### 激活工具

```json
POST /api/v1/ai/config/tools/activate
{
  "tool_code": "web_search",
  "tool_name": "网络搜索",
  "tool_category": "search",
  "config": {
    "search_engine": "google",
    "max_results": 5
  }
}
```

### 创建技能

```json
POST /api/v1/ai/config/skills
{
  "skill_name": "代码审查",
  "skill_type": "analysis",
  "description": "审查代码质量",
  "config": {
    "prompt_template": "请审查以下代码..."
  },
  "is_active": true
}
```

### 创建规则

```json
POST /api/v1/ai/config/rules
{
  "rule_name": "代码规范",
  "rule_category": "professional",
  "priority": 80,
  "content": "所有代码必须符合PEP8规范",
  "is_active": true
}
```

## 注意事项

1. **API密钥安全**：API密钥会加密存储，请妥善保管
2. **配置版本**：修改配置后，旧的Agent实例会自动清理
3. **内存管理**：系统会自动清理长时间未使用的Agent
4. **租户隔离**：每个租户的配置和Agent实例完全隔离

## 故障排查

### 1. 数据库迁移失败

检查数据库连接配置，确保数据库服务正常运行。

### 2. Agent创建失败

检查LLM配置是否正确，API密钥是否有效。

### 3. 配置更新不生效

手动清理Agent池：`POST /api/v1/ai/chat/pool/clear`

## 后续开发

1. 集成LangChain实现真实的AI Agent功能
2. 支持流式输出（SSE）
3. 实现工具自动调用
4. 添加性能监控和告警
5. 完善测试用例

## 联系方式

如有问题或建议，请联系开发团队。
