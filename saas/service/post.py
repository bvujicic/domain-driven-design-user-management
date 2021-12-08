from typing import Optional
from saas.domain.posts import NewsPost, PostContent, PostAbstractRepository, Question, Answer
from saas.domain.users import Enterprize, Profile
from saas.domain.exceptions import PostDoesNotExist


def create_post(repository: 'PostAbstractRepository', author: 'Profile', content: 'PostContent') -> 'NewsPost':
    post = NewsPost(author=author, content=content)

    repository.add_news_post(post=post)

    return post


def list_posts_by_enterprize(enterprize: 'Enterprize', repository: 'PostAbstractRepository') -> list['NewsPost']:
    posts = repository.list_for_enterprize(enterprize=enterprize)
    return posts


def delete_news_post(news_post_id: str, admin_username: str, repository: 'PostAbstractRepository'):
    news_post = repository.retrieve_news_post_by_admin(reference=news_post_id, admin_username=admin_username)

    if news_post.deleted is not None:
        raise PostDoesNotExist(reference=news_post.reference)

    news_post.delete()

    repository.add_news_post(post=news_post)


def post_question(
    repository: 'PostAbstractRepository', author: 'Profile', content: 'PostContent', tags: Optional[set] = None
) -> 'Question':
    question = Question(author=author, content=content)
    question.tags = tags

    repository.add_question(question=question)

    return question


def retrieve_question(reference: str, repository: 'PostAbstractRepository') -> 'Question':
    question = repository.retrieve_question(reference=reference)

    return question


def create_answer(
    author: 'Profile', content: 'PostContent', question: 'Question', repository: 'PostAbstractRepository'
) -> 'Answer':
    answer = Answer(author=author, content=content, question=question)

    repository.add_answer(answer=answer)

    return answer


def retrieve_answers_to_question(question_reference: str, repository: 'PostAbstractRepository') -> list['Answer']:
    answers = repository.retrieve_answers_for_question(question_reference=question_reference)

    return answers


def list_questions_by_enterprize(enterprize: 'Enterprize', repository: 'PostAbstractRepository') -> list['Question']:
    questions = repository.list_questions_for_enterprize(enterprize=enterprize)

    return questions
