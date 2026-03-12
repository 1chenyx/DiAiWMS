---
name: "sqlalchemy-db"
description: "Guides SQLAlchemy database operations with tenant isolation. Invoke when creating models, repositories, services, or performing CRUD operations on business data."
---

# SQLAlchemy Database Operations

This skill provides comprehensive guidance for implementing database operations using SQLAlchemy in this WMS project, with a strong focus on **multi-tenant data isolation**.

## Core Principles

### 1. Tenant Isolation (CRITICAL)
**ALL business data tables MUST include `tenant_id` field for multi-tenant isolation.**

- Field definition: `tenant_id = mapped_column(String(36), nullable=False, comment="租户ID")`
- All queries on business data MUST filter by `tenant_id`
- All create/update operations MUST set/validate `tenant_id`

### 2. Architecture Layers
- **Model Layer**: Database entity definitions (`app/models/entities/`)
- **Repository Layer**: Data access operations (`app/repositories/`)
- **Service Layer**: Business logic (`app/services/`)

## Creating Models

### Base Model
All models inherit from `WMSBaseModel` which provides:
- `id`: Primary key (Integer, auto-increment)

### Model Template for Business Data

```python
from datetime import datetime
from sqlalchemy import String, BigInteger, Boolean, Numeric
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class YourEntity(WMSBaseModel):
    """
    Entity description
    """
    __tablename__ = "your_table_name"

    # Business fields
    field1 = mapped_column(String(100), nullable=False, default="", comment="字段1说明")
    field2 = mapped_column(BigInteger, nullable=False, default=0, comment="字段2说明")
    field3 = mapped_column(Boolean, nullable=False, default=False, comment="字段3说明")
    
    # CRITICAL: Tenant ID for multi-tenant isolation
    tenant_id = mapped_column(String(36), nullable=False, comment="租户ID")
    
    # Common audit fields (optional)
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
```

### Key Points
1. **ALWAYS** include `tenant_id` for business data
2. Use `mapped_column` (SQLAlchemy 2.0 style)
3. Provide meaningful `comment` for each field
4. Set appropriate `nullable` and `default` values
5. Use lambda for timestamp defaults: `default=lambda: int(datetime.now().timestamp())`

## Creating Repositories

### Repository Template

```python
from app.repositories.base_repository import BaseRepository
from app.models.entities import YourEntity


class YourEntityRepository(BaseRepository[YourEntity]):
    """
    Repository for YourEntity
    """
    def __init__(self, db_session):
        super().__init__(YourEntity, db_session)
```

### Base Repository Methods Available
- `get_by_id(id)` - Get single record by ID
- `get_all(filters, order_by, limit)` - Get all records with filters
- `get_by_field(field_name, field_value)` - Get by single field
- `get_by_fields(filters)` - Get by multiple fields
- `count(filters)` - Count records
- `exists(id)` - Check if record exists
- `create(**kwargs)` - Create new record
- `update(id, **kwargs)` - Update record
- `delete(id)` - Delete record
- `page_query(page_index, page_size, filters, order_by)` - Paginated query

## Creating Services

### Service Template for Business Data

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import YourEntity
from app.repositories.your_entity_repository import YourEntityRepository
from app.services.base_service import TenantAwareService


class YourEntityService(TenantAwareService[YourEntityRepository, YourEntity]):
    """
    Service for YourEntity business logic
    """
    def __init__(self, db_session: AsyncSession):
        repository = YourEntityRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session
```

### Tenant-Aware Service Methods Available
- `get_by_tenant(tenant_id, filters, order_by, limit)` - Get records by tenant
- `count_by_tenant(tenant_id, filters)` - Count records by tenant
- `page_query_by_tenant(page_index, page_size, tenant_id, filters, order_by)` - Paginated query by tenant
- `create_with_tenant(tenant_id, **kwargs)` - Create with tenant ID
- `update_with_tenant(id, tenant_id, **kwargs)` - Update with tenant validation
- `query_by_tenant(tenant_id, filters, order_by, limit)` - Generic query by tenant
- `get_one_by_tenant(tenant_id, filters)` - Get single record by tenant
- `query_entity_by_tenant(entity_class, tenant_id, filters, order_by, limit)` - Query any entity by tenant
- `get_one_entity_by_tenant(entity_class, tenant_id, filters)` - Get single entity by tenant

## CRUD Operations with Tenant Isolation

### 1. Query Operations

#### Simple Query with Tenant Filter
```python
from sqlalchemy import select

async def get_by_tenant_example(self, current_user: CurrentUser):
    query = select(YourEntity).where(YourEntity.tenant_id == current_user.tenant_id)
    result = await self._db_session.execute(query)
    return result.scalars().all()
```

#### Query with Additional Filters
```python
async def query_with_filters(
    self,
    current_user: CurrentUser,
    status: str = None,
    category_id: int = None
):
    query = select(YourEntity).where(YourEntity.tenant_id == current_user.tenant_id)
    
    if status:
        query = query.where(YourEntity.status == status)
    if category_id:
        query = query.where(YourEntity.category_id == category_id)
    
    result = await self._db_session.execute(query)
    return result.scalars().all()
```

#### Paginated Query
```python
async def page_search(
    self,
    page_index: int,
    page_size: int,
    current_user: CurrentUser,
    search_params: dict = None
):
    from sqlalchemy import func
    
    # Base query with tenant filter
    query = select(YourEntity).where(YourEntity.tenant_id == current_user.tenant_id)
    
    # Apply search filters
    if search_params:
        if "field1" in search_params:
            query = query.where(YourEntity.field1 == search_params["field1"])
        if "field2" in search_params:
            query = query.where(YourEntity.field2 == search_params["field2"])
    
    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await self._db_session.execute(total_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.order_by(YourEntity.last_update_time.desc())
    query = query.offset((page_index - 1) * page_size).limit(page_size)
    
    result = await self._db_session.execute(query)
    rows = result.scalars().all()
    
    return rows, total
```

### 2. Create Operations

#### Using Service Method
```python
async def create_entity(
    self,
    current_user: CurrentUser,
    field1: str,
    field2: int
):
    entity = await self.create_with_tenant(
        tenant_id=current_user.tenant_id,
        field1=field1,
        field2=field2
    )
    return entity
```

#### Direct Repository Creation
```python
async def create_direct(
    self,
    current_user: CurrentUser,
    **kwargs
):
    # Ensure tenant_id is set
    kwargs["tenant_id"] = current_user.tenant_id
    return await self._repository.create(**kwargs)
```

### 3. Update Operations

#### Using Service Method (with tenant validation)
```python
async def update_entity(
    self,
    id: int,
    current_user: CurrentUser,
    **kwargs
):
    # This automatically validates tenant_id
    entity = await self.update_with_tenant(
        id=id,
        tenant_id=current_user.tenant_id,
        **kwargs
    )
    return entity
```

#### Manual Update with Tenant Check
```python
async def update_with_check(
    self,
    id: int,
    current_user: CurrentUser,
    **kwargs
):
    entity = await self.get_by_id(id)
    if not entity:
        return None
    
    # Validate tenant ownership
    if entity.tenant_id != current_user.tenant_id:
        return None
    
    kwargs["tenant_id"] = current_user.tenant_id
    return await self._repository.update(id, **kwargs)
```

### 4. Delete Operations

#### Delete with Tenant Validation
```python
async def delete_entity(
    self,
    id: int,
    current_user: CurrentUser
):
    entity = await self.get_by_id(id)
    if not entity:
        return False
    
    # Validate tenant ownership
    if entity.tenant_id != current_user.tenant_id:
        return False
    
    await self._repository.delete(id)
    return True
```

## Best Practices

### 1. Always Filter by Tenant
```python
# ✅ CORRECT
query = select(Stock).where(Stock.tenant_id == current_user.tenant_id)

# ❌ WRONG - Missing tenant filter
query = select(Stock)
```

### 2. Use TenantAwareService for Business Data
```python
# ✅ CORRECT - For business data with tenant isolation
class StockService(TenantAwareService[StockRepository, Stock]):
    pass

# ✅ CORRECT - For system data without tenant (e.g., Tenant table itself)
class TenantService(BaseService[TenantRepository, Tenant]):
    pass
```

### 3. Validate Tenant in Updates/Deletes
```python
# ✅ CORRECT - Always validate tenant ownership
if entity.tenant_id != current_user.tenant_id:
    raise PermissionError("Access denied")

# ❌ WRONG - No tenant validation
await repository.delete(id)
```

### 4. Set Tenant ID on Creation
```python
# ✅ CORRECT
kwargs["tenant_id"] = current_user.tenant_id
await repository.create(**kwargs)

# ❌ WRONG - Missing tenant_id
await repository.create(**kwargs)
```

### 5. Use Async/Await Properly
```python
# ✅ CORRECT
result = await self._db_session.execute(query)
rows = result.scalars().all()

# ❌ WRONG - Missing await
result = self._db_session.execute(query)
```

### 6. Import CurrentUser Type
```python
from app.core.current_user import CurrentUser
```

## Common Patterns

### Join Query with Tenant Filter
```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def get_with_relations(self, current_user: CurrentUser):
    query = select(YourEntity).where(
        YourEntity.tenant_id == current_user.tenant_id
    ).options(
        selectinload(YourEntity.related_entity)
    )
    result = await self._db_session.execute(query)
    return result.scalars().all()
```

### Bulk Operations with Tenant Filter
```python
from sqlalchemy import update

async def bulk_update_status(
    self,
    ids: List[int],
    status: str,
    current_user: CurrentUser
):
    stmt = update(YourEntity).where(
        YourEntity.id.in_(ids),
        YourEntity.tenant_id == current_user.tenant_id
    ).values(status=status)
    
    await self._db_session.execute(stmt)
    await self._db_session.commit()
```

### Count with Tenant Filter
```python
from sqlalchemy import func, select

async def count_by_status(
    self,
    status: str,
    current_user: CurrentUser
):
    query = select(func.count()).select_from(YourEntity).where(
        YourEntity.tenant_id == current_user.tenant_id,
        YourEntity.status == status
    )
    result = await self._db_session.execute(query)
    return result.scalar()
```

## File Organization

```
app/
├── models/
│   ├── base.py                    # WMSBaseModel
│   └── entities/
│       └── your_entity.py         # Your model
├── repositories/
│   └── your_entity_repository.py  # Your repository
└── services/
    └── your_entity_service.py     # Your service
```

## Checklist for New Database Operations

- [ ] Model includes `tenant_id` field (for business data)
- [ ] Model inherits from `WMSBaseModel`
- [ ] Repository inherits from `BaseRepository`
- [ ] Service inherits from `TenantAwareService` (for business data)
- [ ] All queries filter by `tenant_id`
- [ ] All creates set `tenant_id`
- [ ] All updates/deletes validate `tenant_id`
- [ ] Using async/await properly
- [ ] Proper error handling
- [ ] Meaningful comments and docstrings
