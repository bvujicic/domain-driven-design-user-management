import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class PostContent:
    title: Optional[str]
    body: str
