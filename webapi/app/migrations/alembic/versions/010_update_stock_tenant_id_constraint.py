"""update stock tenant_id constraint

Revision ID: 010
Revises: 009
Create Date: 2026-03-09 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE stock SET tenant_id = '' WHERE tenant_id IS NULL")


def downgrade() -> None:
    pass
