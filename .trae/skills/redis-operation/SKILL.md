---
name: "redis-operation"
description: "Guides Redis operations with tenant isolation and proper key naming conventions. Invoke when creating cache operations, session management, or any Redis data storage."
---

# Redis 操作开发指南

本技能提供完整的 Redis 操作指导，严格遵循多租户隔离、Key 命名规范和时效性要求。

## 项目 Redis 架构

```
webapi/
├── app/
│   ├── utils/
│   │   └── cache_manager.py      # Redis缓存管理器
│   ├── ai/
│   │   └── ai_cache_manager.py   # AI配置缓存管理器
│   └── api/
│       └── dependencies.py        # JWT Token Redis存储
```

## Key 命名规范

### 标准命名格式

```
{应用名}:{租户ID}:{模块}:{功能}:{唯一标识}
```

### 命名规则详解

#### 1. 应用名 (Application)
- 固定值: `ModernWMS`
- 用于区分不同应用的缓存

#### 2. 租户ID (Tenant ID)
- 从 JWT Token 中获取
- 确保租户数据隔离
- 格式: UUID 字符串

#### 3. 模块 (Module)
- 表示业务模块
- 使用小写字母和下划线
- 示例: `user`, `stock`, `inbound`, `outbound`, `ai`

#### 4. 功能 (Function)
- 表示具体功能
- 使用小写字母和下划线
- 示例: `token`, `config`, `data`, `list`

#### 5. 唯一标识 (Identifier)
- 用于区分同一功能下的不同数据
- 可以是 ID、用户名、时间戳等
- 示例: `{user_id}`, `{config_id}`, `{timestamp}`

### Key 命名示例

```python
# 用户Token
ModernWMS:{tenant_id}:user:token:{user_id}

# 刷新Token
ModernWMS:{tenant_id}:user:refresh_token:{user_id}

# AI配置缓存
ModernWMS:{tenant_id}:ai:config:{config_id}

# AI模型缓存
ModernWMS:{tenant_id}:ai:model:{model_code}

# 库存数据缓存
ModernWMS:{tenant_id}:stock:data:{sku_id}

# 入库订单缓存
ModernWMS:{tenant_id}:inbound:order:{order_id}

# 出库订单缓存
ModernWMS:{tenant_id}:outbound:order:{order_id}

# 商品列表缓存
ModernWMS:{tenant_id}:product:list:{page_index}:{page_size}

# 仓库位置树缓存
ModernWMS:{tenant_id}:warehouse:location:tree

# 临时数据缓存
ModernWMS:{tenant_id}:temp:import:{task_id}
```

## 过期时间策略

### 默认过期时间配置

```python
# 缓存过期时间常量（分钟）
CACHE_EXPIRE_MINUTES = {
    # Token相关
    'access_token': 60,           # 1小时
    'refresh_token': 10080,      # 7天
    'verify_code': 5,            # 5分钟
    
    # 用户相关
    'user_info': 30,             # 30分钟
    'user_permissions': 60,      # 1小时
    
    # AI相关
    'ai_config': 60,              # 1小时
    'ai_model': 60,              # 1小时
    'ai_chat_history': 1440,     # 24小时
    
    # 业务数据
    'stock_data': 10,            # 10分钟
    'order_data': 15,            # 15分钟
    'product_list': 5,            # 5分钟
    'warehouse_tree': 30,        # 30分钟
    
    # 临时数据
    'import_task': 60,           # 1小时
    'export_task': 60,           # 1小时
    'temp_data': 10,             # 10分钟
}
```

### 过期时间选择原则

1. **高频访问数据**: 5-15分钟（如商品列表、库存数据）
2. **中频访问数据**: 30-60分钟（如用户信息、配置数据）
3. **低频访问数据**: 1-24小时（如历史记录、统计数据）
4. **临时数据**: 根据业务需求设置（如导入任务、验证码）
5. **Token数据**: 根据安全策略设置（如访问令牌1小时，刷新令牌7天）

## Redis 操作工具类

### CacheManager 使用

#### 基础操作

```python
from app.utils.cache_manager import CacheManager

# 获取单例实例
cache = CacheManager()

# 获取数据
data = cache.get(key)

# 设置数据（不过期）
cache.set_not_expire(key, value)

# 设置数据（滑动过期）
cache.set_sliding_expire(key, value, expire_minutes=30)

# 设置数据（绝对过期）
cache.set_absolute_expire(key, value, expire_minutes=60)

# 设置数据（滑动+绝对过期）
cache.set_sliding_and_absolute_expire(
    key, 
    value, 
    sliding_minutes=30, 
    absolute_minutes=60
)

# 删除数据
cache.remove(key)
```

#### Token 操作

```python
# 检查Token是否存在并续期
is_exist = cache.is_token_exist(user_id, 'access_token', 60)

# 设置Token
await cache.token_set(user_id, 'access_token', token, 60)
```

### 自定义 Redis 工具类

#### RedisHelper 工具类

```python
import json
import redis
from typing import Optional, Any, List, Dict
from datetime import timedelta
from app.initializer._conf import Config
from app.core.current_user import get_current_user

class RedisHelper:
    """Redis操作辅助类，提供统一的Key生成和操作方法"""
    
    def __init__(self):
        self._redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """初始化Redis连接"""
        try:
            config = Config()
            self._redis_client = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                db=config.redis_db,
                password=config.redis_password,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self._redis_client.ping()
        except Exception as e:
            self._redis_client = None
    
    def build_key(
        self,
        module: str,
        function: str,
        identifier: str,
        tenant_id: Optional[str] = None
    ) -> str:
        """
        构建标准的Redis Key
        
        Args:
            module: 模块名（如: user, stock, ai）
            function: 功能名（如: token, config, data）
            identifier: 唯一标识（如: user_id, config_id）
            tenant_id: 租户ID，如果不提供则从当前用户获取
        
        Returns:
            完整的Redis Key
        """
        if tenant_id is None:
            current_user = get_current_user()
            tenant_id = current_user.tenant_id if current_user else 'default'
        
        return f"ModernWMS:{tenant_id}:{module}:{function}:{identifier}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取数据"""
        if not self._redis_client:
            return None
        
        try:
            value = self._redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
        except Exception as e:
            pass
        
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        expire_minutes: int = 30
    ) -> bool:
        """
        设置数据并指定过期时间
        
        Args:
            key: Redis Key
            value: 要存储的值
            expire_minutes: 过期时间（分钟）
        
        Returns:
            是否设置成功
        """
        if not self._redis_client:
            return False
        
        try:
            expire_seconds = int(timedelta(minutes=expire_minutes).total_seconds())
            serialized_value = json.dumps(value, ensure_ascii=False)
            self._redis_client.setex(key, expire_seconds, serialized_value)
            return True
        except Exception as e:
            return False
    
    def delete(self, key: str) -> bool:
        """删除数据"""
        if not self._redis_client:
            return False
        
        try:
            self._redis_client.delete(key)
            return True
        except Exception as e:
            return False
    
    def exists(self, key: str) -> bool:
        """检查Key是否存在"""
        if not self._redis_client:
            return False
        
        try:
            return bool(self._redis_client.exists(key))
        except Exception as e:
            return False
    
    def expire(self, key: str, expire_minutes: int) -> bool:
        """设置Key的过期时间"""
        if not self._redis_client:
            return False
        
        try:
            expire_seconds = int(timedelta(minutes=expire_minutes).total_seconds())
            return bool(self._redis_client.expire(key, expire_seconds))
        except Exception as e:
            return False
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取数据"""
        if not self._redis_client:
            return {}
        
        try:
            values = self._redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        result[key] = value
            return result
        except Exception as e:
            return {}
    
    def set_many(
        self,
        data: Dict[str, Any],
        expire_minutes: int = 30
    ) -> bool:
        """批量设置数据"""
        if not self._redis_client:
            return False
        
        try:
            expire_seconds = int(timedelta(minutes=expire_minutes).total_seconds())
            pipe = self._redis_client.pipeline()
            for key, value in data.items():
                serialized_value = json.dumps(value, ensure_ascii=False)
                pipe.setex(key, expire_seconds, serialized_value)
            pipe.execute()
            return True
        except Exception as e:
            return False
    
    def delete_many(self, keys: List[str]) -> bool:
        """批量删除数据"""
        if not self._redis_client:
            return False
        
        try:
            if keys:
                self._redis_client.delete(*keys)
            return True
        except Exception as e:
            return False
    
    def get_pattern(self, pattern: str) -> List[Any]:
        """根据模式获取数据"""
        if not self._redis_client:
            return []
        
        try:
            keys = self._redis_client.keys(pattern)
            if keys:
                values = self._redis_client.mget(keys)
                result = []
                for value in values:
                    if value:
                        try:
                            result.append(json.loads(value))
                        except json.JSONDecodeError:
                            result.append(value)
                return result
            return []
        except Exception as e:
            return []
    
    def delete_pattern(self, pattern: str) -> int:
        """根据模式删除数据"""
        if not self._redis_client:
            return 0
        
        try:
            keys = self._redis_client.keys(pattern)
            if keys:
                return self._redis_client.delete(*keys)
            return 0
        except Exception as e:
            return 0

# 全局单例
_redis_helper = None

def get_redis_helper() -> RedisHelper:
    """获取RedisHelper单例"""
    global _redis_helper
    if _redis_helper is None:
        _redis_helper = RedisHelper()
    return _redis_helper
```

## 业务场景使用示例

### 1. 用户认证缓存

```python
from app.utils.cache_manager import CacheManager
from app.core.current_user import get_current_user

cache = CacheManager()
current_user = get_current_user()

# 生成访问令牌Key
access_token_key = f"ModernWMS:{current_user.tenant_id}:user:token:{current_user.user_id}"

# 设置访问令牌（1小时过期）
cache.set_absolute_expire(access_token_key, token, 60)

# 生成刷新令牌Key
refresh_token_key = f"ModernWMS:{current_user.tenant_id}:user:refresh_token:{current_user.user_id}"

# 设置刷新令牌（7天过期）
cache.set_absolute_expire(refresh_token_key, refresh_token, 10080)
```

### 2. 业务数据缓存

```python
from app.utils.cache_manager import CacheManager
from app.core.current_user import get_current_user

cache = CacheManager()
current_user = get_current_user()

# 库存数据缓存
stock_key = f"ModernWMS:{current_user.tenant_id}:stock:data:{sku_id}"
cache.set_absolute_expire(stock_key, stock_data, 10)

# 获取库存数据
cached_stock = cache.get(stock_key)
if cached_stock:
    return cached_stock

# 从数据库获取并缓存
stock_data = await stock_repository.get_by_id(sku_id)
cache.set_absolute_expire(stock_key, stock_data, 10)
return stock_data
```

### 3. 列表数据缓存

```python
from app.utils.cache_manager import CacheManager
from app.core.current_user import get_current_user

cache = CacheManager()
current_user = get_current_user()

# 商品列表缓存
product_list_key = f"ModernWMS:{current_user.tenant_id}:product:list:{page_index}:{page_size}"
cache.set_absolute_expire(product_list_key, product_list, 5)

# 获取商品列表
cached_list = cache.get(product_list_key)
if cached_list:
    return cached_list

# 从数据库获取并缓存
product_list = await product_repository.get_page(page_index, page_size)
cache.set_absolute_expire(product_list_key, product_list, 5)
return product_list
```

### 4. AI配置缓存

```python
from app.utils.cache_manager import CacheManager
from app.core.current_user import get_current_user

cache = CacheManager()
current_user = get_current_user()

# AI配置缓存
ai_config_key = f"ModernWMS:{current_user.tenant_id}:ai:config:{config_id}"
cache.set_absolute_expire(ai_config_key, ai_config, 60)

# 获取AI配置
cached_config = cache.get(ai_config_key)
if cached_config:
    return cached_config

# 从数据库获取并缓存
ai_config = await ai_config_repository.get_by_id(config_id)
cache.set_absolute_expire(ai_config_key, ai_config, 60)
return ai_config
```

### 5. 临时任务缓存

```python
from app.utils.cache_manager import CacheManager
from app.core.current_user import get_current_user

cache = CacheManager()
current_user = get_current_user()

# 导入任务缓存
import_task_key = f"ModernWMS:{current_user.tenant_id}:temp:import:{task_id}"
cache.set_absolute_expire(import_task_key, task_data, 60)

# 获取任务状态
task_status = cache.get(import_task_key)
if task_status:
    return task_status

# 任务完成后删除缓存
cache.remove(import_task_key)
```

### 6. 树形数据缓存

```python
from app.utils.cache_manager import CacheManager
from app.core.current_user import get_current_user

cache = CacheManager()
current_user = get_current_user()

# 仓库位置树缓存
tree_key = f"ModernWMS:{current_user.tenant_id}:warehouse:location:tree"
cache.set_absolute_expire(tree_key, tree_data, 30)

# 获取树形数据
cached_tree = cache.get(tree_key)
if cached_tree:
    return cached_tree

# 从数据库获取并缓存
tree_data = await warehouse_location_service.get_tree()
cache.set_absolute_expire(tree_key, tree_data, 30)
return tree_data
```

### 7. 验证码缓存

```python
from app.utils.cache_manager import CacheManager

cache = CacheManager()

# 验证码缓存（不区分租户，或使用default租户）
verify_code_key = f"ModernWMS:default:auth:verify_code:{phone_number}"
cache.set_absolute_expire(verify_code_key, code, 5)

# 验证验证码
cached_code = cache.get(verify_code_key)
if cached_code and cached_code == input_code:
    cache.remove(verify_code_key)
    return True
return False
```

### 8. 批量操作缓存

```python
from app.utils.cache_manager import CacheManager

cache = CacheManager()

# 批量设置缓存
cache_data = {
    f"ModernWMS:{tenant_id}:stock:data:{sku_id_1}": stock_data_1,
    f"ModernWMS:{tenant_id}:stock:data:{sku_id_2}": stock_data_2,
    f"ModernWMS:{tenant_id}:stock:data:{sku_id_3}": stock_data_3,
}

# 使用RedisHelper批量设置
from app.utils.redis_helper import get_redis_helper
redis_helper = get_redis_helper()
redis_helper.set_many(cache_data, expire_minutes=10)

# 批量获取缓存
keys = list(cache_data.keys())
cached_data = redis_helper.get_many(keys)
```

### 9. 模式匹配删除

```python
from app.utils.redis_helper import get_redis_helper

redis_helper = get_redis_helper()

# 删除某个租户的所有库存缓存
pattern = f"ModernWMS:{tenant_id}:stock:data:*"
deleted_count = redis_helper.delete_pattern(pattern)

# 删除某个租户的所有AI配置缓存
pattern = f"ModernWMS:{tenant_id}:ai:config:*"
deleted_count = redis_helper.delete_pattern(pattern)
```

### 10. 缓存失效策略

```python
from app.utils.cache_manager import CacheManager
from app.core.current_user import get_current_user

cache = CacheManager()
current_user = get_current_user()

# 数据更新时失效相关缓存
async def update_stock(sku_id: int, update_data: dict):
    # 更新数据库
    await stock_repository.update(sku_id, update_data)
    
    # 失效相关缓存
    stock_key = f"ModernWMS:{current_user.tenant_id}:stock:data:{sku_id}"
    cache.remove(stock_key)
    
    # 失效相关列表缓存
    pattern = f"ModernWMS:{current_user.tenant_id}:product:list:*"
    from app.utils.redis_helper import get_redis_helper
    redis_helper = get_redis_helper()
    redis_helper.delete_pattern(pattern)

# 数据删除时失效相关缓存
async def delete_stock(sku_id: int):
    # 删除数据库记录
    await stock_repository.delete(sku_id)
    
    # 失效相关缓存
    stock_key = f"ModernWMS:{current_user.tenant_id}:stock:data:{sku_id}"
    cache.remove(stock_key)
```

## 最佳实践

### 1. 缓存策略

```python
# Cache-Aside模式（旁路缓存）
async def get_stock(sku_id: int):
    # 1. 先查缓存
    cache_key = f"ModernWMS:{tenant_id}:stock:data:{sku_id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # 2. 缓存未命中，查数据库
    stock_data = await stock_repository.get_by_id(sku_id)
    
    # 3. 写入缓存
    if stock_data:
        cache.set_absolute_expire(cache_key, stock_data, 10)
    
    return stock_data

# Write-Through模式（写穿透）
async def update_stock(sku_id: int, update_data: dict):
    # 1. 更新数据库
    await stock_repository.update(sku_id, update_data)
    
    # 2. 更新缓存
    cache_key = f"ModernWMS:{tenant_id}:stock:data:{sku_id}"
    updated_data = await stock_repository.get_by_id(sku_id)
    cache.set_absolute_expire(cache_key, updated_data, 10)
```

### 2. 缓存穿透防护

```python
async def get_stock_with_protection(sku_id: int):
    cache_key = f"ModernWMS:{tenant_id}:stock:data:{sku_id}"
    
    # 查询缓存
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        # 缓存存在，返回数据（包括空值）
        return cached_data if cached_data else None
    
    # 查询数据库
    stock_data = await stock_repository.get_by_id(sku_id)
    
    # 缓存结果（包括空值，防止穿透）
    cache.set_absolute_expire(cache_key, stock_data or None, 5)
    
    return stock_data
```

### 3. 缓存雪崩防护

```python
import random

async def get_stock_with_random_expire(sku_id: int):
    cache_key = f"ModernWMS:{tenant_id}:stock:data:{sku_id}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    stock_data = await stock_repository.get_by_id(sku_id)
    
    # 随机过期时间，防止雪崩
    random_expire = random.randint(8, 12)
    cache.set_absolute_expire(cache_key, stock_data, random_expire)
    
    return stock_data
```

### 4. 缓存击穿防护

```python
import asyncio

_lock = {}

async def get_stock_with_lock(sku_id: int):
    cache_key = f"ModernWMS:{tenant_id}:stock:data:{sku_id}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # 使用锁防止击穿
    if cache_key not in _lock:
        _lock[cache_key] = asyncio.Lock()
    
    async with _lock[cache_key]:
        # 再次检查缓存
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 查询数据库
        stock_data = await stock_repository.get_by_id(sku_id)
        cache.set_absolute_expire(cache_key, stock_data, 10)
        
        del _lock[cache_key]
        return stock_data
```

### 5. 缓存预热

```python
async def warmup_cache(tenant_id: str):
    """预热缓存"""
    # 预热常用数据
    hot_skus = await get_hot_skus(tenant_id)
    for sku in hot_skus:
        cache_key = f"ModernWMS:{tenant_id}:stock:data:{sku.id}"
        stock_data = await stock_repository.get_by_id(sku.id)
        cache.set_absolute_expire(cache_key, stock_data, 10)
    
    # 预热树形数据
    tree_key = f"ModernWMS:{tenant_id}:warehouse:location:tree"
    tree_data = await warehouse_location_service.get_tree()
    cache.set_absolute_expire(tree_key, tree_data, 30)
```

## 错误处理

```python
from app.utils.cache_manager import CacheManager

cache = CacheManager()

try:
    # 尝试Redis操作
    data = cache.get(key)
    if data is None:
        # Redis失败，降级到数据库查询
        data = await repository.get_by_id(id)
except Exception as e:
    # 记录错误日志
    logger.error(f"Redis operation failed: {e}")
    # 降级到数据库查询
    data = await repository.get_by_id(id)
```

## 监控和日志

```python
import logging
import time

logger = logging.getLogger(__name__)

def get_with_monitoring(key: str):
    start_time = time.time()
    
    try:
        data = cache.get(key)
        elapsed = time.time() - start_time
        
        if data is not None:
            logger.info(f"Cache hit: {key}, elapsed: {elapsed:.3f}s")
        else:
            logger.info(f"Cache miss: {key}, elapsed: {elapsed:.3f}s")
        
        return data
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Cache error: {key}, elapsed: {elapsed:.3f}s, error: {e}")
        return None
```

## 开发流程 Checklist

- [ ] 使用标准Key命名格式: `{应用名}:{租户ID}:{模块}:{功能}:{唯一标识}`
- [ ] 为所有缓存数据设置合理的过期时间
- [ ] 使用CacheManager或RedisHelper进行操作
- [ ] 实现缓存失效策略（更新/删除时清理缓存）
- [ ] 添加缓存穿透、雪崩、击穿防护
- [ ] 实现降级策略（Redis失败时使用数据库）
- [ ] 添加监控和日志
- [ ] 测试缓存功能

## 常见问题

### 1. Key命名不规范

```python
# ❌ 错误
key = f"user_token_{user_id}"

# ✅ 正确
key = f"ModernWMS:{tenant_id}:user:token:{user_id}"
```

### 2. 忘记设置过期时间

```python
# ❌ 错误
cache.set_not_expire(key, value)

# ✅ 正确
cache.set_absolute_expire(key, value, expire_minutes=30)
```

### 3. 缓存失效不及时

```python
# ❌ 错误
await stock_repository.update(sku_id, update_data)

# ✅ 正确
await stock_repository.update(sku_id, update_data)
cache_key = f"ModernWMS:{tenant_id}:stock:data:{sku_id}"
cache.remove(cache_key)
```

### 4. 缓存穿透

```python
# ❌ 错误
if not cached_data:
    data = await repository.get_by_id(id)
    return data

# ✅ 正确
if cached_data is None:
    data = await repository.get_by_id(id)
    cache.set_absolute_expire(key, data or None, 5)
    return data
```

### 5. 缓存雪崩

```python
# ❌ 错误
cache.set_absolute_expire(key, value, 10)  # 所有缓存都是10分钟

# ✅ 正确
random_expire = random.randint(8, 12)
cache.set_absolute_expire(key, value, random_expire)
```
