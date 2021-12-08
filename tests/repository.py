from typing import Any

from saas.domain.events import Event, EventAbstractRepository
from saas.domain.exceptions import PostDoesNotExist, EventDoesNotExist
from saas.domain.posts import NewsPost, PostAbstractRepository, Question, Answer
from saas.domain.users import Enterprize, User, ProfileAbstractRepository, Profile
from saas.domain.exceptions import (
    UsernameDoesNotExist,
    UserDoesNotExist,
    EnterprizeExists,
    EnterprizeDoesNotExist,
)


class FakeProfileRepository(ProfileAbstractRepository):
    def __init__(self, users: list[User]):
        self._profiles: set[Profile] = set()
        self._users: set[User] = set(users)
        self._enterprizes: set[Enterprize] = set()

    def save_profile(self, profile: 'Profile'):
        self._profiles.add(profile)

    def upload_photo(self, profile: Profile, photo: Any):
        profile.photo = photo
        self._profiles.add(profile)

        return str(photo)

    def delete_photo(self, profile: Profile):
        profile.photo = None
        self._profiles.add(profile)

    def create_enterprize(self, enterprize: Enterprize):
        if enterprize.subdomain in (enterprize.subdomain for enterprize in self._enterprizes):
            raise EnterprizeExists(subdomain=enterprize.subdomain)

        self._enterprizes.add(enterprize)

    def retrieve_profile(self, reference: str) -> Profile:
        try:
            return next(profile for profile in self._profiles if profile.reference == reference)
        except StopIteration:
            raise UserDoesNotExist(reference=reference)

    def retrieve_profiles_for_admin(self, admin_username: str) -> list[Profile]:
        admin = next(
            profile
            for profile in self._profiles
            if profile.user is not None and profile.user.username.lower() == admin_username.lower()
        )
        return list(
            profile
            for profile in self._profiles
            if profile.user is not None and profile.enterprize == admin.enterprize
        )

    def retrieve_invited_profiles_for_admin(self, admin_username: str) -> list[Profile]:
        return self.retrieve_profiles_for_admin(admin_username=admin_username)

    def retrieve_by_username(self, username: str) -> Profile:
        try:
            return next(
                profile
                for profile in self._profiles
                if profile.user is not None and profile.user.username.lower() == username.lower()
            )
        except StopIteration:
            raise UsernameDoesNotExist(username=username)

    def retrieve_by_username_allowed_to_register(self, username: str) -> Profile:
        try:
            return next(
                profile
                for profile in self._profiles
                if profile.user is not None
                and profile.user.username.lower() == username.lower()
                and profile.user.password is None
            )
        except StopIteration:
            raise UsernameDoesNotExist(username=username)

    def retrieve_enterprize(self, enterprize_subdomain: str) -> Enterprize:
        try:
            return next(enterprize for enterprize in self._enterprizes if enterprize_subdomain == enterprize.subdomain)
        except StopIteration:
            raise EnterprizeDoesNotExist(subdomain=enterprize_subdomain)

    def retrieve_dashboard_statistics(self, admin_username: str) -> dict[str, int]:
        admin = next(profile for profile in self._profiles if profile.user.username.lower() == admin_username.lower())
        active_registrations = len(
            [
                profile
                for profile in self._profiles
                if profile.enterprize == admin.enterprize and profile.user.is_active
            ]
        )
        total_registrations = len([profile for profile in self._profiles if profile.enterprize == admin.enterprize])
        accepted_invitations = len(
            [
                profile
                for profile in self._profiles
                if profile.enterprize == admin.enterprize
                and profile.user.is_active
                and profile.user.invited is not None
            ]
        )
        total_invitations = len(
            [
                profile
                for profile in self._profiles
                if profile.enterprize == admin.enterprize and profile.user.invited is not None
            ]
        )
        return {
            'active_registrations': active_registrations,
            'total_registrations': total_registrations,
            'accepted_invitations': accepted_invitations,
            'total_invitations': total_invitations,
        }


class FakePostRepository(PostAbstractRepository):
    def __init__(self):
        self._qa_posts = set()
        self._news_posts = set()
        self._admin_profiles = set()

    def list_for_enterprize(self, enterprize: Enterprize):
        return list(post for post in self._news_posts if post.author.enterprize == enterprize)

    def list_questions_for_enterprize(self, enterprize: Enterprize):
        return list(question for question in self._qa_posts if question.author.enterprize == enterprize)

    def add_news_post(self, post: NewsPost):
        self._news_posts.add(post)
        self._admin_profiles.add(post.author)

    def retrieve_news_post(self, reference: str) -> NewsPost:
        try:
            return next(post for post in self._news_posts if post.reference == reference)
        except StopIteration:
            raise PostDoesNotExist(reference=reference)

    def retrieve_news_post_by_admin(self, reference: str, admin_username: str):
        try:
            admin = next(profile for profile in self._admin_profiles if profile.user.username == admin_username)
            return next(
                news_post
                for news_post in self._news_posts
                if news_post.reference == reference and news_post.author.enterprize == admin.enterprize
            )
        except StopIteration:
            raise PostDoesNotExist(reference=reference)

    def retrieve_news_posts_by_tag(self, tag: str):
        try:
            return next(news_post for news_post in self._news_posts if tag in news_post.tags)
        except StopIteration:
            return list()

    def add_question(self, question: Question):
        self._qa_posts.add(question)

    def retrieve_question(self, reference: str):
        try:
            return next(question for question in self._qa_posts if question.reference == reference)
        except StopIteration:
            raise PostDoesNotExist(reference=reference)

    def retrieve_answers_for_question(self, question_reference: str) -> list['Answer']:
        question = self.retrieve_question(reference=question_reference)

        return question.answers

    def add_answer(self, answer: Answer):
        self._qa_posts.add(answer)


class FakeEventRepository(EventAbstractRepository):
    def __init__(self, events: list[Event] = None):
        if events is None:
            self._events = set()
            self._admin_profiles = set()
        else:
            self._events = set(events)
            self._admin_profiles = set(event.organizer for event in events)

    def save_event(self, event: Event):
        self._events.add(event)
        self._admin_profiles.add(event.organizer)

    def retrieve(self, reference: str) -> Event:
        try:
            return next(event for event in self._events if event.reference == reference)
        except StopIteration:
            raise EventDoesNotExist(reference=reference)

    def retrieve_event_by_admin(self, reference: str, admin_username: str):
        try:
            admin = next(profile for profile in self._admin_profiles if profile.user.username == admin_username)
            return next(
                event
                for event in self._events
                if event.reference == reference and event.organizer.enterprize == admin.enterprize
            )
        except StopIteration:
            raise EventDoesNotExist(reference=reference)

    def retrieve_event_by_enterprize(self, reference: str, enterprize_reference: str):
        try:
            return next(
                event
                for event in self._events
                if event.reference == reference and event.organizer.enterprize.reference == enterprize_reference
            )
        except StopIteration:
            raise EventDoesNotExist(reference=reference)

    def list_events_for_enterprize(self, enterprize_reference: str):
        return list(event for event in self._events if event.organizer.enterprize.reference == enterprize_reference)
