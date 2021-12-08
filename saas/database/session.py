from datetime import datetime, date
from enum import Enum
import json

import sqlalchemy.orm
import sqlalchemy.engine.url
import sqlalchemy.dialects.sqlite

from saas.core.config import configuration


def _default(value):
    if isinstance(value, datetime) or isinstance(value, date):
        return value.isoformat()
    elif isinstance(value, Enum):
        return value.value
    return value


def dumps(d):
    return json.dumps(d, default=_default)


database_engine_url = sqlalchemy.engine.url.make_url(name_or_url=configuration.DATABASE_URI)

if database_engine_url.get_dialect() == sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite:
    database_engine = sqlalchemy.create_engine(database_engine_url, echo=configuration.DEBUG)
else:
    database_engine = sqlalchemy.create_engine(
        database_engine_url, pool_size=10, max_overflow=20, echo=configuration.DEBUG, json_serializer=dumps
    )


DatabaseSession = sqlalchemy.orm.sessionmaker(bind=database_engine, autocommit=False, autoflush=False)


def create_session():
    from .metadata import start_mappers

    session = DatabaseSession()
    start_mappers()

    return session
