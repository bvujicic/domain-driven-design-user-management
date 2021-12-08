from saas.service.post import (
    create_post,
    list_posts_by_enterprize,
    post_question,
    retrieve_question,
    create_answer,
    retrieve_answers_to_question,
    list_questions_by_enterprize,
    delete_news_post,
)
from saas.domain.exceptions import PostDoesNotExist
import pytest


class TestNewsPostService:
    def test_admin_can_create_news_post(self, admin_profile, post_content, post_repository):
        post = create_post(author=admin_profile, content=post_content, repository=post_repository)

        assert post.author == admin_profile
        assert post.content == post_content

    def test_can_list_news_posts_by_enterprize(self, enterprize, news_post, post_repository):
        posts = list_posts_by_enterprize(enterprize=enterprize, repository=post_repository)

        assert news_post in posts

    def test_admin_can_delete_news_post(self, admin_profile, news_post, post_repository):
        delete_news_post(
            news_post_id=news_post.reference, admin_username=admin_profile.username, repository=post_repository
        )

        assert news_post.deleted is not None

    def test_admin_cannot_delete_already_delete_news_post(self, admin_profile, news_post, post_repository):
        with pytest.raises(PostDoesNotExist):
            delete_news_post(
                news_post_id=news_post.reference, admin_username=admin_profile.username, repository=post_repository
            )
            delete_news_post(
                news_post_id=news_post.reference, admin_username=admin_profile.username, repository=post_repository
            )

    def test_wrong_admin_cannot_delete_news_post(self, other_admin_profile, news_post, post_repository):
        with pytest.raises(PostDoesNotExist):
            delete_news_post(
                admin_username=other_admin_profile.username,
                news_post_id=news_post.reference,
                repository=post_repository,
            )

    def test_user_cannot_delete_news_post(self, profile, news_post, post_repository):
        with pytest.raises(PostDoesNotExist):
            delete_news_post(
                admin_username=profile.username,
                news_post_id=news_post.reference,
                repository=post_repository,
            )


class TestQAService:
    tags = {'tag1', 'tag2', 'tag3'}

    def test_post_question(self, profile, post_content, post_repository):
        question = post_question(author=profile, content=post_content, repository=post_repository)

        assert question.author == profile
        assert question.content == post_content

    def test_post_question_with_tags(self, profile, post_content, post_repository):
        question = post_question(author=profile, content=post_content, repository=post_repository, tags=self.tags)

        assert question.author == profile
        assert question.content == post_content
        assert question.tags == self.tags

    def test_list_questions_by_enterprize(self, profile, question, post_repository):
        questions = list_questions_by_enterprize(enterprize=profile.enterprize, repository=post_repository)

        assert question in questions

    def test_retrieve_question(self, question, post_repository):
        retrieved_question = retrieve_question(reference=question.reference, repository=post_repository)

        assert retrieved_question is question

    def test_post_answer(self, profile, question, post_content, post_repository):
        answer = create_answer(author=profile, content=post_content, question=question, repository=post_repository)

        assert answer.author == profile
        assert answer.question == question
        assert answer in question.answers

    def test_retrieve_answers_for_question(self, question, post_repository):
        answers = retrieve_answers_to_question(question_reference=question.reference, repository=post_repository)

        assert answers == question.answers
