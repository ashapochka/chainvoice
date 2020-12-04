"""empty message

Revision ID: d15f77151156
Revises: c1f738e0734f
Create Date: 2020-11-12 16:40:39.689317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd15f77151156'
down_revision = 'c1f738e0734f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('parties', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE parties SET active = false")
    op.alter_column('parties', 'active', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('parties', 'active')
    # ### end Alembic commands ###