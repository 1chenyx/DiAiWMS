"""add warehouse and location fields to inbound tables

Revision ID: 013
Revises: 012
Create Date: 2026-03-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Update inbound_pick_putaway_item table
    inspector = sa.inspect(conn)
    pick_columns = [col['name'] for col in inspector.get_columns('inbound_pick_putaway_item')]
    
    if 'warehouse_id' not in pick_columns:
        op.add_column('inbound_pick_putaway_item', sa.Column('warehouse_id', sa.Integer(), nullable=False, server_default='0'))
        op.execute("UPDATE inbound_pick_putaway_item SET warehouse_id = 0 WHERE warehouse_id IS NULL")
    
    if 'warehouse_name' not in pick_columns:
        op.add_column('inbound_pick_putaway_item', sa.Column('warehouse_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE inbound_pick_putaway_item SET warehouse_name = '' WHERE warehouse_name IS NULL")
    
    if 'warehouse_area_id' not in pick_columns:
        op.add_column('inbound_pick_putaway_item', sa.Column('warehouse_area_id', sa.Integer(), nullable=False, server_default='0'))
        op.execute("UPDATE inbound_pick_putaway_item SET warehouse_area_id = 0 WHERE warehouse_area_id IS NULL")
    
    if 'warehouse_area_name' not in pick_columns:
        op.add_column('inbound_pick_putaway_item', sa.Column('warehouse_area_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE inbound_pick_putaway_item SET warehouse_area_name = '' WHERE warehouse_area_name IS NULL")
    
    if 'warehouse_location_name' not in pick_columns:
        op.add_column('inbound_pick_putaway_item', sa.Column('warehouse_location_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE inbound_pick_putaway_item SET warehouse_location_name = '' WHERE warehouse_location_name IS NULL")
    
    # Update inbound_receipt_item table
    receipt_columns = [col['name'] for col in inspector.get_columns('inbound_receipt_item')]
    
    if 'warehouse_id' not in receipt_columns:
        op.add_column('inbound_receipt_item', sa.Column('warehouse_id', sa.Integer(), nullable=False, server_default='0'))
        op.execute("UPDATE inbound_receipt_item SET warehouse_id = 0 WHERE warehouse_id IS NULL")
    
    if 'warehouse_name' not in receipt_columns:
        op.add_column('inbound_receipt_item', sa.Column('warehouse_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE inbound_receipt_item SET warehouse_name = '' WHERE warehouse_name IS NULL")
    
    if 'warehouse_area_id' not in receipt_columns:
        op.add_column('inbound_receipt_item', sa.Column('warehouse_area_id', sa.Integer(), nullable=False, server_default='0'))
        op.execute("UPDATE inbound_receipt_item SET warehouse_area_id = 0 WHERE warehouse_area_id IS NULL")
    
    if 'warehouse_area_name' not in receipt_columns:
        op.add_column('inbound_receipt_item', sa.Column('warehouse_area_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE inbound_receipt_item SET warehouse_area_name = '' WHERE warehouse_area_name IS NULL")
    
    if 'warehouse_location_name' not in receipt_columns:
        op.add_column('inbound_receipt_item', sa.Column('warehouse_location_name', sa.String(100), nullable=False, server_default=''))
        op.execute("UPDATE inbound_receipt_item SET warehouse_location_name = '' WHERE warehouse_location_name IS NULL")


def downgrade() -> None:
    op.drop_column('inbound_receipt_item', 'warehouse_location_name')
    op.drop_column('inbound_receipt_item', 'warehouse_area_name')
    op.drop_column('inbound_receipt_item', 'warehouse_area_id')
    op.drop_column('inbound_receipt_item', 'warehouse_name')
    op.drop_column('inbound_receipt_item', 'warehouse_id')
    
    op.drop_column('inbound_pick_putaway_item', 'warehouse_location_name')
    op.drop_column('inbound_pick_putaway_item', 'warehouse_area_name')
    op.drop_column('inbound_pick_putaway_item', 'warehouse_area_id')
    op.drop_column('inbound_pick_putaway_item', 'warehouse_name')
    op.drop_column('inbound_pick_putaway_item', 'warehouse_id')