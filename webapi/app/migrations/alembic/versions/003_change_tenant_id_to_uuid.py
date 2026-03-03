"""change tenant_id from integer to uuid string

Revision ID: 003
Revises: 002
Create Date: 2026-02-28 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'user',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'userrole',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'warehouse',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'warehousearea',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'goodslocation',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'category',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='1',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'spu',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='1',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'stock',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'company',
        'tenant_id',
        existing_type=sa.Integer(),
        type_=sa.String(length=36),
        existing_default='1',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'supplier',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'customer',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='1',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'goodsowner',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='1',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'freightfee',
        'tenant_id',
        existing_type=sa.Integer(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'user_defined_print_solution',
        'tenant_id',
        existing_type=sa.Integer(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'stockprocess',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'stockprocessdetail',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'stocktaking',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='1',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'stockmove',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'stockadjust',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'stockfreeze',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='0',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'menu',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='1',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'rolemenu',
        'tenant_id',
        existing_type=sa.BigInteger(),
        type_=sa.String(length=36),
        existing_default='1',
        server_default='',
        nullable=False
    )
    
    op.alter_column(
        'action_log',
        'tenant_id',
        existing_type=sa.Integer(),
        type_=sa.String(length=36),
        existing_default='1',
        server_default='',
        nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        'user',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'userrole',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'warehouse',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'warehousearea',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'goodslocation',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'category',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='1',
        nullable=False
    )
    
    op.alter_column(
        'spu',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='1',
        nullable=False
    )
    
    op.alter_column(
        'stock',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'company',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.Integer(),
        existing_default='',
        server_default='1',
        nullable=False
    )
    
    op.alter_column(
        'supplier',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'customer',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='1',
        nullable=False
    )
    
    op.alter_column(
        'goodsowner',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='1',
        nullable=False
    )
    
    op.alter_column(
        'freightfee',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.Integer(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'user_defined_print_solution',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.Integer(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'stockprocess',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'stockprocessdetail',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'stocktaking',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='1',
        nullable=False
    )
    
    op.alter_column(
        'stockmove',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'stockadjust',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'stockfreeze',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='0',
        nullable=False
    )
    
    op.alter_column(
        'menu',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='1',
        nullable=False
    )
    
    op.alter_column(
        'rolemenu',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.BigInteger(),
        existing_default='',
        server_default='1',
        nullable=False
    )
    
    op.alter_column(
        'action_log',
        'tenant_id',
        existing_type=sa.String(length=36),
        type_=sa.Integer(),
        existing_default='',
        server_default='1',
        nullable=False
    )
