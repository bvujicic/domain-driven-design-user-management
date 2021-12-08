from saas.service.event import create_event, delete_event, list_events_by_enterprize
from saas.domain.exceptions import EventDoesNotExist
import pytest


class TestEvents:
    def test_admin_can_create_event(self, admin_profile, event_content, event_repository):
        event = create_event(organizer=admin_profile, content=event_content, repository=event_repository)

        assert event.organizer == admin_profile
        assert event.content == event_content

    def test_admin_can_delete_event(self, admin_profile, event, event_repository):
        delete_event(admin_username=admin_profile.username, event_id=event.reference, repository=event_repository)
        assert event.deleted is not None

    def test_admin_cannot_delete_already_deleted_event(self, admin_profile, event, event_repository):
        with pytest.raises(EventDoesNotExist):
            delete_event(admin_username=admin_profile.username, event_id=event.reference, repository=event_repository)
            delete_event(admin_username=admin_profile.username, event_id=event.reference, repository=event_repository)

    def test_wrong_admin_cannot_delete_event(self, other_admin_profile, event, event_repository):
        with pytest.raises(EventDoesNotExist):
            delete_event(
                admin_username=other_admin_profile.username,
                event_id=event.reference,
                repository=event_repository,
            )

    def test_user_cannot_delete_event(self, profile, event, event_repository):
        with pytest.raises(EventDoesNotExist):
            delete_event(
                admin_username=profile.username,
                event_id=event.reference,
                repository=event_repository,
            )

    def test_list_events_for_enterprize(self, enterprize, event, event_repository):
        events = list_events_by_enterprize(enterprize=enterprize, repository=event_repository)

        assert event in events

    def test_list_event_for_enterprize_empty(self, enterprize, other_event, event_repository):
        events = list_events_by_enterprize(enterprize=enterprize, repository=event_repository)

        assert other_event not in events
