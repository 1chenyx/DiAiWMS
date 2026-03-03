import asyncio
import asyncpg

async def check_tenant_config():
    print("Checking tenant configuration...")
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='WMS',
            password='123456',
            database='WMS'
        )
        
        result = await conn.fetchrow("SELECT * FROM tenant WHERE tenant_code = '001'")
        if result:
            print("Tenant configuration:")
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print("Tenant not found!")
        
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_tenant_config())
