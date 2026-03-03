"""change_tenant_id_to_uuid

Revision ID: 005
Revises: 004
Create Date: 2026-02-28 19:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'tenant',
        sa.Column('id_new', sa.String(length=36), nullable=False, server_default='', comment='主键ID(UUID)')
    )
    
    op.execute("""
        UPDATE tenant SET id_new = '00000000-0000-0000-0000-000000000001'::text
        WHERE id = 1
    """)
    
    op.drop_constraint('tenant_pkey', 'tenant', type_='primary')
    op.drop_column('tenant', 'id')
    
    op.alter_column(
        'tenant',
        'id_new',
        new_column_name='id',
        existing_type=sa.String(length=36),
        nullable=False
    )
    
    op.create_primary_key('tenant_pkey', 'tenant', ['id'])


def downgrade() -> None:
    op.add_column(
        'tenant',
        sa.Column('id_new', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID')
    )
    
    op.execute("""
        UPDATE tenant SET id_new = 1
        WHERE id = '00000000-0000-0000-0000-000000000001'
    """)
    
    op.drop_constraint('tenant_pkey', 'tenant', type_='primary')
    op.drop_column('tenant', 'id')
    
    op.alter_column(
        'tenant',
        'id_new',
        new_column_name='id',
        existing_type=sa.Integer(),
        nullable=False,
        autoincrement=True
    )
    
    op.create_primary_key('tenant_pkey', 'tenant', ['id'])
