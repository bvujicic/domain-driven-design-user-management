import pytest

from saas.domain.events import Event
from saas.domain.exceptions import UserNotAdmin


class TestEventsDomain:
    def test_can_create_event(self, admin_profile, event_content):
        event = Event(organizer=admin_profile, content=event_content)

        assert event.reference
        assert event.organizer == admin_profile
        assert event.content

    def test_cannot_create_event_by_user(self, profile, event_content):
        with pytest.raises(UserNotAdmin):
            Event(organizer=profile, content=event_content)

    def test_can_delete_event(self, event):
        event.delete()

        assert event.deleted is not None
