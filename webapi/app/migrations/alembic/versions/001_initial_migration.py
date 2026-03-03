"""initial migration

Revision ID: 001
Revises: 
Create Date: 2026-02-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('user_num', sa.String(length=128), nullable=False, default='', comment='用户编号'),
        sa.Column('user_name', sa.String(length=128), nullable=False, default='', comment='用户名'),
        sa.Column('contact_tel', sa.String(length=64), nullable=False, default='', comment='联系电话'),
        sa.Column('user_role', sa.String(length=128), nullable=False, default='', comment='用户角色'),
        sa.Column('sex', sa.String(length=10), nullable=False, default='', comment='性别'),
        sa.Column('is_valid', sa.Boolean(), nullable=False, default=False, comment='是否有效'),
        sa.Column('auth_string', sa.String(length=64), nullable=False, default='', comment='密码'),
        sa.Column('creator', sa.String(length=64), nullable=False, default='', comment='创建人'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, default=0, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False, default=0, comment='租户ID'),
        sa.PrimaryKeyConstraint('id'),
        comment='用户表'
    )
    
    op.create_table(
        'user_role',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('role_name', sa.String(length=128), nullable=False, default='', comment='角色名称'),
        sa.Column('role_description', sa.String(length=500), nullable=False, default='', comment='角色描述'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, default=0, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.Column('is_valid', sa.Boolean(), nullable=False, default=False, comment='是否有效'),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False, default=0, comment='租户ID'),
        sa.PrimaryKeyConstraint('id'),
        comment='用户角色表'
    )
    
    op.create_table(
        'warehouse',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('warehouse_name', sa.String(length=32), nullable=False, default='', comment='仓库名称'),
        sa.Column('city', sa.String(length=128), nullable=False, default='', comment='城市'),
        sa.Column('address', sa.String(length=256), nullable=False, default='', comment='地址'),
        sa.Column('email', sa.String(length=128), nullable=False, default='', comment='邮箱'),
        sa.Column('manager', sa.String(length=64), nullable=False, default='', comment='管理员'),
        sa.Column('contact_tel', sa.String(length=64), nullable=False, default='', comment='联系电话'),
        sa.Column('creator', sa.String(length=64), nullable=False, default='', comment='创建人'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, default=0, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.Column('is_valid', sa.Boolean(), nullable=False, default=True, comment='是否有效'),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False, default=0, comment='租户ID'),
        sa.PrimaryKeyConstraint('id'),
        comment='仓库表'
    )
    
    op.create_table(
        'warehouse_area',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('warehouse_id', sa.BigInteger(), nullable=False, default=0, comment='仓库ID'),
        sa.Column('area_name', sa.String(length=100), nullable=False, default='', comment='区域名称'),
        sa.Column('parent_id', sa.BigInteger(), nullable=False, default=0, comment='父区域ID'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, default=0, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.Column('is_valid', sa.Boolean(), nullable=False, default=False, comment='是否有效'),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False, default=0, comment='租户ID'),
        sa.Column('area_property', sa.BigInteger(), nullable=False, default=0, comment='区域属性'),
        sa.PrimaryKeyConstraint('id'),
        comment='仓库区域表'
    )
    
    op.create_table(
        'category',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('category_name', sa.String(length=100), nullable=False, default='', comment='分类名称'),
        sa.Column('parent_id', sa.BigInteger(), nullable=False, default=0, comment='父分类ID'),
        sa.Column('creator', sa.String(length=50), nullable=False, default='', comment='创建人'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, default=0, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.Column('is_valid', sa.Boolean(), nullable=False, default=True, comment='是否有效'),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False, default=1, comment='租户ID'),
        sa.PrimaryKeyConstraint('id'),
        comment='商品分类表'
    )
    
    op.create_table(
        'spu',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('spu_code', sa.String(length=50), nullable=False, default='', comment='SPU编码'),
        sa.Column('spu_name', sa.String(length=100), nullable=False, default='', comment='SPU名称'),
        sa.Column('category_id', sa.BigInteger(), nullable=False, default=0, comment='分类ID'),
        sa.Column('spu_description', sa.String(length=500), nullable=False, default='', comment='SPU描述'),
        sa.Column('supplier_id', sa.BigInteger(), nullable=False, default=0, comment='供应商ID'),
        sa.Column('supplier_name', sa.String(length=100), nullable=False, default='', comment='供应商名称'),
        sa.Column('brand', sa.String(length=100), nullable=False, default='', comment='品牌'),
        sa.Column('origin', sa.String(length=100), nullable=False, default='', comment='产地'),
        sa.Column('length_unit', sa.SmallInteger(), nullable=False, default=0, comment='长度单位'),
        sa.Column('volume_unit', sa.SmallInteger(), nullable=False, default=0, comment='体积单位'),
        sa.Column('weight_unit', sa.SmallInteger(), nullable=False, default=0, comment='重量单位'),
        sa.Column('creator', sa.String(length=50), nullable=False, default='', comment='创建人'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, default=0, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.Column('is_valid', sa.Boolean(), nullable=False, default=True, comment='是否有效'),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False, default=1, comment='租户ID'),
        sa.PrimaryKeyConstraint('id'),
        comment='标准产品单元表'
    )
    
    op.create_table(
        'sku',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('spu_id', sa.BigInteger(), nullable=False, default=0, comment='SPU ID'),
        sa.Column('sku_code', sa.String(length=50), nullable=False, default='', comment='SKU编码'),
        sa.Column('sku_name', sa.String(length=100), nullable=False, default='', comment='SKU名称'),
        sa.Column('bar_code', sa.String(length=50), nullable=False, default='', comment='条码'),
        sa.Column('weight', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='重量'),
        sa.Column('lenght', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='长度'),
        sa.Column('width', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='宽度'),
        sa.Column('height', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='高度'),
        sa.Column('volume', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='体积'),
        sa.Column('unit', sa.String(length=20), nullable=False, default='', comment='单位'),
        sa.Column('cost', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='成本'),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, default=0, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='库存量单位表'
    )
    
    op.create_table(
        'goodslocation',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('warehouse_id', sa.BigInteger(), nullable=False, default=0, comment='仓库ID'),
        sa.Column('warehouse_name', sa.String(length=100), nullable=False, default='', comment='仓库名称'),
        sa.Column('warehouse_area_name', sa.String(length=100), nullable=False, default='', comment='库区名称'),
        sa.Column('warehouse_area_property', sa.BigInteger(), nullable=False, default=0, comment='库区属性'),
        sa.Column('location_name', sa.String(length=100), nullable=False, default='', comment='货位名称'),
        sa.Column('location_length', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='货位长度'),
        sa.Column('location_width', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='货位宽度'),
        sa.Column('location_heigth', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='货位高度'),
        sa.Column('location_volume', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='货位体积'),
        sa.Column('location_load', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='货位载重'),
        sa.Column('roadway_number', sa.String(length=50), nullable=False, default='', comment='巷道号'),
        sa.Column('shelf_number', sa.String(length=50), nullable=False, default='', comment='货架号'),
        sa.Column('layer_number', sa.String(length=50), nullable=False, default='', comment='层号'),
        sa.Column('tag_number', sa.String(length=50), nullable=False, default='', comment='标签号'),
        sa.Column('create_time', sa.BigInteger(), nullable=False, default=0, comment='创建时间'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.Column('is_valid', sa.Boolean(), nullable=False, default=False, comment='是否有效'),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False, default=0, comment='租户ID'),
        sa.Column('warehouse_area_id', sa.BigInteger(), nullable=False, default=0, comment='库区ID'),
        sa.PrimaryKeyConstraint('id'),
        comment='货位表'
    )
    
    op.create_table(
        'stock',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('sku_id', sa.BigInteger(), nullable=False, default=0, comment='SKU ID'),
        sa.Column('goods_location_id', sa.BigInteger(), nullable=False, default=0, comment='货位ID'),
        sa.Column('qty', sa.BigInteger(), nullable=False, default=0, comment='数量'),
        sa.Column('goods_owner_id', sa.BigInteger(), nullable=False, default=0, comment='货主ID'),
        sa.Column('is_freeze', sa.Boolean(), nullable=False, default=False, comment='是否冻结'),
        sa.Column('last_update_time', sa.BigInteger(), nullable=False, default=0, comment='最后更新时间'),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False, default=0, comment='租户ID'),
        sa.Column('series_number', sa.String(length=100), nullable=False, default='', comment='序列号'),
        sa.Column('expiry_date', sa.BigInteger(), nullable=False, default=0, comment='过期日期'),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格'),
        sa.Column('putaway_date', sa.BigInteger(), nullable=False, default=0, comment='上架日期'),
        sa.PrimaryKeyConstraint('id'),
        comment='库存表'
    )


def downgrade() -> None:
    op.drop_table('stock')
    op.drop_table('goodslocation')
    op.drop_table('sku')
    op.drop_table('spu')
    op.drop_table('category')
    op.drop_table('warehouse_area')
    op.drop_table('warehouse')
    op.drop_table('user_role')
    op.drop_table('user')
