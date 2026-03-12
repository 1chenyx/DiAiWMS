---
name: "fastapi-crud"
description: "Guides FastAPI CRUD API development following project conventions. Invoke when creating or modifying API endpoints."
---

# FastAPI CRUD API 开发指南

本技能提供完整的FastAPI增删改查接口开发指导，严格遵循项目统一风格。

## 项目架构概览

```
app/
├── api/
│   ├── v1/tenant/          # 租户模块API
│   │   └── xxx.py          # 业务API路由
│   ├── dependencies.py     # 依赖注入（认证、数据库）
│   ├── responses.py        # 统一响应格式
│   └── service_dependencies.py  # Service依赖注入
├── schemas/                # Pydantic视图模型
│   └── xxx.py
├── services/               # 业务逻辑层
│   └── xxx_service.py
└── repositories/           # 数据访问层
    └── xxx_repository.py
```

## 依赖注入体系

### 1. 数据库会话注入

```python
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.core.current_user import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

# 方式一：直接注入数据库会话（推荐用于复杂查询）
async def get_xxx(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    pass
```

### 2. Service依赖注入

```python
from app.api.service_dependencies import get_service_dependency
from app.services.xxx_service import XxxService

# 方式二：注入Service实例（推荐用于标准CRUD）
async def get_xxx(
    service: XxxService = Depends(get_service_dependency(XxxService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    pass
```

### 3. CurrentUser类型

```python
from app.core.current_user import CurrentUser

class CurrentUser(BaseModel):
    user_id: int = 0           # 用户ID
    user_num: str = ""         # 用户编号
    user_name: str = ""        # 用户名称
    user_role: str = ""        # 用户角色
    tenant_id: str = ""        # 租户ID（关键：用于数据隔离）
    userrole_id: int = 0      # 用户角色ID
    is_authenticated: bool = False  # 是否已认证
```

## 统一响应格式

### 响应函数

```python
from app.api.responses import success_response, error_response

# 成功响应
return success_response(data)
return success_response(data, msg="操作成功")
return success_response({"id": 123, "name": "xxx"})

# 失败响应
return error_response("错误信息")
return error_response(msg="操作失败", code=400)
```

### 响应格式示例

```json
// 成功响应
{
    "isSuccess": true,
    "msg": "操作成功",
    "code": 0,
    "data": { ... }
}

// 失败响应
{
    "isSuccess": false,
    "msg": "错误信息",
    "code": 400,
    "error": "详细错误信息"
}
```

## Schema定义模式

### 文件位置
`app/schemas/xxx.py`

### 视图模型模板

```python
from typing import Optional
from pydantic import BaseModel, Field


class XxxViewModel(BaseModel):
    """用于接口返回的视图模型"""
    id: int = Field(default=0, description="主键ID")
    field1: str = Field(default="", description="字段1")
    field2: int = Field(default=0, description="字段2")
    tenant_id: str = Field(default="", description="租户ID")


class XxxCreateViewModel(BaseModel):
    """用于创建操作的视图模型"""
    field1: str = Field(..., description="字段1（必填）")
    field2: int = Field(default=0, description="字段2（可选）")
    field3: Optional[str] = Field(default="", description="字段3")


class XxxUpdateViewModel(BaseModel):
    """用于更新操作的视图模型"""
    id: int = Field(..., description="主键ID（必填）")
    field1: Optional[str] = Field(None, description="字段1")
    field2: Optional[int] = Field(None, description="字段2")
```

### 设计原则

- **ViewModel**: 返回给前端的完整数据，字段都有默认值
- **CreateViewModel**: 创建时需要提交的字段，必填字段用`...`，可选字段用`default=`
- **UpdateViewModel**: 更新时提交的字段，必填字段用`...`，其他字段用`Optional`

## Router开发模板

### 标准CRUD接口文件结构

```python
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.xxx import (
    XxxViewModel,
    XxxCreateViewModel,
    XxxUpdateViewModel
)
from app.services.xxx_service import XxxService
from app.api.service_dependencies import get_service_dependency
from app.api.responses import success_response, error_response
from app.api.dependencies import get_current_user
from app.core.current_user import CurrentUser

router = APIRouter()


# ==================== 查询接口 ====================

@router.get("/xxx", response_model=XxxViewModel)
async def get_xxx(
    id: int = Query(..., description="XXX ID"),
    service: XxxService = Depends(get_service_dependency(XxxService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    根据ID获取XXX信息
    
    Args:
        id: XXX ID
        service: XXX服务
        current_user: 当前用户
        
    Returns:
        XXX信息
    """
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.get("/xxx/list", response_model=List[XxxViewModel])
async def get_xxx_list(
    service: XxxService = Depends(get_service_dependency(XxxService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取所有XXX列表
    
    Args:
        service: XXX服务
        current_user: 当前用户
        
    Returns:
        XXX列表
    """
    result = await service.get_all(current_user)
    return success_response(result)


@router.get("/xxx/page")
async def get_xxx_page(
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    # 查询参数
    field1: Optional[str] = Query(None, description="字段1"),
    field2: Optional[int] = Query(None, description="字段2"),
    service: XxxService = Depends(get_service_dependency(XxxService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询XXX列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        field1: 字段1（模糊查询）
        field2: 字段2
        service: XXX服务
        current_user: 当前用户
        
    Returns:
        XXX列表和总数
    """
    search_params = {}
    if field1:
        search_params["field1"] = field1
    if field2:
        search_params["field2"] = field2
    
    data, totals = await service.page_search(
        page_index, page_size, search_params, current_user
    )
    
    return success_response({
        "data": data,
        "totals": totals,
        "page_index": page_index,
        "page_size": page_size
    })


# ==================== 创建接口 ====================

@router.post("/xxx", response_model=XxxViewModel)
async def create_xxx(
    view_model: XxxCreateViewModel,
    service: XxxService = Depends(get_service_dependency(XxxService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建XXX
    
    Args:
        view_model: XXX创建数据
        service: XXX服务
        current_user: 当前用户
        
    Returns:
        创建的XXX信息
    """
    id, msg = await service.add(view_model, current_user)
    
    if id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(id)
    return success_response(result)


# ==================== 更新接口 ====================

@router.post("/xxx/update", response_model=XxxViewModel)
async def update_xxx(
    view_model: XxxUpdateViewModel,
    service: XxxService = Depends(get_service_dependency(XxxService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    更新XXX
    
    Args:
        view_model: XXX更新数据
        service: XXX服务
        current_user: 当前用户
        
    Returns:
        更新后的XXX信息
    """
    flag, msg = await service.update(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(view_model.id, current_user)
    return success_response(result)


# ==================== 删除接口 ====================

@router.post("/xxx/delete")
async def delete_xxx(
    id: int = Query(..., description="XXX ID"),
    service: XxxService = Depends(get_service_dependency(XxxService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    删除XXX
    
    Args:
        id: XXX ID
        service: XXX服务
        current_user: 当前用户
        
    Returns:
        删除结果
    """
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response({"id": id})
```

## 接口命名规范

### 1. URL路径规范

- **小写字母 + 中划线分隔**: `/xxx/yyy-zzz`
- **避免驼峰和下划线**

```python
# ✅ 正确
@router.get("/warehouse-location")
@router.get("/inbound-order")
@router.post("/stock-update")

# ❌ 错误
@router.get("/warehouseLocation")  # 驼峰
@router.get("/warehouse_location")  # 下划线
```

### 2. HTTP方法规范

| 操作 | HTTP方法 | URL模式 |
|------|----------|---------|
| 获取单条 | GET | `/xxx` |
| 获取列表 | GET | `/xxx/list` |
| 分页查询 | GET | `/xxx/page` |
| 创建 | POST | `/xxx` |
| 更新 | POST | `/xxx/update` |
| 删除 | POST | `/xxx/delete` |

### 3. Query参数规范

```python
# 必填参数
id: int = Query(..., description="ID")

# 可选参数
name: Optional[str] = Query(None, description="名称")

# 带校验的可选参数
page_index: int = Query(1, ge=1, description="页码")
page_size: int = Query(10, ge=1, le=100, description="每页数量")
```

## 分页查询规范

### 返回格式

```python
return success_response({
    "data": data,           # 数据列表
    "totals": totals,       # 总数量
    "page_index": page_index,  # 当前页码
    "page_size": page_size     # 每页大小
})
```

### 前端参数规范

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page_index | int | 是 | 页码，从1开始 |
| page_size | int | 是 | 每页数量（建议10/20/50/100） |

## Service层开发模式

### 标准CRUD方法返回值约定

```python
# 添加记录
id, msg = await service.add(view_model, current_user)
# 返回: (新记录ID, 错误消息)，ID为0表示失败

# 更新记录  
flag, msg = await service.update(id, view_model, current_user)
# 返回: (是否成功, 错误消息)

# 删除记录
flag, msg = await service.delete(id, current_user)
# 返回: (是否成功, 错误消息)

# 查询单条
result = await service.get_by_id(id, current_user)
# 返回: 实体对象或None

# 查询列表
result = await service.get_all(current_user)
# 返回: 实体列表
```

### 关键：传递CurrentUser

所有涉及业务数据的Service方法都需要接收`current_user`参数，用于：
1. 获取`tenant_id`进行数据隔离
2. 获取`user_id`记录操作人
3. 权限验证

```python
# Service方法示例
async def get_by_id(self, id: int, current_user: CurrentUser):
    # 内部会自动添加 tenant_id 过滤
    return await self.get_one_by_tenant(self._repository._model, current_user.tenant_id, {"id": id})
```

## 路由注册

### 在main.py中注册

```python
from app.api.v1.tenant import stock, warehouse, sku

def create_app():
    app = FastAPI()
    
    # 注册路由
    api_router = APIRouter()
    api_router.include_router(stock.router, tags=["库存管理"])
    api_router.include_router(warehouse.router, tags=["仓库管理"])
    api_router.include_router(sku.router, tags=["SKU管理"])
    
    app.include_router(api_router, prefix="/api/v1/tenant")
    
    return app
```

## 最佳实践

### 1. 依赖注入优先

```python
# ✅ 推荐：使用Service依赖注入
async def get_xxx(
    service: XxxService = Depends(get_service_dependency(XxxService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    return await service.get_by_id(id, current_user)

# ⚠️ 仅在需要自定义查询时使用直接数据库注入
async def get_xxx_custom(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    # 自定义复杂查询逻辑
    pass
```

### 2. 必填参数使用...

```python
# ✅ 正确
id: int = Query(..., description="ID")
view_model: XxxCreateViewModel

# ❌ 错误
id: int = Query(None, description="ID")  # 必填不能用None
```

### 3. 分页参数校验

```python
page_index: int = Query(1, ge=1, description="页码")  # 最小值为1
page_size: int = Query(10, ge=1, le=100, description="每页数量")  # 限制最大值
```

### 4. 描述清晰完整

```python
@router.get("/xxx")
async def get_xxx(
    id: int = Query(..., description="XXX ID"),  # ✅ 有描述
    # ❌ 缺少描述
    id: int = Query(...),
):
```

### 5. 添加接口文档注释

```python
@router.get("/xxx")
async def get_xxx(...):
    """
    根据ID获取XXX信息
    
    Args:
        id: XXX ID
        service: XXX服务
        current_user: 当前用户
        
    Returns:
        XXX信息
    """
```

### 6. 响应模型注解

```python
# 返回单条
@router.get("/xxx", response_model=XxxViewModel)

# 返回列表
@router.get("/xxx/list", response_model=List[XxxViewModel])

# 无固定返回格式（使用success_response包装）
@router.get("/xxx/page")
```

## 常见错误模式（避免）

### 1. 缺少tenant_id过滤

```python
# ❌ 错误：查询所有数据
result = await service.get_all()

# ✅ 正确：按租户过滤
result = await service.get_all(current_user)
```

### 2. 缺少认证依赖

```python
# ❌ 错误：未验证用户身份
async def get_xxx(id: int):
    pass

# ✅ 正确：验证用户身份
async def get_xxx(
    id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    pass
```

### 3. 错误响应格式不一致

```python
# ❌ 错误：直接返回字典
return {"error": "错误信息"}

# ✅ 正确：使用统一响应函数
return error_response("错误信息")

# ✅ 正确：使用HTTPException
from fastapi import HTTPException
raise HTTPException(status_code=404, detail="记录不存在")
```

### 4. 路径命名不一致

```python
# ❌ 错误
@router.post("/xxxUpdate")
@router.get("/getXxxList")

# ✅ 正确
@router.post("/xxx/update")
@router.get("/xxx/list")
```

## 开发流程 Checklist

- [ ] 创建Schema文件（ViewModel、CreateViewModel、UpdateViewModel）
- [ ] 创建或扩展Service方法
- [ ] 创建API Router文件
- [ ] 实现GET /xxx（单条查询）
- [ ] 实现GET /xxx/list（列表查询）
- [ ] 实现GET /xxx/page（分页查询）
- [ ] 实现POST /xxx（创建）
- [ ] 实现POST /xxx/update（更新）
- [ ] 实现POST /xxx/delete（删除）
- [ ] 在main.py中注册路由
- [ ] 测试各接口
