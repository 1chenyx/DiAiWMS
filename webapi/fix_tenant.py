import asyncio
import asyncpg

async def fix_tenant_config():
    print("Fixing tenant configuration...")
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='WMS',
            password='123456',
            database='WMS'
        )
        
        await conn.execute("""
            UPDATE tenant 
            SET db_database = 'WMS'
            WHERE tenant_code = '001'
        """)
        
        print("Tenant configuration updated successfully!")
        
        result = await conn.fetchrow("SELECT id, tenant_code, db_database FROM tenant WHERE tenant_code = '001'")
        print(f"Updated tenant: id={result['id']}, code={result['tenant_code']}, db={result['db_database']}")
        
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_tenant_config())
