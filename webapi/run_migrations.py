import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from app.initializer._conf import init_config

def run_migrations():
    config = init_config()
    
    db_url = f"postgresql://{config.db_username}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_database}"
    
    engine = create_engine(db_url)
    conn = engine.connect()
    
    try:
        with conn.begin():
            print("开始执行数据库迁移...")
            
            inspector = inspect(engine)
            
            tables = ['inbound_pick_putaway_item', 'inbound_receipt_item', 
                     'outbound_order_item', 'outbound_pick_putaway_item', 'outbound_receipt_item']
            
            for table in tables:
                columns = [col['name'] for col in inspector.get_columns(table)]
                
                if 'spu_code' not in columns:
                    print(f"添加 spu_code 字段到 {table}")
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN spu_code VARCHAR(64) NOT NULL DEFAULT ''"))
                
                if 'spu_name' not in columns:
                    print(f"添加 spu_name 字段到 {table}")
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN spu_name VARCHAR(128) NOT NULL DEFAULT ''"))
                
                if 'sku_code' not in columns:
                    print(f"添加 sku_code 字段到 {table}")
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN sku_code VARCHAR(64) NOT NULL DEFAULT ''"))
                
                if 'sku_name' not in columns:
                    print(f"添加 sku_name 字段到 {table}")
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN sku_name VARCHAR(128) NOT NULL DEFAULT ''"))
                
                if 'batch_no' not in columns:
                    print(f"添加 batch_no 字段到 {table}")
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN batch_no VARCHAR(64) NOT NULL DEFAULT ''"))
                
                if 'production_date' not in columns:
                    print(f"添加 production_date 字段到 {table}")
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN production_date BIGINT NOT NULL DEFAULT 0"))
            
            if 'inbound_putaway_task' not in inspector.get_table_names():
                print("创建 inbound_putaway_task 表")
                conn.execute(text("""
                    CREATE TABLE inbound_putaway_task (
                        id INTEGER NOT NULL,
                        pick_putaway_item_id INTEGER NOT NULL,
                        putaway_qty INTEGER NOT NULL DEFAULT 0,
                        weight NUMERIC(10,2) NOT NULL DEFAULT 0,
                        volume NUMERIC(10,2) NOT NULL DEFAULT 0,
                        price NUMERIC(10,2) NOT NULL DEFAULT 0,
                        expiry_date BIGINT NOT NULL DEFAULT 0,
                        batch_no VARCHAR(64) NOT NULL DEFAULT '',
                        production_date BIGINT NOT NULL DEFAULT 0,
                        goods_location_id INTEGER NOT NULL DEFAULT 0,
                        warehouse_id INTEGER NOT NULL DEFAULT 0,
                        warehouse_name VARCHAR(100) NOT NULL DEFAULT '',
                        warehouse_area_id INTEGER NOT NULL DEFAULT 0,
                        warehouse_area_name VARCHAR(100) NOT NULL DEFAULT '',
                        warehouse_location_name VARCHAR(100) NOT NULL DEFAULT '',
                        putaway_person_id INTEGER NOT NULL DEFAULT 0,
                        putaway_person VARCHAR(64) NOT NULL DEFAULT '',
                        putaway_time BIGINT NOT NULL DEFAULT 0,
                        series_number VARCHAR(100) NOT NULL DEFAULT '',
                        tenant_id VARCHAR(36) NOT NULL DEFAULT '',
                        creator VARCHAR(64) NOT NULL DEFAULT '',
                        create_time BIGINT NOT NULL DEFAULT 0,
                        last_update_time BIGINT NOT NULL DEFAULT 0,
                        PRIMARY KEY (id),
                        FOREIGN KEY (pick_putaway_item_id) REFERENCES inbound_pick_putaway_item(id)
                    )
                """))
                conn.execute(text("CREATE SEQUENCE IF NOT EXISTS inbound_putaway_task_id_seq"))
                conn.execute(text("ALTER TABLE inbound_putaway_task ALTER COLUMN id SET DEFAULT nextval('inbound_putaway_task_id_seq')"))
            else:
                columns = [col['name'] for col in inspector.get_columns('inbound_putaway_task')]
                
                if 'batch_no' not in columns:
                    print(f"添加 batch_no 字段到 inbound_putaway_task")
                    conn.execute(text("ALTER TABLE inbound_putaway_task ADD COLUMN batch_no VARCHAR(64) NOT NULL DEFAULT ''"))
                
                if 'production_date' not in columns:
                    print(f"添加 production_date 字段到 inbound_putaway_task")
                    conn.execute(text("ALTER TABLE inbound_putaway_task ADD COLUMN production_date BIGINT NOT NULL DEFAULT 0"))
            
            if 'inbound_order_item' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('inbound_order_item')]
                
                if 'batch_no' not in columns:
                    print(f"添加 batch_no 字段到 inbound_order_item")
                    conn.execute(text("ALTER TABLE inbound_order_item ADD COLUMN batch_no VARCHAR(64) NOT NULL DEFAULT ''"))
                
                if 'production_date' not in columns:
                    print(f"添加 production_date 字段到 inbound_order_item")
                    conn.execute(text("ALTER TABLE inbound_order_item ADD COLUMN production_date BIGINT NOT NULL DEFAULT 0"))
                
                if 'spu_code' not in columns:
                    print(f"添加 spu_code 字段到 inbound_order_item")
                    conn.execute(text("ALTER TABLE inbound_order_item ADD COLUMN spu_code VARCHAR(64) NOT NULL DEFAULT ''"))
                
                if 'spu_name' not in columns:
                    print(f"添加 spu_name 字段到 inbound_order_item")
                    conn.execute(text("ALTER TABLE inbound_order_item ADD COLUMN spu_name VARCHAR(128) NOT NULL DEFAULT ''"))
                
                if 'sku_code' not in columns:
                    print(f"添加 sku_code 字段到 inbound_order_item")
                    conn.execute(text("ALTER TABLE inbound_order_item ADD COLUMN sku_code VARCHAR(64) NOT NULL DEFAULT ''"))
                
                if 'sku_name' not in columns:
                    print(f"添加 sku_name 字段到 inbound_order_item")
                    conn.execute(text("ALTER TABLE inbound_order_item ADD COLUMN sku_name VARCHAR(128) NOT NULL DEFAULT ''"))
            
            if 'sku' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('sku')]
                
                if 'shelf_life' not in columns:
                    print(f"添加 shelf_life 字段到 sku")
                    conn.execute(text("ALTER TABLE sku ADD COLUMN shelf_life SMALLINT NOT NULL DEFAULT 0"))
                
                if 'production_date' in columns:
                    print(f"删除 sku 表中的 production_date 字段")
                    conn.execute(text("ALTER TABLE sku DROP COLUMN production_date"))
            
            if 'stock' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('stock')]
                
                if 'batch_no' not in columns:
                    print(f"添加 batch_no 字段到 stock")
                    conn.execute(text("ALTER TABLE stock ADD COLUMN batch_no VARCHAR(64) NOT NULL DEFAULT ''"))
                
                if 'production_date' not in columns:
                    print(f"添加 production_date 字段到 stock")
                    conn.execute(text("ALTER TABLE stock ADD COLUMN production_date BIGINT NOT NULL DEFAULT 0"))
            
            if 'inbound_order' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('inbound_order')]
                
                if 'pick_putaway_no' not in columns:
                    print(f"添加 pick_putaway_no 字段到 inbound_order")
                    conn.execute(text("ALTER TABLE inbound_order ADD COLUMN pick_putaway_no VARCHAR(64) NOT NULL DEFAULT ''"))
            
            if 'inbound_pick_putaway' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('inbound_pick_putaway')]
                
                if 'order_nos' not in columns:
                    print(f"添加 order_nos 字段到 inbound_pick_putaway")
                    conn.execute(text("ALTER TABLE inbound_pick_putaway ADD COLUMN order_nos VARCHAR(512) NOT NULL DEFAULT ''"))
            
            if 'inbound_pick_putaway_item' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('inbound_pick_putaway_item')]
                
                if 'order_item_ids' not in columns:
                    print(f"添加 order_item_ids 字段到 inbound_pick_putaway_item")
                    conn.execute(text("ALTER TABLE inbound_pick_putaway_item ADD COLUMN order_item_ids VARCHAR(512) NOT NULL DEFAULT ''"))
            
            print("数据库迁移完成！")
            
    except Exception as e:
        print(f"迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    run_migrations()
