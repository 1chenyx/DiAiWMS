"""drop company table

Revision ID: 008
Revises: 007
Create Date: 2026-03-01 22:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('company')


def downgrade() -> None:
    op.create_table(
        'company',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('company_name', sa.String(length=128), nullable=False, default='', comment='公司名称'),
        sa.Column('city', sa.String(length=64), nullable=False, default='', comment='城市'),
        sa.Column('address', sa.String(length=255), nullable=False, default='', comment='地址'),
        sa.Column('manager', sa.String(length=64), nullable=False, default='', comment='负责人'),
        sa.Column('contact_tel', sa.String(length=32), nullable=False, default='', comment='联系电话'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, comment='最后更新时间'),
        sa.Column('tenant_id', sa.String(length=36), nullable=False, default='', comment='租户ID'),
        sa.PrimaryKeyConstraint('id'),
        comment='公司表'
    )
