from saas.domain.events import Event, EventContent, EventAbstractRepository
from saas.domain.exceptions import EventDoesNotExist
from saas.domain.users import Profile, Enterprize


def create_event(organizer: 'Profile', content: 'EventContent', repository: 'EventAbstractRepository') -> 'Event':
    event = Event(organizer=organizer, content=content)
    repository.save_event(event=event)

    return event


def delete_event(event_id: str, admin_username: str, repository: 'EventAbstractRepository'):
    event = repository.retrieve_event_by_admin(reference=event_id, admin_username=admin_username)

    if event.deleted is not None:
        raise EventDoesNotExist(reference=event_id)

    event.delete()
    repository.save_event(event=event)


def list_events_by_enterprize(enterprize: Enterprize, repository: EventAbstractRepository) -> list[Event]:
    events = repository.list_events_for_enterprize(enterprize_reference=enterprize.reference)
    return events
