"""Add operation_id column to states table

Revision ID: 77c3995c8465
Revises: 001
Create Date: 2025-03-18 15:39:43.581686

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '77c3995c8465'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('states', sa.Column('operation_id', sa.String(length=255), nullable=True))
    op.alter_column('states', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('states', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('states', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('states', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_column('states', 'operation_id')
    # ### end Alembic commands ### 
