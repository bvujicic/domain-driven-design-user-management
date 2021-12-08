import dataclasses
import uuid
from datetime import datetime, timezone
from typing import Optional


class DomainEntity:
    def __init__(self):
        self.reference: str = str(uuid.uuid4())
        self.event_logs: list = list()
        self.created = datetime.now(tz=timezone.utc)
        self.deleted: Optional[datetime] = None

    def delete(self):
        if self.deleted is None:
            self.deleted = datetime.now(tz=timezone.utc)


@dataclasses.dataclass(frozen=True)
class DomainEvent:
    name: str = dataclasses.field(init=False)
    reference: str = dataclasses.field(default=str(uuid.uuid4()), init=False)
    # occurred: datetime = dataclasses.field(default=datetime.now(tz=timezone.utc), init=False)
