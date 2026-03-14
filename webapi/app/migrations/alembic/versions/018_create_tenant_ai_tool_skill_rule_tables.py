"""create tenant ai tool skill rule tables

Revision ID: 018
Revises: 017
Create Date: 2026-03-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建租户AI工具配置表
    op.create_table(
        'tenant_ai_tool',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('tenant_id', sa.String(length=36), nullable=False, comment='租户ID'),
        sa.Column('tool_code', sa.String(length=64), nullable=False, comment='工具代码'),
        sa.Column('tool_name', sa.String(length=128), nullable=False, comment='工具名称'),
        sa.Column('tool_category', sa.String(length=32), nullable=False, comment='工具分类'),
        sa.Column('config', sa.JSON(), nullable=True, comment='工具配置'),
        sa.Column('description', sa.String(length=512), nullable=True, comment='工具描述'),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False, comment='是否激活'),
        sa.Column('creator', sa.String(length=64), nullable=True, comment='创建人'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, comment='最后更新时间'),
        sa.Column('is_valid', sa.Boolean(), default=True, nullable=False, comment='是否有效'),
        sa.PrimaryKeyConstraint('id'),
        comment='租户AI工具配置表'
    )
    op.create_index('ix_tenant_ai_tool_tenant_id', 'tenant_ai_tool', ['tenant_id'])
    op.create_index('ix_tenant_ai_tool_tool_code', 'tenant_ai_tool', ['tool_code'])
    op.create_index('ix_tenant_ai_tool_is_active', 'tenant_ai_tool', ['is_active'])
    
    # 创建租户AI技能配置表
    op.create_table(
        'tenant_ai_skill',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('tenant_id', sa.String(length=36), nullable=False, comment='租户ID'),
        sa.Column('skill_name', sa.String(length=128), nullable=False, comment='技能名称'),
        sa.Column('skill_type', sa.String(length=32), nullable=False, comment='技能类型'),
        sa.Column('description', sa.String(length=512), nullable=True, comment='技能描述'),
        sa.Column('config', sa.JSON(), nullable=True, comment='技能配置'),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False, comment='是否激活'),
        sa.Column('creator', sa.String(length=64), nullable=True, comment='创建人'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, comment='最后更新时间'),
        sa.Column('is_valid', sa.Boolean(), default=True, nullable=False, comment='是否有效'),
        sa.PrimaryKeyConstraint('id'),
        comment='租户AI技能配置表'
    )
    op.create_index('ix_tenant_ai_skill_tenant_id', 'tenant_ai_skill', ['tenant_id'])
    op.create_index('ix_tenant_ai_skill_skill_type', 'tenant_ai_skill', ['skill_type'])
    op.create_index('ix_tenant_ai_skill_is_active', 'tenant_ai_skill', ['is_active'])
    
    # 创建租户AI规则配置表
    op.create_table(
        'tenant_ai_rule',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('tenant_id', sa.String(length=36), nullable=False, comment='租户ID'),
        sa.Column('rule_name', sa.String(length=128), nullable=False, comment='规则名称'),
        sa.Column('rule_category', sa.String(length=32), nullable=False, comment='规则类别'),
        sa.Column('priority', sa.Integer(), default=0, nullable=False, comment='优先级'),
        sa.Column('content', sa.Text(), nullable=False, comment='规则内容'),
        sa.Column('description', sa.String(length=512), nullable=True, comment='规则描述'),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False, comment='是否激活'),
        sa.Column('is_system', sa.Boolean(), default=False, nullable=False, comment='是否系统规则'),
        sa.Column('creator', sa.String(length=64), nullable=True, comment='创建人'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, comment='最后更新时间'),
        sa.Column('is_valid', sa.Boolean(), default=True, nullable=False, comment='是否有效'),
        sa.PrimaryKeyConstraint('id'),
        comment='租户AI规则配置表'
    )
    op.create_index('ix_tenant_ai_rule_tenant_id', 'tenant_ai_rule', ['tenant_id'])
    op.create_index('ix_tenant_ai_rule_rule_category', 'tenant_ai_rule', ['rule_category'])
    op.create_index('ix_tenant_ai_rule_priority', 'tenant_ai_rule', ['priority'])
    op.create_index('ix_tenant_ai_rule_is_active', 'tenant_ai_rule', ['is_active'])


def downgrade() -> None:
    # 删除租户AI规则配置表
    op.drop_index('ix_tenant_ai_rule_is_active', table_name='tenant_ai_rule')
    op.drop_index('ix_tenant_ai_rule_priority', table_name='tenant_ai_rule')
    op.drop_index('ix_tenant_ai_rule_rule_category', table_name='tenant_ai_rule')
    op.drop_index('ix_tenant_ai_rule_tenant_id', table_name='tenant_ai_rule')
    op.drop_table('tenant_ai_rule')
    
    # 删除租户AI技能配置表
    op.drop_index('ix_tenant_ai_skill_is_active', table_name='tenant_ai_skill')
    op.drop_index('ix_tenant_ai_skill_skill_type', table_name='tenant_ai_skill')
    op.drop_index('ix_tenant_ai_skill_tenant_id', table_name='tenant_ai_skill')
    op.drop_table('tenant_ai_skill')
    
    # 删除租户AI工具配置表
    op.drop_index('ix_tenant_ai_tool_is_active', table_name='tenant_ai_tool')
    op.drop_index('ix_tenant_ai_tool_tool_code', table_name='tenant_ai_tool')
    op.drop_index('ix_tenant_ai_tool_tenant_id', table_name='tenant_ai_tool')
    op.drop_table('tenant_ai_tool')
