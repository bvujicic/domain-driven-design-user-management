from fastapi import Depends

from saas.database.models import ProfileRepository, PostRepository, EventRepository
from saas.database.session import DatabaseSession


def database_session():
    session = DatabaseSession()
    try:
        return session

    finally:
        session.close()


def profile_database(session: DatabaseSession = Depends(database_session)):
    return ProfileRepository(session=session)


def post_database(session: DatabaseSession = Depends(database_session)):
    return PostRepository(session=session)


def event_database(session: DatabaseSession = Depends(database_session)):
    return EventRepository(session=session)
