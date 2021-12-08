import pytest

from saas.domain.exceptions import UserNotAdmin
from saas.domain.posts import NewsPost, PostContent, Question, Answer


class TestPost:
    post_content = PostContent(title='Test title', body='Test body')

    def test_can_create_post_by_admin(self, admin_profile):
        post = NewsPost(author=admin_profile, content=self.post_content)

        assert post.author.user.is_admin
        assert post.author == admin_profile
        assert post.tags == set()

    def test_cannot_create_post_by_user(self, profile):
        with pytest.raises(UserNotAdmin):
            NewsPost(author=profile, content=self.post_content)


class TestQA:
    question_content = PostContent(title='Question', body='This is the question?')
    answer_content = PostContent(title=None, body='This is the answer.')
    tags = {'tag1', 'tag2', 'tag3'}

    def test_can_create_question(self, active_profile):
        question = Question(author=active_profile, content=self.question_content)

        assert question.author == active_profile
        assert question.content == self.question_content
        assert question.question is None
        assert not question.answers

    def test_can_add_tags_to_question(self, active_profile):
        question = Question(author=active_profile, content=self.question_content)

        question.tags = ['tag1', 'tag2', 'tag3', 'tag2']

        assert question.tags == self.tags

    def test_can_create_answer_to_question(self, active_profile):
        question = Question(author=active_profile, content=self.question_content)
        answer = Answer(author=active_profile, question=question, content=self.answer_content)

        assert answer.author == active_profile
        assert answer.content == self.answer_content
        assert answer.question == question
        assert answer in question.answers
        assert not answer.answers
