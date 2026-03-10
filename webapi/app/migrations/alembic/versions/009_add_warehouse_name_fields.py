"""add warehouse_name and goods_location_code fields

Revision ID: 009
Revises: 008
Create Date: 2026-03-09 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('inbound_order', sa.Column('warehouse_name', sa.String(length=128), nullable=False, server_default='', comment='仓库名称'))
    op.add_column('outbound_order', sa.Column('warehouse_name', sa.String(length=128), nullable=False, server_default='', comment='仓库名称'))
    op.add_column('outbound_order_item', sa.Column('goods_location_code', sa.String(length=64), nullable=False, server_default='', comment='库位编码'))


def downgrade() -> None:
    op.drop_column('outbound_order_item', 'goods_location_code')
    op.drop_column('outbound_order', 'warehouse_name')
    op.drop_column('inbound_order', 'warehouse_name')
