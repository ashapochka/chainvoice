"""empty message

Revision ID: 129092d2868b
Revises: 55320a5f5f8d
Create Date: 2020-10-22 13:02:04.692766

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '129092d2868b'
down_revision = '55320a5f5f8d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payments',
                  sa.Column('blockchain_tx_hash', sa.String(), nullable=True))
    op.create_index(op.f('ix_payments_blockchain_tx_hash'), 'payments',
                    ['blockchain_tx_hash'], unique=False)
    op.drop_index('ix_payments_blockchain_tx_address', table_name='payments')
    op.drop_column('payments', 'blockchain_tx_address')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payments', sa.Column('blockchain_tx_address', sa.VARCHAR(),
                                        autoincrement=False, nullable=True))
    op.create_index('ix_payments_blockchain_tx_address', 'payments',
                    ['blockchain_tx_address'], unique=False)
    op.drop_index(op.f('ix_payments_blockchain_tx_hash'), table_name='payments')
    op.drop_column('payments', 'blockchain_tx_hash')
    # ### end Alembic commands ###
