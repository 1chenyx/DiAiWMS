"""add_database_config_to_tenant_table

Revision ID: 004
Revises: 003
Create Date: 2026-02-28 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'tenant',
        sa.Column('db_drivername', sa.String(length=50), nullable=False, server_default='postgresql+asyncpg', comment='数据库驱动类型')
    )
    op.add_column(
        'tenant',
        sa.Column('db_database', sa.String(length=100), nullable=False, server_default='', comment='数据库名称')
    )
    op.add_column(
        'tenant',
        sa.Column('db_username', sa.String(length=100), nullable=False, server_default='', comment='数据库用户名')
    )
    op.add_column(
        'tenant',
        sa.Column('db_password', sa.String(length=100), nullable=False, server_default='', comment='数据库密码')
    )
    op.add_column(
        'tenant',
        sa.Column('db_host', sa.String(length=100), nullable=False, server_default='localhost', comment='数据库主机')
    )
    op.add_column(
        'tenant',
        sa.Column('db_port', sa.Integer(), nullable=False, server_default='5432', comment='数据库端口')
    )
    op.add_column(
        'tenant',
        sa.Column('db_charset', sa.String(length=20), nullable=False, server_default='utf8', comment='数据库字符集')
    )
    op.add_column(
        'tenant',
        sa.Column('db_pool_size', sa.Integer(), nullable=False, server_default='10', comment='连接池大小')
    )
    op.add_column(
        'tenant',
        sa.Column('db_max_overflow', sa.Integer(), nullable=False, server_default='5', comment='连接池最大溢出数')
    )
    op.add_column(
        'tenant',
        sa.Column('db_pool_recycle', sa.Integer(), nullable=False, server_default='3600', comment='连接回收时间(秒)')
    )
    op.add_column(
        'tenant',
        sa.Column('slave_host', sa.String(length=100), nullable=True, server_default=None, comment='从库主机(可选)')
    )
    op.add_column(
        'tenant',
        sa.Column('slave_port', sa.Integer(), nullable=True, server_default=None, comment='从库端口(可选)')
    )
    
    op.create_unique_constraint('uq_tenant_tenant_code', 'tenant', ['tenant_code'])


def downgrade() -> None:
    op.drop_constraint('uq_tenant_tenant_code', 'tenant', type_='unique')
    
    op.drop_column('tenant', 'slave_port')
    op.drop_column('tenant', 'slave_host')
    op.drop_column('tenant', 'db_pool_recycle')
    op.drop_column('tenant', 'db_max_overflow')
    op.drop_column('tenant', 'db_pool_size')
    op.drop_column('tenant', 'db_charset')
    op.drop_column('tenant', 'db_port')
    op.drop_column('tenant', 'db_host')
    op.drop_column('tenant', 'db_password')
    op.drop_column('tenant', 'db_username')
    op.drop_column('tenant', 'db_database')
    op.drop_column('tenant', 'db_drivername')
