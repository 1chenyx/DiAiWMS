"""add spu and sku name fields to inbound_pick_putaway_item

Revision ID: 014
Revises: 013
Create Date: 2026-03-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('inbound_pick_putaway_item')]
    
    if 'spu_code' not in columns:
        op.add_column('inbound_pick_putaway_item', sa.Column('spu_code', sa.String(64), nullable=False, server_default=''))
        op.execute("UPDATE inbound_pick_putaway_item SET spu_code = '' WHERE spu_code IS NULL")
    
    if 'spu_name' not in columns:
        op.add_column('inbound_pick_putaway_item', sa.Column('spu_name', sa.String(128), nullable=False, server_default=''))
        op.execute("UPDATE inbound_pick_putaway_item SET spu_name = '' WHERE spu_name IS NULL")
    
    if 'sku_code' not in columns:
        op.add_column('inbound_pick_putaway_item', sa.Column('sku_code', sa.String(64), nullable=False, server_default=''))
        op.execute("UPDATE inbound_pick_putaway_item SET sku_code = '' WHERE sku_code IS NULL")
    
    if 'sku_name' not in columns:
        op.add_column('inbound_pick_putaway_item', sa.Column('sku_name', sa.String(128), nullable=False, server_default=''))
        op.execute("UPDATE inbound_pick_putaway_item SET sku_name = '' WHERE sku_name IS NULL")


def downgrade() -> None:
    op.drop_column('inbound_pick_putaway_item', 'sku_name')
    op.drop_column('inbound_pick_putaway_item', 'sku_code')
    op.drop_column('inbound_pick_putaway_item', 'spu_name')
    op.drop_column('inbound_pick_putaway_item', 'spu_code')
