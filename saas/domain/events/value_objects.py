import dataclasses
import datetime


@dataclasses.dataclass(frozen=True)
class EventContent:
    starts_at: datetime.datetime
    ends_at: datetime.datetime
    location: str
    title: str
    body: str
