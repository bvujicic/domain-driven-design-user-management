"""empty message

Revision ID: dbb1f6ce678b
Revises: 63c4d8a148fd
Create Date: 2020-10-23 15:01:26.099597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbb1f6ce678b'
down_revision = '63c4d8a148fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('photo_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'photo_url')
    # ### end Alembic commands ###
