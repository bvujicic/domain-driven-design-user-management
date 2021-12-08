import sqlalchemy
from sqlalchemy.orm import exc

from saas.database.metadata import metadata
from saas.domain.events import EventAbstractRepository, Event
from saas.domain.exceptions import EventDoesNotExist
from .profiles import profiles
from saas.domain.users import Profile, User, UserType, Enterprize

events = sqlalchemy.Table(
    'events',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('reference', sqlalchemy.String(36), unique=True, index=True, nullable=False),
    sqlalchemy.Column('title', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('body', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('location', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('starts_at', sqlalchemy.TIMESTAMP(timezone=True), nullable=False),
    sqlalchemy.Column('ends_at', sqlalchemy.TIMESTAMP(timezone=True), nullable=False),
    sqlalchemy.Column('created', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column('deleted', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column(
        'organizer_id',
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey(profiles.c.id),
        index=True,
        nullable=False,
    ),
)


class EventRepository(EventAbstractRepository):
    def __init__(self, session):
        self.session = session

    def save_event(self, event: Event):
        self.session.add(event)
        self.session.commit()

    def retrieve(self, reference: str) -> Event:
        try:
            return self.session.query(Event).filter_by(reference=reference).one()
        except exc.NoResultFound:
            raise EventDoesNotExist(reference=reference)

    def retrieve_event_by_admin(self, reference: str, admin_username: str):
        try:
            admin = (
                self.session.query(Profile)
                .join(User)
                .filter(User.username == admin_username, User.type == UserType.admin)
                .one()
            )
            return (
                self.session.query(Event)
                .join(Profile)
                .filter(Event.reference == reference, Profile.enterprize == admin.enterprize)
                .one()
            )
        except exc.NoResultFound:
            raise EventDoesNotExist(reference=reference)

    def list_events_for_enterprize(self, enterprize_reference: str):
        profile_ids = self._list_profile_ids_for_enterprize(enterprize_reference=enterprize_reference)

        return list(
            self.session.query(Event)
            .filter(Event.organizer_id.in_(profile_ids), Event.deleted.is_(None))  # type: ignore
            .order_by(Event.created.desc())  # type: ignore
        )

    def _list_profile_ids_for_enterprize(self, enterprize_reference: str):
        return self.session.query(Profile.id).filter(Enterprize.reference == enterprize_reference)  # type: ignore
