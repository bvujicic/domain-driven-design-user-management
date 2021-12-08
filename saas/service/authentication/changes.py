from saas.domain.exceptions import UsernameExists, UsernameDoesNotExist
from saas.domain.users import ProfileAbstractRepository, Profile
from saas.domain.users.events import (
    UserPasswordChangeInitiated,
    UserPasswordChanged,
    UsernameChangeInitiated,
    UsernameChanged,
)
from saas.service import message_bus
from .security import create_password_change_token, create_username_change_token


def initiate_password_change(profile: 'Profile', repository: 'ProfileAbstractRepository'):
    password_change_token = create_password_change_token(username=profile.user.username)
    event = UserPasswordChangeInitiated(username=profile.user.username, password_change_token=password_change_token)
    profile.event_logs = []
    profile.event_logs.append(event)

    repository.save_profile(profile=profile)

    message_bus.handle(profile.event_logs[-1])


def change_user_password(profile: 'Profile', new_plain_password: str, repository: 'ProfileAbstractRepository') -> None:
    profile.user.password = new_plain_password
    event = UserPasswordChanged(username=profile.user.username)
    profile.event_logs = []
    profile.event_logs.append(event)

    repository.save_profile(profile=profile)

    message_bus.handle(profile.event_logs[-1])


def initiate_username_change(profile: 'Profile', new_username: str, repository: 'ProfileAbstractRepository'):
    try:
        repository.retrieve_by_username(username=new_username)
    except UsernameDoesNotExist:
        profile = repository.retrieve_by_username(username=profile.user.username)
        username_change_token = create_username_change_token(username=profile.user.username, new_username=new_username)
        event = UsernameChangeInitiated(new_username=new_username, username_change_token=username_change_token)
        profile.event_logs = []
        profile.event_logs.append(event)
        repository.save_profile(profile=profile)

        message_bus.handle(profile.event_logs[-1])
    else:
        raise UsernameExists(username=new_username)


def change_username(profile: 'Profile', new_username: str, repository: 'ProfileAbstractRepository'):
    profile.user.username = new_username
    event = UsernameChanged(new_username=new_username)
    profile.event_logs = []
    profile.event_logs.append(event)

    repository.save_profile(profile=profile)

    message_bus.handle(profile.event_logs[-1])
