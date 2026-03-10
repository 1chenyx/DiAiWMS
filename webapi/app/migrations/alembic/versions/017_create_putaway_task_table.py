"""create inbound_putaway_task table

Revision ID: 017
Revises: 016
Create Date: 2026-03-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'inbound_putaway_task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pick_putaway_item_id', sa.Integer(), nullable=False, comment='拣货上架单明细ID'),
        sa.Column('putaway_qty', sa.Integer(), nullable=False, default=0, comment='本次上架数量'),
        sa.Column('weight', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='重量'),
        sa.Column('volume', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='体积'),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格'),
        sa.Column('expiry_date', sa.BigInteger(), nullable=False, default=0, comment='过期日期'),
        sa.Column('goods_location_id', sa.Integer(), nullable=False, default=0, comment='上架库位ID'),
        sa.Column('warehouse_id', sa.Integer(), nullable=False, default=0, comment='仓库ID'),
        sa.Column('warehouse_name', sa.String(100), nullable=False, default='', comment='仓库名称'),
        sa.Column('warehouse_area_id', sa.Integer(), nullable=False, default=0, comment='库区ID'),
        sa.Column('warehouse_area_name', sa.String(100), nullable=False, default='', comment='库区名称'),
        sa.Column('warehouse_location_name', sa.String(100), nullable=False, default='', comment='库位名称'),
        sa.Column('putaway_person_id', sa.Integer(), nullable=False, default=0, comment='上架人ID'),
        sa.Column('putaway_person', sa.String(64), nullable=False, default='', comment='上架人'),
        sa.Column('putaway_time', sa.BigInteger(), nullable=False, default=0, comment='上架时间'),
        sa.Column('series_number', sa.String(100), nullable=False, default='', comment='序列号'),
        sa.Column('tenant_id', sa.String(36), nullable=False, default='', comment='租户ID'),
        sa.Column('creator', sa.String(64), nullable=False, default='', comment='创建人'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, default=0, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.ForeignKeyConstraint(['pick_putaway_item_id'], ['inbound_pick_putaway_item.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.execute("CREATE SEQUENCE IF NOT EXISTS inbound_putaway_task_id_seq")
    op.execute("ALTER TABLE inbound_putaway_task ALTER COLUMN id SET DEFAULT nextval('inbound_putaway_task_id_seq')")


def downgrade() -> None:
    op.drop_table('inbound_putaway_task')
    op.execute("DROP SEQUENCE IF EXISTS inbound_putaway_task_id_seq")
