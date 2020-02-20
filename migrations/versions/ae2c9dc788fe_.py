"""empty message

Revision ID: ae2c9dc788fe
Revises: 
Create Date: 2020-02-19 15:20:37.431809

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae2c9dc788fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('works', sa.Column('last_updated', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('works', 'last_updated')
    # ### end Alembic commands ###
