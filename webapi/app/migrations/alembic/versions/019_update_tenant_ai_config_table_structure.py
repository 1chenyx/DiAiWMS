"""update tenant ai config table structure

Revision ID: 019
Revises: 018
Create Date: 2026-03-14 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 修改temperature字段类型为String
    op.alter_column('tenant_ai_config', 'temperature',
                    existing_type=sa.Integer(),
                    type_=sa.String(length=10),
                    existing_nullable=True)
    
    # 修改api_endpoint字段为not nullable
    op.alter_column('tenant_ai_config', 'api_endpoint',
                    existing_type=sa.String(length=512),
                    nullable=False)
    
    # 修改api_key字段长度
    op.alter_column('tenant_ai_config', 'api_key',
                    existing_type=sa.String(length=512),
                    type_=sa.String(length=500))
    
    # 修改provider_code字段长度
    op.alter_column('tenant_ai_config', 'provider_code',
                    existing_type=sa.String(length=32),
                    type_=sa.String(length=50))
    
    # 修改model_code字段长度
    op.alter_column('tenant_ai_config', 'model_code',
                    existing_type=sa.String(length=64),
                    type_=sa.String(length=100))
    
    # 修改creator字段长度
    op.alter_column('tenant_ai_config', 'creator',
                    existing_type=sa.String(length=64),
                    type_=sa.String(length=50))
    
    # 删除不需要的字段
    op.drop_column('tenant_ai_config', 'top_p')
    op.drop_column('tenant_ai_config', 'config')


def downgrade() -> None:
    # 恢复删除的字段
    op.add_column('tenant_ai_config', sa.Column('top_p', sa.Integer(), nullable=True, comment='top_p参数，乘以100存储'))
    op.add_column('tenant_ai_config', sa.Column('config', sa.JSON(), nullable=True, comment='其他配置参数，JSON格式'))
    
    # 恢复字段长度
    op.alter_column('tenant_ai_config', 'creator',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=64))
    
    op.alter_column('tenant_ai_config', 'model_code',
                    existing_type=sa.String(length=100),
                    type_=sa.String(length=64))
    
    op.alter_column('tenant_ai_config', 'provider_code',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=32))
    
    op.alter_column('tenant_ai_config', 'api_key',
                    existing_type=sa.String(length=500),
                    type_=sa.String(length=512))
    
    op.alter_column('tenant_ai_config', 'api_endpoint',
                    existing_type=sa.String(length=512),
                    nullable=True)
    
    # 恢复temperature字段类型为Integer
    op.alter_column('tenant_ai_config', 'temperature',
                    existing_type=sa.String(length=10),
                    type_=sa.Integer(),
                    existing_nullable=True)
