"""empty message

Revision ID: f7de6275c687
Revises: 
Create Date: 2020-09-08 15:56:20.560100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7de6275c687'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'enterprizes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('subdomain', sa.String(), nullable=False),
        sa.Column(
            'created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('subdomain'),
    )
    op.create_index(op.f('ix_enterprizes_reference'), 'enterprizes', ['reference'], unique=True)
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=36), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column(
            'created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=True,
        ),
        sa.Column('enterprize_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['enterprize_id'],
            ['enterprizes.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('password'),
        sa.UniqueConstraint('username'),
    )
    op.create_index(op.f('ix_users_enterprize_id'), 'users', ['enterprize_id'], unique=False)
    op.create_index(op.f('ix_users_reference'), 'users', ['reference'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_reference'), table_name='users')
    op.drop_index(op.f('ix_users_enterprize_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_enterprizes_reference'), table_name='enterprizes')
    op.drop_table('enterprizes')
    # ### end Alembic commands ###
