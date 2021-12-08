from datetime import datetime, timezone
from typing import Dict

import sqlalchemy.exc
from sqlalchemy.dialects.postgresql import JSONB

from saas.database.metadata import metadata

system_event_logs = sqlalchemy.Table(
    'system_event_logs',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('stream_reference', sqlalchemy.String(36), index=True, nullable=False),
    sqlalchemy.Column('created', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column('payload', JSONB),
)


class SystemEvent:
    def __init__(self, stream_reference: str, payload: Dict):
        self.created = datetime.now(tz=timezone.utc)
        self.stream_reference = stream_reference
        self.payload = payload
