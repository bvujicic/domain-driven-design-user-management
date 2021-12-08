from typing import Optional, Set, TYPE_CHECKING
from datetime import datetime, timezone

from saas.domain.base import DomainEntity
from saas.domain.exceptions import UserNotAdmin
from .value_objects import PostContent

if TYPE_CHECKING:
    from saas.domain.users import Profile


class Post(DomainEntity):
    def __init__(self, author: 'Profile', content: 'PostContent'):
        super().__init__()

        self.author = author
        self.content = content
        self.tags: Set = set()
        self.created = datetime.now(tz=timezone.utc)

    def __repr__(self):
        return f'{self.__class__.__name__}(author={self.author.user.username}, reference={self.reference})'

    @property
    def content(self):
        return PostContent(title=self.title, body=self.body)

    @content.setter
    def content(self, content: PostContent):
        self.title = content.title
        self.body = content.body

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        self._tags = set(value) if value is not None else set()


class NewsPost(Post):
    def __init__(self, author: 'Profile', content: 'PostContent'):
        if not author.user.is_admin:
            raise UserNotAdmin(username=author.user.username)

        super().__init__(author=author, content=content)


class Question(Post):
    def __init__(self, author: 'Profile', content: 'PostContent'):
        super().__init__(author=author, content=content)

        self.question = None
        self.answers: list[Optional[Post]] = []


class Answer(Post):
    def __init__(self, author: 'Profile', question: 'Question', content: 'PostContent'):
        super().__init__(author=author, content=content)

        self.question: Question = question
        self.answers: list[Optional[Post]] = list()

        self.question.answers.append(self)
