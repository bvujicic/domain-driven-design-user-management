from saas.domain.exceptions import (
    UserAlreadyActive,
    UsernameDoesNotExist,
    UserInactive,
    UsernameExists,
)
from saas.domain.services import create_hashed_password
from saas.domain.users import User, ProfileAbstractRepository, UserCredentials
from saas.service import message_bus
from saas.service.authentication.security import decode_profile_activation_token, create_profile_activation_token
from saas.service.exceptions import InvalidToken, InvalidActivationCode
from saas.service.profile import create_profile


def register_user(
    credentials: 'UserCredentials', enterprize_subdomain: str, repository: 'ProfileAbstractRepository'
) -> 'User':
    enterprize = repository.retrieve_enterprize(enterprize_subdomain=enterprize_subdomain)

    try:
        profile = repository.retrieve_by_username(username=credentials.username)
    except UsernameDoesNotExist:
        profile = _create_profile_and_register_user(
            credentials=credentials, enterprize=enterprize, repository=repository
        )
    else:
        if profile.user.is_active:
            raise UsernameExists(username=credentials.username)
        else:
            if profile.user.password is None:
                profile.user.password = create_hashed_password(plain_password=credentials.plain_password)
            else:
                raise UserInactive(username=credentials.username)

    token = create_profile_activation_token(username=credentials.username)
    profile.publish_profile_registered_event(profile_activation_token=token)

    repository.save_profile(profile=profile)

    message_bus.handle(profile.event_logs[-1])

    return profile.user


def _create_profile_and_register_user(credentials, enterprize, repository):
    profile = create_profile(repository=repository, enterprize=enterprize)
    profile.register_user(credentials=credentials)

    return profile


def activate_profile(profile_activation_token: str, repository: ProfileAbstractRepository) -> User:
    try:
        username = decode_profile_activation_token(token=profile_activation_token)
    except InvalidToken:
        raise InvalidActivationCode(activation_code=profile_activation_token)

    profile = repository.retrieve_by_username(username=username)

    if profile.user.is_active:
        raise UserAlreadyActive(username=profile.user.username)

    profile.activate()
    repository.save_profile(profile=profile)

    message_bus.handle(profile.event_logs[-1])

    return profile.user
