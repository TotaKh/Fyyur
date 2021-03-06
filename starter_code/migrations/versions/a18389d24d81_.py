"""empty message

Revision ID: a18389d24d81
Revises: 985d72cd40d5
Create Date: 2020-12-18 01:33:16.713755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a18389d24d81'
down_revision = '985d72cd40d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('artist_id', sa.Integer(), nullable=False))
    op.add_column('show', sa.Column('venue_id', sa.Integer(), nullable=False))
    op.drop_constraint('show_Venue_id_fkey', 'show', type_='foreignkey')
    op.drop_constraint('show_Artist_id_fkey', 'show', type_='foreignkey')
    op.create_foreign_key(None, 'show', 'venue', ['venue_id'], ['id'])
    op.create_foreign_key(None, 'show', 'artist', ['artist_id'], ['id'])
    op.drop_column('show', 'Artist_id')
    op.drop_column('show', 'Venue_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('Venue_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('show', sa.Column('Artist_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'show', type_='foreignkey')
    op.drop_constraint(None, 'show', type_='foreignkey')
    op.create_foreign_key('show_Artist_id_fkey', 'show', 'artist', ['Artist_id'], ['id'])
    op.create_foreign_key('show_Venue_id_fkey', 'show', 'venue', ['Venue_id'], ['id'])
    op.drop_column('show', 'venue_id')
    op.drop_column('show', 'artist_id')
    # ### end Alembic commands ###
