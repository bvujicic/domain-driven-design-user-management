from saas.domain.users import UserCredentials, ProfileAbstractRepository, User
from saas.domain.services import verify_hashed_password
from saas.domain.exceptions import (
    UsernameDoesNotExist,
    UserInactive,
    InvalidPasswordHash,
)
from saas.service.exceptions import InvalidCredentials


def authenticate_credentials(*, credentials: 'UserCredentials', repository: 'ProfileAbstractRepository') -> 'User':
    try:
        profile = repository.retrieve_by_username(username=credentials.username)
    except UsernameDoesNotExist:
        raise InvalidCredentials()

    if not profile.user.is_active:
        raise UserInactive(username=profile.user.username)

    try:
        is_password_verified = verify_hashed_password(
            plain_password=credentials.plain_password, password=profile.user.password
        )
    except InvalidPasswordHash:
        raise InvalidCredentials()

    if not is_password_verified:
        raise InvalidCredentials()

    return profile.user
