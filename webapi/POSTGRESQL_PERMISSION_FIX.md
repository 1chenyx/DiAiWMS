# PostgreSQL数据库权限问题解决方案

## 问题描述

启动服务时遇到权限错误：
```
sqlalchemy.exc.ProgrammingError: (sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.InsufficientPrivilegeError'>: 对模式 public 权限不够
```

## 原因

PostgreSQL用户"WMS"没有足够的权限在public模式下创建表。

## 解决方案

### 方案1：给WMS用户授予CREATE权限（推荐）

以postgres超级用户身份连接到PostgreSQL数据库，执行以下SQL：

```sql
-- 连接到WMS数据库
\c WMS

-- 授予WMS用户在public模式下的CREATE权限
GRANT CREATE ON SCHEMA public TO WMS;

-- 授予WMS用户在public模式下的所有权限
GRANT ALL ON SCHEMA public TO WMS;

-- 授予WMS用户在WMS数据库上的连接权限
GRANT CONNECT ON DATABASE WMS TO WMS;

-- 授予WMS用户在public模式下现有表的权限
GRANT ALL ON ALL TABLES IN SCHEMA public TO WMS;

-- 授予WMS用户在public模式下现有序列的权限
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO WMS;

-- 授予WMS用户在public模式下未来创建的表的权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO WMS;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO WMS;
```

### 方案2：使用postgres超级用户

修改配置文件使用postgres超级用户：

```yaml
# 修改 config/app_dev.yaml
db_username: postgres
db_password: "你的postgres密码"
```

### 方案3：创建专用数据库管理员用户

创建一个具有足够权限的数据库管理员用户：

```sql
-- 以postgres用户连接
CREATE USER wms_admin WITH PASSWORD 'admin_password';

-- 授予超级用户权限
ALTER USER wms_admin WITH SUPERUSER;

-- 授予WMS数据库的所有权限
GRANT ALL PRIVILEGES ON DATABASE WMS TO wms_admin;
```

然后修改配置文件使用wms_admin用户：

```yaml
db_username: wms_admin
db_password: "admin_password"
```

## 推荐方案

**方案1**是最推荐的方式，因为它：
1. 遵循最小权限原则
2. 安全性更高
3. 不会过度授权

## 执行步骤

1. 使用psql连接到PostgreSQL：
```bash
psql -h localhost -p 5432 -U postgres -d WMS
```

2. 执行方案1中的SQL语句

3. 重新启动服务

## 验证权限

执行完权限授予后，可以使用以下SQL验证：

```sql
-- 检查WMS用户的权限
SELECT * FROM information_schema.role_table_grants 
WHERE grantee = 'wms' AND table_schema = 'public';

-- 检查WMS用户的模式权限
SELECT * FROM information_schema.schema_privileges 
WHERE grantee = 'wms' AND schema_name = 'public';
```

## 注意事项

1. **安全性**：不要在生产环境中使用超级用户运行应用
2. **最小权限**：只授予必要的权限
3. **密码安全**：确保数据库密码安全存储
4. **连接池**：确保连接池大小适合数据库配置
