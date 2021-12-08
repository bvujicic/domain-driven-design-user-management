import pytest

from saas.domain.exceptions import UserAlreadyExists
from saas.domain.services import verify_hashed_password
from saas.domain.users import Profile
from saas.domain.users.events import UserActivated, UserInvited


class TestProfile:
    email_address = 'test@example.com'

    def test_can_create_blank_profile(self, enterprize):
        profile = Profile(enterprize=enterprize)

        assert profile.enterprize is enterprize

    def test_can_create_profile(self, enterprize, full_name):
        profile = Profile(enterprize=enterprize, full_name=full_name)

        assert profile.user is None
        assert profile.enterprize is enterprize

    def test_profiles_not_equal(self, enterprize):
        profile = Profile(enterprize=enterprize)
        other_profile = Profile(enterprize=enterprize)

        assert profile != other_profile

    def test_profiles_equal_with_equal_usernames(self, enterprize):
        profile = Profile(enterprize=enterprize)
        profile.preregister_username(email_address=self.email_address)

        other_profile = Profile(enterprize=enterprize)
        other_profile.preregister_username(email_address=self.email_address)

        assert profile == other_profile

    def test_can_preregister_username(self, enterprize, full_name):
        profile = Profile(enterprize=enterprize, full_name=full_name)
        profile.preregister_username(email_address=self.email_address)

        assert profile.username == self.email_address
        assert profile.user.password is None
        assert profile.enterprize is enterprize

    def test_cannot_preregister_username_already_exists(self, enterprize, full_name):
        with pytest.raises(UserAlreadyExists):
            profile = Profile(enterprize=enterprize, full_name=full_name)
            profile.preregister_username(email_address=self.email_address)
            profile.preregister_username(email_address=self.email_address)

    def test_can_register_new_username(self, enterprize, full_name, credentials):
        profile = Profile(enterprize=enterprize, full_name=full_name)
        profile.register_user(credentials=credentials)

        assert profile.user.username == credentials.username
        assert profile.user.password != credentials.plain_password
        # assert isinstance(profile.event_logs.pop(), UserRegistered)

    def test_cannot_register_username_already_exists(self, enterprize, full_name, credentials):
        with pytest.raises(UserAlreadyExists):
            profile = Profile(enterprize=enterprize, full_name=full_name)
            profile.register_user(credentials=credentials)
            profile.register_user(credentials=credentials)

    def test_can_set_password(self, preregistered_profile, credentials):
        preregistered_profile.user.password = credentials.plain_password

        assert verify_hashed_password(
            plain_password=credentials.plain_password, password=preregistered_profile.user.password
        )

    def test_user_can_activate(self, profile):
        profile.activate()

        assert profile.user.is_active
        assert profile.user.activated is not None
        assert isinstance(profile.event_logs[-1], UserActivated)

    def test_invite_user_to_register(self, profile, admin_profile):
        profile.invite_to_register(creator=admin_profile)

        assert profile.user.invited is not None
        assert isinstance(profile.event_logs[-1], UserInvited)
