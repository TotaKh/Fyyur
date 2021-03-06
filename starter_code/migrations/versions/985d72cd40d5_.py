"""empty message

Revision ID: 985d72cd40d5
Revises: bc8fb4e172c0
Create Date: 2020-12-18 00:39:22.833810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '985d72cd40d5'
down_revision = 'bc8fb4e172c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'website')
    # ### end Alembic commands ###
