from databases import Database
from sqlalchemy import (
    MetaData,
    Table, Column, ForeignKey,
    Integer, String, Boolean, Numeric, Date,
    create_engine, pool
)
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.dialects.postgresql import (
    UUID, ENUM
)

from .config import get_settings

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

blockchain_contracts = Table(
    'blockchain_contracts',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column('name', String, index=True, unique=False, nullable=False),
    Column('contract_address', String, index=True, nullable=True),
    Column('contract_code', String, nullable=True),
    Column('contract_abi', String, nullable=True),
    Column(
        'owner_id', None,
        ForeignKey('parties.id', ondelete='RESTRICT'),
        nullable=False
    )
)

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column('username', String, index=True, unique=True, nullable=False),
    Column('hashed_password', String, nullable=False),
    Column('email', String, index=True, nullable=True),
    Column('name', String, index=True, nullable=True),
    Column('is_active', Boolean, nullable=False, default=False),
    Column('is_superuser', Boolean, nullable=False, default=False)
)

catalogs = Table(
    'catalogs',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', UUID, index=True, unique=True, nullable=False),
    Column(
        'seller_id', None,
        ForeignKey('parties.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    ),
    Column('name', String, index=True, unique=False, nullable=False)
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
    Column('name', String, index=True, unique=False, nullable=False),
    Column('price', Numeric(precision=10, scale=2), nullable=True)
)

# TODO: define uniqueness on (ref_id, seller_id, customer_id)
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
    Column('created_at', TIMESTAMP(timezone=True), index=True, nullable=False),
    Column('amount', Numeric(precision=10, scale=2), nullable=True)
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
    Column('amount', Numeric(precision=10, scale=2), nullable=False),
    Column('paid_at', TIMESTAMP(timezone=True), index=True, nullable=False),
    Column('blockchain_tx_hash', String, index=True, nullable=True)
)


class DbClient:
    metadata: MetaData = None
    database: Database = None
    engine = None

    def __init__(self, _metadata):
        self.metadata = _metadata
        self.engine = create_engine(
            get_settings().database_url,
            poolclass=pool.NullPool
        )
        self.database = Database(
            get_settings().database_url,
            min_size=1, max_size=1, ssl=True
        )

    def create_schema(self):
        self.metadata.create_all(self.engine)

    async def connect(self):
        await self.database.connect()

    async def disconnect(self):
        await self.database.disconnect()


db_client = DbClient(metadata)


def get_db() -> Database:
    return db_client.database
