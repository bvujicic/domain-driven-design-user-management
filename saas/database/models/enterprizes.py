import sqlalchemy

from saas.database.metadata import metadata

enterprizes = sqlalchemy.Table(
    'enterprizes',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('reference', sqlalchemy.String(36), unique=True, index=True, nullable=False),
    sqlalchemy.Column('name', sqlalchemy.String),
    sqlalchemy.Column('subdomain', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('created', sqlalchemy.TIMESTAMP(timezone=True)),
)
