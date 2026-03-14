# 多租户 LangChain Agent 服务架构设计

## 问题分析

### 核心挑战
1. **配置多样性**：每个租户可能有不同的LLM配置、工具集和技能定义
2. **资源压力**：每次请求都创建新实例会对数据库和服务器造成压力
3. **更新困难**：实例常驻内存时，配置更新难以生效
4. **内存管理**：大量租户实例可能导致内存溢出

## 解决方案：分层缓存 + 懒加载 + 版本控制

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                       │
│                   (FastAPI Endpoints)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Agent Instance Pool                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LRU Cache + TTL + Version Check                     │   │
│  │  - 最大实例数限制                                     │   │
│  │  - 自动清理不活跃实例                                 │   │
│  │  - 配置版本检测                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Tenant Agents:                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│  │Tenant 1 │  │Tenant 2 │  │Tenant N │                     │
│  │Agent    │  │Agent    │  │Agent    │                     │
│  └─────────┘  └─────────┘  └─────────┘                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Tenant Configuration Manager                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  配置缓存 (Redis/Memory)                             │   │
│  │  - 租户配置缓存                                       │   │
│  │  - 版本号管理                                         │   │
│  │  - 配置变更通知                                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Tenant Config│  │ Tool Defs    │  │ Skill Defs   │     │
│  │ (PostgreSQL) │  │ (PostgreSQL) │  │ (PostgreSQL) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. TenantConfigManager（租户配置管理器）
**职责**：
- 管理租户配置的加载和缓存
- 配置版本化管理
- 配置变更通知

**缓存策略**：
- 一级缓存：内存缓存（热点租户配置）
- 二级缓存：Redis缓存（所有租户配置）
- 数据库：持久化存储

**优势**：
- 配置读取快速（内存缓存命中率高）
- 配置更新实时（版本号检测）
- 减少数据库压力

#### 2. AgentInstancePool（Agent实例池）
**职责**：
- 管理Agent实例的生命周期
- LRU缓存策略
- TTL自动清理
- 版本检测自动更新

**缓存策略**：
```python
缓存键 = (tenant_id, config_version)
缓存值 = Agent实例 + 最后访问时间 + 创建时间

LRU策略：
- 最大实例数：100（可配置）
- TTL：30分钟（可配置）
- 清理策略：定期清理 + 访问时清理
```

**优势**：
- 热点租户实例常驻内存
- 冷门租户自动清理
- 配置更新自动重建实例

#### 3. 配置版本化
**实现方式**：
```python
class TenantConfig:
    tenant_id: str
    config_version: int  # 每次更新自增
    llm_config: LLMConfig
    tools: List[ToolConfig]
    skills: List[SkillConfig]
    updated_at: datetime
```

**更新流程**：
1. 数据库更新配置，version + 1
2. 清除Redis缓存
3. Agent池检测到版本变化，重建实例

### 性能优化策略

#### 1. 懒加载（Lazy Loading）
```python
# 不是预先创建所有租户实例，而是按需创建
agent = agent_pool.get_agent(tenant_id)  # 首次访问时创建
```

#### 2. 分层缓存
```
请求 → 内存缓存 → Redis缓存 → 数据库
      (10ms)      (50ms)      (200ms)
```

#### 3. 批量预加载
```python
# 对于已知的热点租户，服务启动时预加载
hot_tenants = ['tenant_1', 'tenant_2', 'tenant_3']
agent_pool.preload_agents(hot_tenants)
```

#### 4. 异步初始化
```python
# 使用后台任务初始化Agent，不阻塞请求
agent = await agent_pool.get_agent_async(tenant_id)
```

### 配置更新方案

#### 方案1：版本检测（推荐）
```python
# 每次获取Agent时检查版本
def get_agent(tenant_id):
    config = config_manager.get_config(tenant_id)
    cached_agent = cache.get((tenant_id, config.version))
    
    if cached_agent:
        return cached_agent
    else:
        # 清除旧版本实例
        cache.clear_old_versions(tenant_id)
        # 创建新实例
        return create_agent(config)
```

#### 方案2：事件驱动
```python
# 配置更新时发布事件
def update_tenant_config(tenant_id, new_config):
    db.update_config(tenant_id, new_config)
    event_bus.publish('config_updated', tenant_id)

# Agent池订阅事件
@event_handler('config_updated')
def on_config_updated(tenant_id):
    agent_pool.invalidate(tenant_id)
```

#### 方案3：定时刷新
```python
# 定期检查配置更新（适用于配置变更不频繁的场景）
async def refresh_configs():
    while True:
        await asyncio.sleep(300)  # 每5分钟检查一次
        for tenant_id in active_tenants:
            check_and_update(tenant_id)
```

### 资源管理

#### 内存限制
```python
class AgentInstancePool:
    MAX_INSTANCES = 100  # 最大实例数
    MAX_MEMORY_PER_INSTANCE = 500  # MB
    
    def check_memory(self):
        current_memory = get_memory_usage()
        if current_memory > WARNING_THRESHOLD:
            self.cleanup_inactive_agents()
```

#### 优雅关闭
```python
async def shutdown():
    # 保存所有租户状态
    for agent in agent_pool.get_all_agents():
        await agent.save_state()
    
    # 清理资源
    agent_pool.clear()
```

### 监控指标

#### 关键指标
1. **缓存命中率**：`cache_hits / total_requests`
2. **平均响应时间**：按租户统计
3. **实例数量**：当前活跃实例数
4. **内存使用**：总内存使用量
5. **配置更新延迟**：配置更新到生效的时间

#### 告警规则
- 缓存命中率 < 80%：考虑增加缓存大小
- 内存使用 > 80%：触发清理或扩容
- 实例创建耗时 > 5s：优化初始化流程

## 最佳实践

### 1. 配置设计
- 配置尽量轻量化，避免存储大量数据
- 使用引用而非复制（工具、技能定义可共享）
- 配置变更频率控制（避免频繁更新）

### 2. 实例管理
- 设置合理的TTL（根据业务特点）
- 监控热点租户，考虑预加载
- 实现优雅降级（实例创建失败时的备选方案）

### 3. 数据库设计
- 配置表建立索引（tenant_id, version）
- 考虑读写分离（配置读取频繁）
- 使用连接池减少连接开销

### 4. 扩展性
- 支持水平扩展（无状态设计）
- 使用分布式缓存（Redis Cluster）
- 考虑多数据中心部署

## 实现示例

详见以下文件：
- `tenant_config_manager.py`：租户配置管理器
- `agent_instance_pool.py`：Agent实例池
- `api_server.py`：FastAPI服务示例
- `models.py`：数据模型定义
