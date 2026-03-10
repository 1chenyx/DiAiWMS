"""add tenant_id to sku table

Revision ID: 011
Revises: 010
Create Date: 2026-03-09 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('sku')]
    
    if 'tenant_id' not in columns:
        op.add_column('sku', sa.Column('tenant_id', sa.String(50), nullable=False, server_default=''))
        op.execute("UPDATE sku SET tenant_id = '' WHERE tenant_id IS NULL")


def downgrade() -> None:
    op.drop_column('sku', 'tenant_id')