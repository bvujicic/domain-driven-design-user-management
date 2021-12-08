from saas.core.config import configuration
from saas.database.models import ProfileRepository
from saas.database.session import create_session
from saas.domain.exceptions import EnterprizeDoesNotExist, UsernameDoesNotExist
from saas.domain.users import UserType
from saas.service.enterprize import create_enterprize
from saas.service.profile import create_profile

session = create_session()
profile_repository = ProfileRepository(session=session)

try:
    enterprize = profile_repository.retrieve_enterprize(enterprize_subdomain='staging')
except EnterprizeDoesNotExist:
    enterprize = create_enterprize(name='Staging', subdomain='staging', repository=profile_repository)


def create_superadmin():
    try:
        profile = profile_repository.retrieve_by_username(username=configuration.SUPERADMIN_USERNAME)
    except UsernameDoesNotExist:

        profile = create_profile(repository=profile_repository, enterprize=enterprize)
        profile.preregister_username(email_address=configuration.SUPERADMIN_USERNAME)
        profile.user.type = UserType.super_admin
        profile.user.activate()

        profile_repository.save_profile(profile=profile)


def create_admin(username):
    try:
        profile = profile_repository.retrieve_by_username(username=username)
    except UsernameDoesNotExist:

        profile = create_profile(repository=profile_repository, enterprize=enterprize)
        profile.preregister_username(email_address=username)
        profile.user.type = UserType.admin
        profile.user.password = '123456'
        profile.user.activate()

        profile_repository.save_profile(profile=profile)


def create_user(username):
    try:
        profile = profile_repository.retrieve_by_username(username=username)
    except UsernameDoesNotExist:

        profile = create_profile(repository=profile_repository, enterprize=enterprize)
        profile.preregister_username(email_address=username)
        profile.user.type = UserType.user
        profile.user.password = '123456'
        profile.user.activate()

        profile_repository.save_profile(profile=profile)
