import pytest

from saas.domain.exceptions import UsernameExists, UserAlreadyActive, UserInactive
from saas.domain.users import UserCredentials
from saas.domain.users.events import (
    UserPasswordChangeInitiated,
    UsernameChangeInitiated,
    UsernameChanged,
    UserPasswordChanged,
)
from saas.service.authentication import (
    authenticate_credentials,
    decode_access_token,
    initiate_password_change,
    change_user_password,
    decode_password_change_token,
    create_password_change_token,
    create_username_change_token,
    decode_username_change_token,
    create_profile_activation_token,
    decode_profile_activation_token,
    initiate_username_change,
    change_username,
)
from saas.service.exceptions import InvalidCredentials, InvalidToken
from saas.service.registration import register_user, activate_profile


class TestRegistration:
    def test_registration_successful_profile_does_not_exist(self, user_repository, credentials, enterprize, full_name):
        user = register_user(
            credentials=credentials,
            enterprize_subdomain=enterprize.subdomain,
            repository=user_repository,
        )
        assert user.username == credentials.username
        assert user.password != credentials.plain_password

    def test_registration_successful_profile_exists(
        self, preregistered_profile, user_repository, credentials, enterprize
    ):
        user = register_user(
            credentials=credentials,
            enterprize_subdomain=enterprize.subdomain,
            repository=user_repository,
        )
        assert preregistered_profile.user is user
        assert user.username == credentials.username
        assert user.password != credentials.plain_password

    def test_registration_case_insensitive_username_exists(
        self, user_repository, active_profile, credentials, enterprize
    ):
        credentials = UserCredentials(
            username=credentials.username.upper(),
            plain_password='password',
        )
        with pytest.raises(UsernameExists):
            register_user(
                credentials=credentials,
                enterprize_subdomain=enterprize.subdomain,
                repository=user_repository,
            )

    def test_registration_username_exists(self, user_repository, active_profile, credentials, enterprize):
        with pytest.raises(UsernameExists):
            register_user(
                credentials=credentials,
                enterprize_subdomain=enterprize.subdomain,
                repository=user_repository,
            )

    def test_registration_username_exists_not_active(self, user_repository, profile, credentials, enterprize):
        with pytest.raises(UserInactive):
            register_user(
                credentials=credentials,
                enterprize_subdomain=enterprize.subdomain,
                repository=user_repository,
            )


class TestProfileActivation:
    def test_can_create_profile_activation_token(self, profile):
        profile_activation_token = create_profile_activation_token(username=profile.user.username)

        assert profile_activation_token

    def test_can_decode_profile_activation_token(self, profile):
        profile_activation_token = create_profile_activation_token(username=profile.user.username)
        username = decode_profile_activation_token(token=profile_activation_token)

        assert username == profile.user.username

    def test_cannot_decode_profile_activation_token_token(self, access_token):
        with pytest.raises(InvalidToken):
            decode_profile_activation_token(token=access_token)

    def test_activation_successful(self, profile, profile_activation_token, user_repository):
        activate_profile(profile_activation_token=profile_activation_token, repository=user_repository)

        assert profile.user.is_active
        assert profile.user.activated is not None

    def test_activation_user_already_active(self, active_profile_activation_token, user_repository):
        with pytest.raises(UserAlreadyActive):
            activate_profile(profile_activation_token=active_profile_activation_token, repository=user_repository)


class TestAuthentication:
    def test_user_can_authenticate(self, active_user, user_repository, credentials):
        retrieved_user = authenticate_credentials(credentials=credentials, repository=user_repository)
        assert retrieved_user == active_user

    def test_user_can_authenticate_case_insensitive(self, active_user, user_repository, credentials):
        credentials = UserCredentials(
            username=credentials.username.upper(),
            plain_password=credentials.plain_password,
        )

        retrieved_user = authenticate_credentials(credentials=credentials, repository=user_repository)
        assert retrieved_user == active_user

    def test_user_inactive(self, user, user_repository, credentials):
        with pytest.raises(UserInactive):
            authenticate_credentials(credentials=credentials, repository=user_repository)

    def test_user_invalid_credentials(self, user_repository, credentials):
        with pytest.raises(InvalidCredentials):
            authenticate_credentials(credentials=credentials, repository=user_repository)


class TestAccessToken:
    def test_can_decode_access_token(self, user, access_token):
        decoded_username = decode_access_token(access_token=access_token)

        assert decoded_username == user.username

    def test_faulty_access_token(self):
        with pytest.raises(InvalidToken):
            decode_access_token(access_token='invalid_access_token')


class TestChangePassword:
    def test_can_create_password_access_token(self, active_profile):
        password_access_token = create_password_change_token(username=active_profile.user.username)

        assert password_access_token

    def test_can_decode_password_access_token(self, active_profile):
        password_access_token = create_password_change_token(username=active_profile.user.username)
        username = decode_password_change_token(password_change_token=password_access_token)

        assert username == active_profile.user.username

    def test_cannot_decode_password_change_token(self, access_token):
        with pytest.raises(InvalidToken):
            decode_password_change_token(password_change_token=access_token)

    def test_initiate_password_change(self, active_profile, user_repository):
        initiate_password_change(profile=active_profile, repository=user_repository)

        assert isinstance(active_profile.event_logs[-1], UserPasswordChangeInitiated)

    def test_can_change_password(self, active_profile, user_repository):
        new_plain_password = 'new_password'
        old_password = active_profile.user.password
        change_user_password(
            profile=active_profile,
            new_plain_password=new_plain_password,
            repository=user_repository,
        )

        assert old_password != active_profile.user.password
        assert isinstance(active_profile.event_logs[-1], UserPasswordChanged)


class TestChangeUsername:
    def test_can_create_username_change_token(self, active_profile, other_credentials):
        username_change_token = create_username_change_token(
            username=active_profile.user.username, new_username=other_credentials.username
        )

        assert username_change_token

    def test_can_decode_username_change_token(self, active_profile, other_credentials, username_change_token):
        username, new_username = decode_username_change_token(username_change_token=username_change_token)

        assert username == active_profile.user.username
        assert new_username == other_credentials.username

    def test_cannot_decode_username_change_token(self, access_token):
        with pytest.raises(InvalidToken):
            decode_username_change_token(username_change_token=access_token)

    def test_inititate_username_change(self, active_profile, user_repository):
        initiate_username_change(
            profile=active_profile, new_username=f'change_{active_profile.user.username}', repository=user_repository
        )

        assert isinstance(active_profile.event_logs[-1], UsernameChangeInitiated)

    def test_username_already_exists(self, active_profile, other_user, user_repository):
        with pytest.raises(UsernameExists):
            initiate_username_change(
                profile=active_profile, new_username=other_user.username, repository=user_repository
            )

    def test_can_change_username(self, active_profile, other_credentials, user_repository):
        change_username(profile=active_profile, new_username=other_credentials.username, repository=user_repository)

        assert active_profile.user.username == other_credentials.username
        assert isinstance(active_profile.event_logs[-1], UsernameChanged)
