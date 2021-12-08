import io
from datetime import date, datetime, timedelta

import pytest
from PIL import Image
from fastapi.testclient import TestClient
from jose import jwt

from saas.core.config import configuration
from saas.domain.events import Event, EventContent
from saas.domain.posts import NewsPost, PostContent, Question
from saas.domain.users import (
    Enterprize,
    UserCredentials,
    FullName,
    UserType,
    Address,
    CompanyStatus,
    Contact,
    Profile,
    LegalStatus,
    EnterprizeNotes,
)
from saas.web.app import web_app
from .repository import FakeProfileRepository, FakePostRepository, FakeEventRepository


# @pytest.fixture(scope='session', autouse=True)
# def mappers():
#     from saas.database.metadata import start_mappers
#
#     start_mappers()


@pytest.fixture(scope='function')
def credentials():
    return UserCredentials(username='boris@mail.com', plain_password='test123')


@pytest.fixture(scope='function')
def other_credentials():
    return UserCredentials(username='test@mail.com', plain_password='test123')


@pytest.fixture(scope='function')
def full_name():
    return FullName(first_name='boris', last_name='test')


@pytest.fixture(scope='function')
def contact():
    address = Address(
        street='Test street',
        zip_code='Test zip code',
        town='Test town',
        country='Test country',
    )
    return Contact(address=address, phone_number='Test number')


@pytest.fixture(scope='function')
def company_status():
    return CompanyStatus(position='Test position', department='Test department')


@pytest.fixture(scope='function')
def photo():
    image = Image.new(mode='RGB', size=(1, 1))
    return io.BytesIO(initial_bytes=image.tobytes())


@pytest.fixture(scope='function')
def user_repository():
    return FakeProfileRepository([])


@pytest.fixture(scope='function')
def enterprize(user_repository):
    enterprize = Enterprize(name='test_enterprize', subdomain='enterprize')
    user_repository.create_enterprize(enterprize=enterprize)

    return enterprize


@pytest.fixture(scope='function')
def other_enterprize(user_repository):
    enterprize = Enterprize(name='other_test_enterprize', subdomain='other_enterprize')
    user_repository.create_enterprize(enterprize=enterprize)

    return enterprize


@pytest.fixture(scope='function')
def profile_with_no_user(user_repository, full_name, enterprize):
    profile = Profile(full_name=full_name, enterprize=enterprize)
    user_repository.save_profile(profile=profile)

    return profile


@pytest.fixture(scope='function')
def profile(user_repository, enterprize, credentials):
    profile = Profile(enterprize=enterprize)
    profile.register_user(credentials=credentials)
    user_repository.save_profile(profile=profile)

    return profile


@pytest.fixture(scope='function')
def preregistered_profile(user_repository, enterprize, credentials):
    profile = Profile(enterprize=enterprize)
    profile.preregister_username(email_address=credentials.username)
    user_repository.save_profile(profile=profile)

    return profile


@pytest.fixture(scope='function')
def active_profile(user_repository, enterprize, credentials):
    profile = Profile(enterprize=enterprize)
    profile.register_user(credentials=credentials)
    profile.activate()
    user_repository.save_profile(profile=profile)

    return profile


@pytest.fixture(scope='function')
def admin_profile(user_repository, enterprize):
    admin_credentials = UserCredentials(username='admin@example.com', plain_password='admin')
    profile = Profile(enterprize=enterprize)
    profile.register_user(credentials=admin_credentials)
    profile.activate()
    profile.user.type = UserType.admin
    user_repository.save_profile(profile=profile)

    return profile


@pytest.fixture(scope='function')
def other_profile(user_repository, other_enterprize):
    other_credentials = UserCredentials(username='other@example.com', plain_password='other')
    profile = Profile(enterprize=other_enterprize)
    profile.register_user(credentials=other_credentials)
    profile.activate()
    profile.user.type = UserType.admin
    user_repository.save_profile(profile=profile)

    return profile


@pytest.fixture(scope='function')
def other_admin_profile(user_repository, other_enterprize):
    admin_credentials = UserCredentials(username='other_admin@example.com', plain_password='admin')
    profile = Profile(enterprize=other_enterprize)
    profile.register_user(credentials=admin_credentials)
    profile.activate()
    profile.user.type = UserType.admin
    user_repository.save_profile(profile=profile)

    return profile


@pytest.fixture(scope='function')
def user(profile):
    return profile.user


@pytest.fixture(scope='function')
def active_user(active_profile):
    return active_profile.user


@pytest.fixture(scope='function')
def admin_user(admin_profile):
    return admin_profile.user


@pytest.fixture(scope='function')
def other_user(other_profile):
    return other_profile.user


@pytest.fixture(scope='function')
def other_admin_user(other_admin_profile):
    return other_admin_profile.user


@pytest.fixture(scope='function')
def enterprize_notes():
    return EnterprizeNotes(
        legal_status=LegalStatus.retirement,
        exit_notes='text',
        enter_date=date.today() - timedelta(days=365),
        exit_date=date.today(),
    )


@pytest.fixture(scope='function')
def post_repository():
    return FakePostRepository()


@pytest.fixture(scope='function')
def post_content():
    return PostContent(title='Title', body='Text')


@pytest.fixture(scope='function')
def news_post(post_content, admin_profile, post_repository):
    news_post = NewsPost(author=admin_profile, content=post_content)
    post_repository.add_news_post(post=news_post)

    return news_post


@pytest.fixture(scope='function')
def question(post_content, profile, post_repository):
    question = Question(author=profile, content=post_content)
    question.tags = {'tag1', 'tag2', 'tag3'}
    post_repository.add_question(question=question)

    return question


@pytest.fixture(scope='function')
def event_content():
    return EventContent(
        title='Title',
        body='Text',
        starts_at=datetime.now(),
        ends_at=datetime.now() + timedelta(hours=1),
        location='Here',
    )


@pytest.fixture(scope='function')
def event(event_content, admin_profile):
    return Event(organizer=admin_profile, content=event_content)


@pytest.fixture(scope='function')
def other_event(event_content, other_admin_profile):
    return Event(organizer=other_admin_profile, content=event_content)


@pytest.fixture(scope='function')
def event_repository(event, other_event):
    return FakeEventRepository([event, other_event])


@pytest.fixture(scope='function')
def http_client(user_repository, post_repository, event_repository):
    from saas.web.session import profile_database, post_database, event_database

    def fake_user_repository():
        return user_repository

    def fake_post_repository():
        return post_repository

    def fake_event_repository():
        return event_repository

    web_app.dependency_overrides[profile_database] = fake_user_repository
    web_app.dependency_overrides[post_database] = fake_post_repository
    web_app.dependency_overrides[event_database] = fake_event_repository

    return TestClient(app=web_app)


@pytest.fixture(scope='function')
def access_token(user):
    return jwt.encode(
        claims={'username': user.username, 'sub': 'access'},
        key=configuration.SECRET_KEY,
        algorithm=configuration.JWT_ALGORITHM,
    )


@pytest.fixture(scope='function')
def other_access_token(other_credentials):
    return jwt.encode(
        claims={'username': other_credentials.username, 'sub': 'access'},
        key=configuration.SECRET_KEY,
        algorithm=configuration.JWT_ALGORITHM,
    )


@pytest.fixture(scope='function')
def admin_access_token(admin_user):
    return jwt.encode(
        claims={'username': admin_user.username, 'sub': 'access'},
        key=configuration.SECRET_KEY,
        algorithm=configuration.JWT_ALGORITHM,
    )


@pytest.fixture(scope='function')
def other_admin_access_token(other_admin_user):
    return jwt.encode(
        claims={'username': other_admin_user.username, 'sub': 'access'},
        key=configuration.SECRET_KEY,
        algorithm=configuration.JWT_ALGORITHM,
    )


@pytest.fixture(scope='function')
def profile_activation_token(user):
    return jwt.encode(
        claims={'username': user.username, 'sub': 'activation'},
        key=configuration.SECRET_KEY,
        algorithm=configuration.JWT_ALGORITHM,
    )


@pytest.fixture(scope='function')
def active_profile_activation_token(active_user):
    return jwt.encode(
        claims={'username': active_user.username, 'sub': 'activation'},
        key=configuration.SECRET_KEY,
        algorithm=configuration.JWT_ALGORITHM,
    )


@pytest.fixture(scope='function')
def password_change_token(user):
    return jwt.encode(
        claims={'username': user.username, 'sub': 'password'},
        key=configuration.SECRET_KEY,
        algorithm=configuration.JWT_ALGORITHM,
    )


@pytest.fixture(scope='function')
def username_change_token(active_user, other_credentials):
    return jwt.encode(
        claims={'username': active_user.username, 'new_username': other_credentials.username, 'sub': 'username'},
        key=configuration.SECRET_KEY,
        algorithm=configuration.JWT_ALGORITHM,
    )


# @pytest.fixture(scope='function')
# def test_file(tmp_path):
#     return io.BytesIO(b'byte_data')
