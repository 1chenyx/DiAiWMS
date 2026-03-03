"""add_tenant_table

Revision ID: 002
Revises: 001
Create Date: 2026-02-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tenant',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('tenant_name', sa.String(length=100), nullable=False, default='', comment='租户名称'),
        sa.Column('tenant_code', sa.String(length=50), nullable=False, default='', comment='租户编码'),
        sa.Column('contact_person', sa.String(length=50), nullable=False, default='', comment='联系人'),
        sa.Column('contact_phone', sa.String(length=20), nullable=False, default='', comment='联系电话'),
        sa.Column('contact_email', sa.String(length=100), nullable=False, default='', comment='联系邮箱'),
        sa.Column('address', sa.String(length=256), nullable=False, default='', comment='地址'),
        sa.Column('description', sa.String(length=500), nullable=False, default='', comment='描述'),
        sa.Column('is_valid', sa.Boolean(), nullable=False, default=True, comment='是否有效'),
        sa.Column('creator', sa.String(length=50), nullable=False, default='', comment='创建人'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, default=0, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='租户表'
    )


def downgrade() -> None:
    op.drop_table('tenant')
