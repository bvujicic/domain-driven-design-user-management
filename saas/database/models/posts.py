import sqlalchemy
from sqlalchemy.orm import exc

from saas.database.metadata import metadata
from saas.domain.exceptions import PostDoesNotExist
from saas.domain.posts import PostAbstractRepository, NewsPost, Question, Answer
from saas.domain.users import Enterprize, Profile, User, UserType
from .profiles import profiles

posts = sqlalchemy.Table(
    'posts',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('reference', sqlalchemy.String(36), unique=True, index=True, nullable=False),
    sqlalchemy.Column('title', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('body', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('created', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column('deleted', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column(
        'author_id',
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey(profiles.c.id),
        index=True,
        nullable=False,
    ),
)

qa_posts = sqlalchemy.Table(
    'qa_posts',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('reference', sqlalchemy.String(36), unique=True, index=True, nullable=False),
    sqlalchemy.Column('title', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('body', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('created', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column('deleted', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column(
        'author_id',
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey(profiles.c.id),
        index=True,
        nullable=False,
    ),
    sqlalchemy.Column('parent_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('qa_posts.id'), index=True),
)

# tags = sqlalchemy.Table(
#     'tags',
#     metadata,
#     sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
#     sqlalchemy.Column('reference', sqlalchemy.String(36), unique=True, index=True),
#     sqlalchemy.Column('tag', sqlalchemy.String, index=True),
#     sqlalchemy.Column('created', sqlalchemy.TIMESTAMP(timezone=True)),
# )
#
# qa_posts_tags_association = sqlalchemy.Table(
#     'qa_posts_tags',
#     metadata,
#     sqlalchemy.Column('tag_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('tags.id')),
#     sqlalchemy.Column('qa_post_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('qa_posts_id')),
# )


class PostRepository(PostAbstractRepository):
    def __init__(self, session):
        self.session = session

    def add_news_post(self, post: 'NewsPost'):
        self.session.add(post)
        self.session.commit()

    def list_for_enterprize(self, enterprize: 'Enterprize') -> list['NewsPost']:
        profile_ids = self._list_profile_ids_for_enterprize(enterprize=enterprize)

        return list(
            self.session.query(NewsPost)
            .filter(NewsPost.author_id.in_(profile_ids), NewsPost.deleted.is_(None))  # type: ignore
            .order_by(NewsPost.created.desc())  # type: ignore
        )

    def list_questions_for_enterprize(self, enterprize: 'Enterprize') -> list['Question']:
        profile_ids = self._list_profile_ids_for_enterprize(enterprize=enterprize)

        return list(
            self.session.query(Question)
            .filter(Question.author_id.in_(profile_ids), Question.parent_id.is_(None))  # type: ignore
            .order_by(Question.created.desc())  # type: ignore
        )

    def retrieve_news_post(self, reference: str) -> 'NewsPost':
        try:
            return (
                self.session.query(NewsPost).filter(NewsPost.reference == reference, NewsPost.deleted.is_(None)).one()  # type: ignore
            )
        except exc.NoResultFound:
            raise PostDoesNotExist(reference=reference)

    def retrieve_news_post_by_admin(self, reference: str, admin_username: str):
        try:
            admin = (
                self.session.query(Profile)
                .join(User)
                .filter(User.username == admin_username, User.type == UserType.admin)
                .one()
            )
            return (
                self.session.query(NewsPost)
                .join(Profile)
                .filter(NewsPost.reference == reference, Profile.enterprize == admin.enterprize)
                .one()
            )
        except exc.NoResultFound:
            raise PostDoesNotExist(reference=reference)

    def retrieve_news_posts_by_tag(self, tag: str):
        pass

    def add_question(self, question: 'Question'):
        self.session.add(question)
        self.session.commit()

    def retrieve_question(self, reference: str):
        try:
            return self.session.query(Question).filter_by(reference=reference).one()
        except exc.NoResultFound:
            raise PostDoesNotExist(reference=reference)

    def retrieve_answers_for_question(self, question_reference: str):
        pass

    def add_answer(self, answer: 'Answer'):
        self.session.add(answer)
        self.session.commit()

    def _list_profile_ids_for_enterprize(self, enterprize: 'Enterprize'):
        return self.session.query(Profile.id).filter_by(enterprize_id=enterprize.id)  # type: ignore
