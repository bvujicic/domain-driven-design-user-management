import abc

from saas.domain.users import Enterprize
from .entities import NewsPost, Question, Answer


class PostAbstractRepository(abc.ABC):
    @abc.abstractmethod
    def list_for_enterprize(self, enterprize: Enterprize):
        raise NotImplementedError

    @abc.abstractmethod
    def list_questions_for_enterprize(self, enterprize: Enterprize):
        raise NotImplementedError

    @abc.abstractmethod
    def add_news_post(self, post: NewsPost):
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_news_post(self, reference: str):
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_news_post_by_admin(self, reference: str, admin_username: str):
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_news_posts_by_tag(self, tag: str):
        raise NotImplementedError

    @abc.abstractmethod
    def add_question(self, question: Question):
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_question(self, reference: str):
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_answers_for_question(self, question_reference: str):
        raise NotImplementedError

    @abc.abstractmethod
    def add_answer(self, answer: Answer):
        raise NotImplementedError
