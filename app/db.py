from databases import Database
from sqlalchemy import (
    MetaData,
    Table, Column, ForeignKey,
    Integer, String, Boolean, Numeric, Date,
    create_engine
)
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.dialects.postgresql import (
    UUID, ENUM
)
from .config import get_settings

database = Database(get_settings().database_url)
metadata = MetaData()

notes = Table(
    "notes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("text", String),
    Column("completed", Boolean),
)

parties = Table(
    'parties',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column('name', String, index=True, unique=True, nullable=False),
    Column('blockchain_account_address', String, index=True, nullable=True),
)

catalogs = Table(
    'catalogs',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column('seller_id', None,
           ForeignKey('parties.id', ondelete='CASCADE'),
           nullable=False
           ),
    Column('name', String, index=True, unique=True, nullable=False)
)

catalog_items = Table(
    'catalog_items',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column(
        'catalog_id', None,
        ForeignKey('catalogs.id', ondelete='CASCADE'),
        nullable=False
    ),
    Column('name', String, index=True, unique=True, nullable=False),
    Column('price', Numeric(precision=10, scale=2), nullable=True)
)

orders = Table(
    'orders',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column('ref_id', String, index=True, nullable=True),
    Column(
        'seller_id', None,
        ForeignKey('parties.id', ondelete='CASCADE'),
        index=True,
        nullable=False
    ),
    Column(
        'customer_id', None,
        ForeignKey('parties.id', ondelete='SET NULL'),
        index=True,
        nullable=True
    ),
    Column('created_at', TIMESTAMP(timezone=True), index=True, nullable=False)
)

order_items = Table(
    'order_items',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column(
        'order_id', None,
        ForeignKey('orders.id', ondelete='CASCADE'),
        index=True,
        nullable=False
    ),
    Column(
        'catalog_item_id', None,
        ForeignKey('catalog_items.id', ondelete='RESTRICT'),
        index=True,
        nullable=False
    ),
    Column('quantity', Integer, nullable=False, default=1),
    Column('base_price', Numeric(precision=10, scale=2), nullable=True)
)

invoice_states = ENUM(
    'DRAFT', 'UNPAID', 'PAID', 'CANCELED',
    name='invoice_states',
    metadata=metadata
)

invoices = Table(
    'invoices',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column('ref_id', String, index=True, nullable=True),
    Column(
        'order_id', None,
        ForeignKey('orders.id', ondelete='CASCADE'),
        index=True,
        nullable=False
    ),
    Column('due_date', Date, index=True, nullable=True),
    Column('state', invoice_states, nullable=False, default='DRAFT')
)

payments = Table(
    'payments',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column(
        'invoice_id', None,
        ForeignKey('invoices.id', ondelete='RESTRICT'),
        index=True,
        nullable=False
    ),
    Column('amount_paid', Numeric(precision=10, scale=2), nullable=False),
    Column('paid_at', TIMESTAMP(timezone=True), index=True, nullable=False),
    Column('blockchain_tx_address', String, index=True, nullable=True)
)

blockchain_contracts = Table(
    'blockchain_contracts',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column('name', String, index=True, unique=True, nullable=False),
    Column('contract_address', String, index=True, nullable=True),
    Column('contract_code', String, nullable=True),
    Column('contract_abi', String, nullable=True)
)

engine = create_engine(
    get_settings().database_url, pool_size=3, max_overflow=0
)


def create_schema():
    metadata.create_all(engine)


async def connect_databases():
    await database.connect()


async def disconnect_databases():
    await database.disconnect()
