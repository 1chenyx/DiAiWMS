"""add warehouse and sku fields to stock table

Revision ID: 012
Revises: 011
Create Date: 2026-03-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('stock')]
    
    if 'warehouse_id' not in columns:
        op.add_column('stock', sa.Column('warehouse_id', sa.BigInteger(), nullable=False, server_default='0'))
        op.execute("UPDATE stock SET warehouse_id = 0 WHERE warehouse_id IS NULL")
    
    if 'warehouse_name' not in columns:
        op.add_column('stock', sa.Column('warehouse_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE stock SET warehouse_name = '' WHERE warehouse_name IS NULL")
    
    if 'warehouse_area_id' not in columns:
        op.add_column('stock', sa.Column('warehouse_area_id', sa.BigInteger(), nullable=False, server_default='0'))
        op.execute("UPDATE stock SET warehouse_area_id = 0 WHERE warehouse_area_id IS NULL")
    
    if 'warehouse_area_name' not in columns:
        op.add_column('stock', sa.Column('warehouse_area_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE stock SET warehouse_area_name = '' WHERE warehouse_area_name IS NULL")
    
    if 'warehouse_location_name' not in columns:
        op.add_column('stock', sa.Column('warehouse_location_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE stock SET warehouse_location_name = '' WHERE warehouse_location_name IS NULL")
    
    if 'spu_name' not in columns:
        op.add_column('stock', sa.Column('spu_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE stock SET spu_name = '' WHERE spu_name IS NULL")
    
    if 'sku_code' not in columns:
        op.add_column('stock', sa.Column('sku_code', sa.String(50), nullable=False, server_default=''))
        op.execute("UPDATE stock SET sku_code = '' WHERE sku_code IS NULL")
    
    if 'sku_name' not in columns:
        op.add_column('stock', sa.Column('sku_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE stock SET sku_name = '' WHERE sku_name IS NULL")


def downgrade() -> None:
    op.drop_column('stock', 'sku_name')
    op.drop_column('stock', 'sku_code')
    op.drop_column('stock', 'spu_name')
    op.drop_column('stock', 'warehouse_location_name')
    op.drop_column('stock', 'warehouse_area_name')
    op.drop_column('stock', 'warehouse_area_id')
    op.drop_column('stock', 'warehouse_name')
    op.drop_column('stock', 'warehouse_id')