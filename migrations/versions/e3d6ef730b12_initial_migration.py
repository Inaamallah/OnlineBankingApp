"""Initial migration

Revision ID: e3d6ef730b12
Revises: 
Create Date: 2025-05-24 04:25:05.067989

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3d6ef730b12'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender_account', sa.String(length=12), nullable=False),
    sa.Column('receiver_account', sa.String(length=12), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('type', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=False),
    sa.Column('cnic', sa.String(length=15), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('password', sa.String(length=60), nullable=False),
    sa.Column('balance', sa.Float(), nullable=True),
    sa.Column('account_number', sa.String(length=12), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('account_number'),
    sa.UniqueConstraint('cnic'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('transaction')
    # ### end Alembic commands ###
