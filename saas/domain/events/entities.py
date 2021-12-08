from saas.domain.base import DomainEntity
from saas.domain.exceptions import UserNotAdmin
from saas.domain.users import Profile
from .value_objects import EventContent


class Event(DomainEntity):
    def __init__(self, organizer: 'Profile', content: 'EventContent'):
        if not organizer.user.is_admin:
            raise UserNotAdmin(username=organizer.user.username)

        self.organizer = organizer
        self.content = content

        super().__init__()

    def __repr__(self):
        return f'{self.__class__.__name__}(organizer={self.organizer.user.username}, reference={self.reference})'

    @property
    def content(self):
        return EventContent(
            title=self.title, body=self.body, starts_at=self.starts_at, ends_at=self.ends_at, location=self.location
        )

    @content.setter
    def content(self, content: EventContent):
        self.title = content.title
        self.body = content.body
        self.starts_at = content.starts_at
        self.ends_at = content.ends_at
        self.location = content.location
