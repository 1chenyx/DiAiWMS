# 多租户数据库连接池重构说明

## 概述

本次重构实现了多租户数据库连接池架构，支持租户级别的数据库隔离和主从数据库读写分离。租户管理模块使用主库，其他所有模块根据当前用户的租户ID自动路由到对应的租户数据库。

## 架构设计

### 1. 核心组件

#### TenantDatabaseConfig
租户数据库配置类，存储单个租户的数据库连接信息：
- 主库连接信息（host, port, username, password等）
- 从库连接信息（可选，用于读写分离）
- 连接池配置（pool_size, max_overflow, pool_recycle）

#### TenantDatabasePool
租户数据库连接池管理器（单例模式），管理所有租户的数据库连接池：
- 主库连接池（用于租户管理模块）
- 租户数据库连接池字典（tenant_id -> engine_info）
- 支持动态添加和移除租户数据库连接
- 支持主从数据库读写分离

### 2. 数据库连接流程

```
用户请求 -> JWT认证 -> 获取CurrentUser(tenant_id)
                |
                v
        根据租户ID获取数据库会话
                |
                +---> 租户管理模块 -> 主库连接池
                |
                +---> 其他业务模块 -> 租户数据库连接池(tenant_id)
                                    |
                                    +---> 写操作 -> 主库会话
                                    |
                                    +---> 读操作 -> 从库会话(如果配置了从库)
```

## 文件修改清单

### 新增文件

1. **[tenant_database.py](file:///d:/python/xm/DIAIWMS/webapi/app/core/tenant_database.py)** - 租户数据库连接池核心实现
2. **[tenant_database.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/tenant_database.py)** - 租户数据库管理API接口
3. **[test_tenant_database.py](file:///d:/python/xm/DIAIWMS/webapi/test_tenant_database.py)** - 多租户数据库连接池测试脚本
4. **[update_api_tenant_db.py](file:///d:/python/xm/DIAIWMS/webapi/update_api_tenant_db.py)** - API文件批量更新脚本

### 修改文件

1. **[database.py](file:///d:/python/xm/DIAIWMS/webapi/app/core/database.py)** - 添加租户数据库连接获取函数
2. **[dependencies.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/dependencies.py)** - 添加多租户依赖注入函数
3. **[__init__.py](file:///d:/python/xm/DIAIWMS/webapi/app/initializer/__init__.py)** - 初始化主库连接池
4. **[_conf.py](file:///d:/python/xm/DIAIWMS/webapi/app/initializer/_conf.py)** - 添加主从数据库配置项
5. **[app_dev.yaml](file:///d:/python/xm/DIAIWMS/webapi/config/app_dev.yaml)** - 添加主从数据库配置

### API模块更新

所有业务API模块已更新为使用租户数据库连接（除租户管理模块外）：
- [category.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/category.py)
- [stockadjust.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/stockadjust.py)
- [stockmove.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/stockmove.py)
- [stockfreeze.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/stockfreeze.py)
- [asn.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/asn.py)
- [supplier.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/supplier.py)
- [customer.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/customer.py)
- [stocktaking.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/stocktaking.py)
- [stockprocess.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/stockprocess.py)
- [dispatchlist.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/dispatchlist.py)
- [warehouse_area.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/warehouse_area.py)
- [goods_owner.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/goods_owner.py)
- [company.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/company.py)
- [account.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/account.py)
- [user_role.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/user_role.py)
- [rolemenu.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/rolemenu.py)
- [action_log.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/action_log.py)
- [freightfee.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/freightfee.py)
- [print_solution.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/print_solution.py)
- [user.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/user.py)
- [warehouse.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/warehouse.py)
- [goods_location.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/goods_location.py)
- [spu.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/spu.py)
- [sku.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/sku.py)
- [stock.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/stock.py)

租户管理模块使用主库：
- [tenant.py](file:///d:/python/xm/DIAIWMS/webapi/app/api/v1/tenant.py)

## 使用方式

### 1. 依赖注入

#### 租户管理模块（使用主库）
```python
from app.api.dependencies import get_master_db_session

@router.get("/tenant")
async def get_tenant(
    id: int,
    db: AsyncSession = Depends(get_master_db_session)
):
    # 使用主库会话
    ...
```

#### 业务模块（使用租户数据库）
```python
from app.api.dependencies import get_db_by_tenant

@router.get("/category")
async def get_category(
    id: int,
    db: AsyncSession = Depends(get_db_by_tenant)  # 自动根据当前用户的tenant_id获取租户数据库
):
    # 使用租户数据库会话（写操作）
    ...
```

#### 读操作（使用从库）
```python
from app.api.dependencies import get_db_by_tenant_read

@router.get("/category/list")
async def get_category_list(
    db: AsyncSession = Depends(get_db_by_tenant_read)  # 使用租户从库会话
):
    # 使用租户从库会话（读操作）
    ...
```

### 2. 租户数据库管理API

#### 添加租户数据库连接池
```bash
POST /api/v1/tenant-database/add
{
    "tenant_id": 1,
    "db_drivername": "mysql+aiomysql",
    "db_database": "tenant1_db",
    "db_username": "root",
    "db_password": "password",
    "db_host": "localhost",
    "db_port": 3306,
    "db_charset": "utf8mb4",
    "slave_host": "localhost",  # 可选
    "slave_port": 3307  # 可选
}
```

#### 移除租户数据库连接池
```bash
DELETE /api/v1/tenant-database/remove?tenant_id=1
```

#### 检查租户数据库连接池是否存在
```bash
GET /api/v1/tenant-database/check?tenant_id=1
```

#### 获取租户数据库配置
```bash
GET /api/v1/tenant-database/config?tenant_id=1
```

#### 列出所有租户数据库连接池
```bash
GET /api/v1/tenant-database/list
```

### 3. 配置文件

在 `config/app_dev.yaml` 中配置主从数据库：

```yaml
# 主库配置
db_drivername: mysql+aiomysql
db_database: master_db
db_username: root
db_password: password
db_host: localhost
db_port: 3306
db_charset: utf8mb4

# 从库配置（可选）
db_slave_host: localhost
db_slave_port: 3307
```

## 主从数据库读写分离

### 实现原理

1. **写操作**：使用主库连接
   - 通过 `get_db_by_tenant` 获取租户主库会话
   - 所有INSERT、UPDATE、DELETE操作使用主库

2. **读操作**：使用从库连接（如果配置了从库）
   - 通过 `get_db_by_tenant_read` 获取租户从库会话
   - 所有SELECT操作使用从库
   - 如果未配置从库，则使用主库

### 使用建议

- 查询接口使用 `get_db_by_tenant_read` 以利用从库
- 创建/更新/删除接口使用 `get_db_by_tenant` 以使用主库
- 租户管理模块统一使用 `get_master_db_session`

## 测试结果

运行测试脚本 `test_tenant_database.py` 的结果：

```
==================================================
多租户数据库连接池测试
==================================================
==================================================
测试主库连接
==================================================
✓ 主库会话获取成功
✓ 主库会话关闭成功

==================================================
测试租户数据库连接
==================================================
✓ 租户1数据库连接池添加成功
✓ 租户1存在检查: True
✓ 租户1会话获取成功
✓ 租户1会话关闭成功
✓ 租户1配置获取成功
✓ 租户1数据库连接池移除成功
✓ 租户1存在检查(移除后): False

==================================================
测试主从数据库连接
==================================================
✓ 租户2主从数据库连接池添加成功
✓ 租户2主库会话获取成功
✓ 租户2从库会话获取成功
✓ 租户2数据库连接池移除成功

==================================================
测试多租户并发连接
==================================================
✓ 租户3数据库连接池添加成功
✓ 租户4数据库连接池添加成功
✓ 租户5数据库连接池添加成功
✓ 租户4会话获取成功
✓ 租户5会话获取成功
✓ 租户3会话关闭成功
✓ 租户4会话关闭成功
✓ 租户5会话关闭成功
✓ 租户3数据库连接池移除成功
✓ 租户4数据库连接池移除成功
✓ 租户5数据库连接池移除成功

==================================================
所有测试完成
==================================================
✓ 所有数据库连接池已关闭
```

所有测试均通过，多租户数据库连接池功能正常。

## 性能优化

1. **连接池管理**
   - 每个租户独立的连接池，避免连接竞争
   - 支持连接池大小和溢出配置
   - 连接自动回收机制（pool_recycle）

2. **读写分离**
   - 读操作使用从库，减轻主库压力
   - 写操作使用主库，保证数据一致性
   - 灵活配置，支持无从库模式

3. **单例模式**
   - TenantDatabasePool使用单例模式，全局唯一
   - 避免重复创建连接池
   - 统一管理所有租户数据库连接

## 安全性

1. **租户隔离**
   - 每个租户独立的数据库连接
   - 租户ID从JWT token中获取，确保安全
   - 租户管理模块使用主库，业务模块使用租户库

2. **连接管理**
   - 连接池自动管理连接生命周期
   - 支持动态添加和移除租户数据库
   - 应用关闭时自动释放所有连接

## 后续优化建议

1. **缓存优化**
   - 使用Redis缓存租户数据库配置
   - 减少数据库查询次数

2. **监控告警**
   - 监控连接池使用情况
   - 连接池耗尽时自动扩容
   - 异常连接自动剔除

3. **负载均衡**
   - 支持多个从库的负载均衡
   - 根据从库负载动态路由

4. **数据库迁移**
   - 支持租户数据库的自动创建和迁移
   - 提供租户数据库初始化脚本
