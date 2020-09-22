"""relate blockchain contracts to parties as owners

Revision ID: 6f107c3dbb23
Revises: 
Create Date: 2020-09-22 12:43:31.028326

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6f107c3dbb23'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'blockchain_contracts',
        sa.Column(
            'owner_id', sa.Integer,
            sa.ForeignKey('parties.id', ondelete='RESTRICT'),
            nullable=False
        )
    )


def downgrade():
    op.drop_column('blockchain_contracts', 'owner_id')
