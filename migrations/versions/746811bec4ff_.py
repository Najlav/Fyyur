"""empty message

Revision ID: 746811bec4ff
Revises: 8a7a523a0bba
Create Date: 2021-06-13 01:43:37.305034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '746811bec4ff'
down_revision = '8a7a523a0bba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    # ### end Alembic commands ###
