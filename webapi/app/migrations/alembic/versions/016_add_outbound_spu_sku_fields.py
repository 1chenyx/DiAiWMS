"""add spu and sku name fields to outbound tables

Revision ID: 016
Revises: 015
Create Date: 2026-03-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    
    inspector = sa.inspect(conn)
    
    # Update outbound_order_item table
    order_columns = [col['name'] for col in inspector.get_columns('outbound_order_item')]
    
    if 'spu_code' not in order_columns:
        op.add_column('outbound_order_item', sa.Column('spu_code', sa.String(64), nullable=False, server_default=''))
        op.execute("UPDATE outbound_order_item SET spu_code = '' WHERE spu_code IS NULL")
    
    if 'spu_name' not in order_columns:
        op.add_column('outbound_order_item', sa.Column('spu_name', sa.String(128), nullable=False, server_default=''))
        op.execute("UPDATE outbound_order_item SET spu_name = '' WHERE spu_name IS NULL")
    
    if 'sku_code' not in order_columns:
        op.add_column('outbound_order_item', sa.Column('sku_code', sa.String(64), nullable=False, server_default=''))
        op.execute("UPDATE outbound_order_item SET sku_code = '' WHERE sku_code IS NULL")
    
    if 'sku_name' not in order_columns:
        op.add_column('outbound_order_item', sa.Column('sku_name', sa.String(128), nullable=False, server_default=''))
        op.execute("UPDATE outbound_order_item SET sku_name = '' WHERE sku_name IS NULL")
    
    # Update outbound_pick_putaway_item table
    pick_columns = [col['name'] for col in inspector.get_columns('outbound_pick_putaway_item')]
    
    if 'spu_code' not in pick_columns:
        op.add_column('outbound_pick_putaway_item', sa.Column('spu_code', sa.String(64), nullable=False, server_default=''))
        op.execute("UPDATE outbound_pick_putaway_item SET spu_code = '' WHERE spu_code IS NULL")
    
    if 'spu_name' not in pick_columns:
        op.add_column('outbound_pick_putaway_item', sa.Column('spu_name', sa.String(128), nullable=False, server_default=''))
        op.execute("UPDATE outbound_pick_putaway_item SET spu_name = '' WHERE spu_name IS NULL")
    
    if 'sku_code' not in pick_columns:
        op.add_column('outbound_pick_putaway_item', sa.Column('sku_code', sa.String(64), nullable=False, server_default=''))
        op.execute("UPDATE outbound_pick_putaway_item SET sku_code = '' WHERE sku_code IS NULL")
    
    if 'sku_name' not in pick_columns:
        op.add_column('outbound_pick_putaway_item', sa.Column('sku_name', sa.String(128), nullable=False, server_default=''))
        op.execute("UPDATE outbound_pick_putaway_item SET sku_name = '' WHERE sku_name IS NULL")
    
    # Update outbound_receipt_item table
    receipt_columns = [col['name'] for col in inspector.get_columns('outbound_receipt_item')]
    
    if 'spu_code' not in receipt_columns:
        op.add_column('outbound_receipt_item', sa.Column('spu_code', sa.String(64), nullable=False, server_default=''))
        op.execute("UPDATE outbound_receipt_item SET spu_code = '' WHERE spu_code IS NULL")
    
    if 'spu_name' not in receipt_columns:
        op.add_column('outbound_receipt_item', sa.Column('spu_name', sa.String(128), nullable=False, server_default=''))
        op.execute("UPDATE outbound_receipt_item SET spu_name = '' WHERE spu_name IS NULL")
    
    if 'sku_code' not in receipt_columns:
        op.add_column('outbound_receipt_item', sa.Column('sku_code', sa.String(64), nullable=False, server_default=''))
        op.execute("UPDATE outbound_receipt_item SET sku_code = '' WHERE sku_code IS NULL")
    
    if 'sku_name' not in receipt_columns:
        op.add_column('outbound_receipt_item', sa.Column('sku_name', sa.String(128), nullable=False, server_default=''))
        op.execute("UPDATE outbound_receipt_item SET sku_name = '' WHERE sku_name IS NULL")


def downgrade() -> None:
    op.drop_column('outbound_receipt_item', 'sku_name')
    op.drop_column('outbound_receipt_item', 'sku_code')
    op.drop_column('outbound_receipt_item', 'spu_name')
    op.drop_column('outbound_receipt_item', 'spu_code')
    
    op.drop_column('outbound_pick_putaway_item', 'sku_name')
    op.drop_column('outbound_pick_putaway_item', 'sku_code')
    op.drop_column('outbound_pick_putaway_item', 'spu_name')
    op.drop_column('outbound_pick_putaway_item', 'spu_code')
    
    op.drop_column('outbound_order_item', 'sku_name')
    op.drop_column('outbound_order_item', 'sku_code')
    op.drop_column('outbound_order_item', 'spu_name')
    op.drop_column('outbound_order_item', 'spu_code')
