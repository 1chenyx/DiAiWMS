"""change temperature to float

Revision ID: 020
Revises: 
Create Date: 2026-03-14

"""
from alembic import op
import sqlalchemy as sa


revision = '020'
down_revision = '019'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE tenant_ai_config 
        ALTER COLUMN temperature TYPE FLOAT USING temperature::FLOAT,
        ALTER COLUMN max_tokens DROP NOT NULL,
        ALTER COLUMN api_endpoint DROP NOT NULL
    """)


def downgrade():
    op.execute("""
        ALTER TABLE tenant_ai_config 
        ALTER COLUMN temperature TYPE INTEGER USING temperature::INTEGER,
        ALTER COLUMN max_tokens SET NOT NULL,
        ALTER COLUMN api_endpoint SET NOT NULL
    """)
