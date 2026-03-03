"""create tenant ai config table

Revision ID: 007
Revises: 005
Create Date: 2026-03-01 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tenant_ai_config',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('provider_code', sa.String(length=32), nullable=False, comment='提供商代码'),
        sa.Column('model_code', sa.String(length=64), nullable=False, comment='模型代码'),
        sa.Column('api_key', sa.String(length=512), nullable=False, comment='API密钥'),
        sa.Column('api_endpoint', sa.String(length=512), nullable=True, comment='API端点URL'),
        sa.Column('is_default', sa.Boolean(), default=False, nullable=False, comment='是否为默认配置'),
        sa.Column('temperature', sa.Integer(), nullable=True, comment='温度参数，乘以100存储'),
        sa.Column('top_p', sa.Integer(), nullable=True, comment='top_p参数，乘以100存储'),
        sa.Column('max_tokens', sa.Integer(), nullable=True, comment='最大token数'),
        sa.Column('config', sa.JSON(), nullable=True, comment='其他配置参数，JSON格式'),
        sa.Column('tenant_id', sa.String(length=36), nullable=False, comment='租户ID'),
        sa.Column('creator', sa.String(length=64), nullable=True, comment='创建人'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, comment='最后更新时间'),
        sa.Column('is_valid', sa.Boolean(), default=True, nullable=False, comment='是否有效'),
        sa.PrimaryKeyConstraint('id'),
        comment='租户AI配置表'
    )
    op.create_index('ix_tenant_ai_config_tenant_id', 'tenant_ai_config', ['tenant_id'])
    op.create_index('ix_tenant_ai_config_provider_code', 'tenant_ai_config', ['provider_code'])
    op.create_index('ix_tenant_ai_config_is_default', 'tenant_ai_config', ['is_default'])


def downgrade() -> None:
    op.drop_index('ix_tenant_ai_config_is_default', table_name='tenant_ai_config')
    op.drop_index('ix_tenant_ai_config_provider_code', table_name='tenant_ai_config')
    op.drop_index('ix_tenant_ai_config_tenant_id', table_name='tenant_ai_config')
    op.drop_table('tenant_ai_config')
