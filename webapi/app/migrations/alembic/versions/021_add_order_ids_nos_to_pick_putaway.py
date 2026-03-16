"""add order_ids and order_nos to outbound_pick_putaway

Revision ID: 021
Revises: 020
Create Date: 2026-03-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '021'
down_revision = '020'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    columns = [col['name'] for col in inspector.get_columns('outbound_pick_putaway')]
    
    if 'order_ids' not in columns:
        op.add_column('outbound_pick_putaway', sa.Column('order_ids', sa.String(512), nullable=False, server_default=''))
        op.execute("UPDATE outbound_pick_putaway SET order_ids = CAST(order_id AS VARCHAR) WHERE order_ids = '' OR order_ids IS NULL")
    
    if 'order_nos' not in columns:
        op.add_column('outbound_pick_putaway', sa.Column('order_nos', sa.String(512), nullable=False, server_default=''))
        op.execute("UPDATE outbound_pick_putaway SET order_nos = order_no WHERE order_nos = '' OR order_nos IS NULL")


def downgrade() -> None:
    op.drop_column('outbound_pick_putaway', 'order_nos')
    op.drop_column('outbound_pick_putaway', 'order_ids')
