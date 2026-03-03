# AI功能模块说明

## 概述

AI功能模块提供了完整的AI配置和执行框架，支持接入不同供应商的不同AI模型，使用LangGraph框架构建工作流。

## 架构设计

### 1. 数据库模型

#### AIProvider (AI提供商表)
存储不同AI服务提供商的配置信息，如OpenAI、Anthropic、Azure等。

主要字段：
- `provider_name`: 提供商名称
- `provider_code`: 提供商代码（唯一标识）
- `api_key`: API密钥
- `api_endpoint`: API端点URL
- `is_active`: 是否启用
- `priority`: 优先级
- `config`: 其他配置参数（JSON格式）

#### AIModel (AI模型表)
存储不同AI模型的配置信息，如gpt-4、claude-3等。

主要字段：
- `provider_id`: 关联的AI提供商ID
- `model_name`: 模型名称
- `model_code`: 模型代码（唯一标识）
- `model_type`: 模型类型（chat、completion、embedding等）
- `max_tokens`: 最大token数
- `temperature`: 温度参数
- `top_p`: top_p参数
- `is_active`: 是否启用
- `is_default`: 是否为默认模型

#### AITask (AI任务表)
记录AI执行任务的日志和状态。

主要字段：
- `task_id`: 任务ID（UUID）
- `task_type`: 任务类型
- `provider_id`: 使用的AI提供商ID
- `model_id`: 使用的AI模型ID
- `status`: 任务状态（pending、running、completed、failed）
- `input_data`: 输入数据（JSON格式）
- `output_data`: 输出数据（JSON格式）
- `token_usage`: token使用情况（JSON格式）

### 2. 缓存管理

使用Redis缓存AI配置，提高查询性能：

- `ai:provider:{id}`: AI提供商缓存
- `ai:model:{id}`: AI模型缓存
- `ai:model:code:{tenant_id}:{model_code}`: 根据代码缓存AI模型
- `ai:default_model:{tenant_id}`: 默认AI模型缓存
- `ai:provider:active:{tenant_id}`: 启用的AI提供商列表缓存

### 3. AI执行框架

#### BaseAIProvider (AI提供商抽象基类)
所有AI提供商实现类都应继承此类，实现`execute`和`get_model_config`方法。

#### OpenAIProvider (OpenAI提供商实现)
实现了OpenAI API的调用，支持GPT系列模型。

#### AnthropicProvider (Anthropic提供商实现)
实现了Anthropic API的调用，支持Claude系列模型。

#### AIProviderFactory (AI提供商工厂)
根据提供商代码创建对应的提供商实例，支持动态注册新的提供商。

#### AIExecutor (AI执行器)
负责AI任务的执行和管理，包括：
- 任务创建和状态管理
- 模型选择和配置加载
- 提供商实例化和执行
- 结果返回和错误处理

#### LangGraphWorkflow (LangGraph工作流基类)
使用LangGraph构建AI工作流的基础框架，预留了扩展接口。

#### ChatWorkflow (聊天工作流)
简单的聊天对话工作流实现。

## API接口

### AI提供商管理

#### 获取AI提供商
```
GET /api/v1/ai/provider?id={id}
```

#### 获取AI提供商列表
```
GET /api/v1/ai/provider/list
```

#### 获取启用的AI提供商
```
GET /api/v1/ai/provider/active
```

#### 创建AI提供商
```
POST /api/v1/ai/provider
Content-Type: application/json

{
  "provider_name": "OpenAI",
  "provider_code": "openai",
  "api_key": "sk-xxx",
  "api_endpoint": "https://api.openai.com/v1",
  "description": "OpenAI API",
  "is_active": true,
  "priority": 0,
  "config": {}
}
```

#### 更新AI提供商
```
PUT /api/v1/ai/provider/{id}
Content-Type: application/json

{
  "api_key": "sk-new-xxx",
  "is_active": false
}
```

#### 删除AI提供商
```
DELETE /api/v1/ai/provider/{id}
```

### AI模型管理

#### 获取AI模型
```
GET /api/v1/ai/model?id={id}
```

#### 获取AI模型列表
```
GET /api/v1/ai/model/list
```

#### 获取默认AI模型
```
GET /api/v1/ai/model/default
```

#### 创建AI模型
```
POST /api/v1/ai/model
Content-Type: application/json

{
  "provider_id": 1,
  "model_name": "GPT-4",
  "model_code": "gpt-4",
  "model_type": "chat",
  "max_tokens": 4096,
  "temperature": 70,
  "top_p": 90,
  "description": "GPT-4模型",
  "is_active": true,
  "is_default": true,
  "config": {}
}
```

#### 更新AI模型
```
PUT /api/v1/ai/model/{id}
Content-Type: application/json

{
  "max_tokens": 8192,
  "is_default": false
}
```

#### 删除AI模型
```
DELETE /api/v1/ai/model/{id}
```

### AI任务执行

#### 执行AI任务
```
POST /api/v1/ai/execute
Content-Type: application/json

{
  "task_type": "chat",
  "model_code": "gpt-4",
  "input_data": {
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  },
  "config": {}
}
```

#### 获取AI任务结果
```
GET /api/v1/ai/task/{task_id}
```

#### AI聊天接口
```
POST /api/v1/ai/chat
Content-Type: application/json

{
  "model_code": "gpt-4",
  "input_data": {
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  },
  "config": {}
}
```

## 使用示例

### 1. 配置OpenAI提供商

```python
import requests

# 创建OpenAI提供商
response = requests.post(
    "http://localhost:8000/api/v1/ai/provider",
    json={
        "provider_name": "OpenAI",
        "provider_code": "openai",
        "api_key": "sk-your-api-key",
        "api_endpoint": "https://api.openai.com/v1",
        "description": "OpenAI API",
        "is_active": True,
        "priority": 0
    },
    headers={"Authorization": "Bearer your-token"}
)

provider = response.json()
provider_id = provider["data"]["id"]
```

### 2. 配置GPT-4模型

```python
# 创建GPT-4模型
response = requests.post(
    "http://localhost:8000/api/v1/ai/model",
    json={
        "provider_id": provider_id,
        "model_name": "GPT-4",
        "model_code": "gpt-4",
        "model_type": "chat",
        "max_tokens": 4096,
        "temperature": 70,
        "top_p": 90,
        "description": "GPT-4模型",
        "is_active": True,
        "is_default": True
    },
    headers={"Authorization": "Bearer your-token"}
)
```

### 3. 执行AI聊天

```python
# 执行聊天
response = requests.post(
    "http://localhost:8000/api/v1/ai/chat",
    json={
        "input_data": {
            "messages": [
                {"role": "user", "content": "你好，请介绍一下你自己"}
            ]
        }
    },
    headers={"Authorization": "Bearer your-token"}
)

result = response.json()
if result["isSuccess"]:
    output = result["data"]["output"]
    print(output["content"])
```

## 扩展开发

### 添加新的AI提供商

1. 创建新的提供商类，继承`BaseAIProvider`：

```python
from app.ai.ai_executor import BaseAIProvider, AIProviderViewModel
from typing import Dict, Any, Optional

class CustomProvider(BaseAIProvider):
    async def execute(
        self,
        model: AIModelViewModel,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # 实现自定义AI调用逻辑
        pass
    
    def get_model_config(self, model: AIModelViewModel) -> Dict[str, Any]:
        # 实现模型配置转换逻辑
        pass
```

2. 注册新的提供商：

```python
from app.ai.ai_executor import AIProviderFactory

AIProviderFactory.register_provider("custom", CustomProvider)
```

### 创建自定义工作流

继承`LangGraphWorkflow`类并实现`execute_workflow`方法：

```python
from app.ai.ai_executor import LangGraphWorkflow
from typing import Dict, Any, Optional
from app.core.current_user import CurrentUser

class CustomWorkflow(LangGraphWorkflow):
    async def execute_workflow(
        self,
        input_data: Dict[str, Any],
        current_user: Optional[CurrentUser] = None
    ) -> Dict[str, Any]:
        # 实现自定义工作流逻辑
        # 可以使用LangGraph构建复杂的工作流
        pass
```

## 数据库迁移

执行数据库迁移以创建AI相关表：

```bash
cd d:\python\xm\DIAIWMS\webapi
alembic upgrade head
```

## 依赖安装

安装AI相关依赖：

```bash
cd d:\python\xm\DIAIWMS\webapi
pip install -r requirements.txt
```

主要依赖：
- `langgraph>=0.2.0`: LangGraph工作流框架
- `openai>=1.0.0`: OpenAI SDK
- `anthropic>=0.40.0`: Anthropic SDK

## 注意事项

1. **API密钥安全**: AI提供商的API密钥存储在数据库中，建议在生产环境中使用加密存储
2. **缓存更新**: 修改AI配置后，相关缓存会自动更新
3. **租户隔离**: AI配置按租户隔离，不同租户的配置互不影响
4. **默认模型**: 每个租户可以设置一个默认模型，执行任务时如果不指定模型则使用默认模型
5. **任务日志**: 所有AI任务执行都会记录日志，便于追踪和调试
