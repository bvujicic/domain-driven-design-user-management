from sqlalchemy import MetaData
from sqlalchemy.orm import foreign, remote

metadata = MetaData()


def start_mappers():
    from saas.database.models import (
        users,
        profiles,
        enterprizes,
        posts,
        qa_posts,
        system_event_logs,
        events,
        SystemEvent,
    )
    from saas.domain.events import Event
    from saas.domain.users import User, Profile, Enterprize
    from saas.domain.posts import NewsPost, Question, Answer
    from sqlalchemy.orm import mapper, relationship

    mapper(SystemEvent, system_event_logs)
    mapper(
        Enterprize,
        enterprizes,
        properties={'profiles': relationship(Profile, backref='enterprize')},
    )
    mapper(
        Profile,
        profiles,
        properties={
            'user': relationship(User, backref='profile', uselist=False),
            'questions': relationship(Question, backref='author'),
            'answers': relationship(Answer, backref='author'),
            'system_events': relationship(
                SystemEvent,
                backref='profile',
                primaryjoin=(foreign(system_event_logs.c.stream_reference) == remote(profiles.c.reference)),
            ),
        },
    )
    mapper(User, users, properties={'_password': users.c.password})

    mapper(NewsPost, posts, properties={'author': relationship(Profile, backref='news_posts')})
    mapper(Question, qa_posts, properties={'answers': relationship(Answer)})
    mapper(Answer, qa_posts)
    mapper(Event, events, properties={'organizer': relationship(Profile, backref='events')})


def create_tables():
    from saas.domain.models import User, Enterprize  # noqa: F401
    from saas.database.session import database_engine

    metadata.create_all(bind=database_engine)


def drop_tables():
    from saas.domain.models import User, Enterprize  # noqa: F401
    from saas.database.session import database_engine

    metadata.drop_all(bind=database_engine)
