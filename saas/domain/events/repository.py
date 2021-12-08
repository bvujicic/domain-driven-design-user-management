import abc

from .entities import Event


class EventAbstractRepository(abc.ABC):
    @abc.abstractmethod
    def save_event(self, event: Event):
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve(self, reference: str):
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_event_by_admin(self, reference: str, admin_username: str):
        raise NotImplementedError

    @abc.abstractmethod
    def list_events_for_enterprize(self, enterprize_reference: str):
        raise NotImplementedError
