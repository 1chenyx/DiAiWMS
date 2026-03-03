import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.utils.md5_util import md5_encrypt_32


async def create_test_data():
    master_db_url = "postgresql+asyncpg://WMS:123456@localhost:5432/WMS"
    
    print("=" * 80)
    print("创建测试数据（租户ID使用UUID）")
    print("=" * 80)
    
    master_engine = create_async_engine(master_db_url, echo=False)
    master_session_maker = sessionmaker(master_engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with master_session_maker() as session:
            print("\n1. 在主库插入租户数据（租户编号: 001）")
            print("-" * 80)
            
            tenant_id = "00000000-0000-0000-0000-000000000001"
            
            await session.execute(text("""
                INSERT INTO tenant (
                    id, tenant_name, tenant_code, contact_person, contact_phone,
                    contact_email, address, description, db_drivername, db_database,
                    db_username, db_password, db_host, db_port, db_charset,
                    db_pool_size, db_max_overflow, db_pool_recycle, slave_host,
                    slave_port, is_valid, creator, create_time, last_update_time
                ) VALUES (
                    :id, :tenant_name, :tenant_code, :contact_person, :contact_phone,
                    :contact_email, :address, :description, :db_drivername, :db_database,
                    :db_username, :db_password, :db_host, :db_port, :db_charset,
                    :db_pool_size, :db_max_overflow, :db_pool_recycle, :slave_host,
                    :slave_port, :is_valid, :creator, :create_time, :last_update_time
                ) ON CONFLICT (id) DO UPDATE SET
                    tenant_name = EXCLUDED.tenant_name,
                    tenant_code = EXCLUDED.tenant_code,
                    last_update_time = EXCLUDED.last_update_time
            """), {
                "id": tenant_id,
                "tenant_name": "测试租户001",
                "tenant_code": "001",
                "contact_person": "管理员",
                "contact_phone": "13800138000",
                "contact_email": "admin@example.com",
                "address": "测试地址",
                "description": "用于测试的租户",
                "db_drivername": "postgresql+asyncpg",
                "db_database": "WMS",
                "db_username": "WMS",
                "db_password": "123456",
                "db_host": "localhost",
                "db_port": 5432,
                "db_charset": "utf8",
                "db_pool_size": 10,
                "db_max_overflow": 5,
                "db_pool_recycle": 3600,
                "slave_host": None,
                "slave_port": None,
                "is_valid": True,
                "creator": "system",
                "create_time": 1740720000,
                "last_update_time": 1740720000
            })
            
            await session.commit()
            print("✓ 租户数据插入成功")
            print(f"  租户ID: {tenant_id}")
            print(f"  租户编号: 001")
            print(f"  租户名称: 测试租户001")
            print(f"  数据库名称: WMS (使用主库)")
            
        print("\n2. 在主库插入用户数据（使用主库作为租户库）")
        print("-" * 80)
        
        async with master_session_maker() as session:
            md5_password = md5_encrypt_32("123456")
            
            await session.execute(text("""
                INSERT INTO userrole (
                    id, role_name, create_time, last_update_time, is_valid, tenant_id
                ) VALUES (
                    1, 'admin', 1740720000, 1740720000, true, :tenant_id
                ) ON CONFLICT (id) DO UPDATE SET
                    role_name = EXCLUDED.role_name,
                    last_update_time = EXCLUDED.last_update_time
            """), {"tenant_id": tenant_id})
            
            await session.execute(text("""
                DELETE FROM "user" WHERE user_num = 'admin'
            """))
            
            await session.execute(text("""
                INSERT INTO "user" (
                    user_num, user_name, contact_tel, user_role, sex, is_valid,
                    auth_string, email, creator, create_time, last_update_time, tenant_id
                ) VALUES (
                    'admin', 'admin', '13800138000', 'admin', '男', true,
                    :password, 'admin@example.com', 'system', 1740720000, 1740720000, :tenant_id
                )
            """), {"password": md5_password, "tenant_id": tenant_id})
            
            await session.commit()
            print("✓ 用户数据插入成功")
            print(f"  用户名: admin")
            print(f"  密码: 123456 (MD5: {md5_password})")
            print(f"  用户角色: admin")
            print(f"  租户ID: {tenant_id}")
        
    except Exception as e:
        print(f"\n✗ 创建测试数据失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await master_engine.dispose()
    
    print("\n" + "=" * 80)
    print("测试数据创建完成！")
    print("=" * 80)
    print("\n登录信息：")
    print("  租户编号: 001")
    print("  用户名: admin")
    print("  密码: 123456")
    print("\n说明：")
    print("  - 租户ID: 00000000-0000-0000-0000-000000000001")
    print("  - 租户数据库: 使用主库WMS")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(create_test_data())
