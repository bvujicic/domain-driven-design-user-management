import abc
from typing import Any

from .entities import Enterprize, Profile


class ProfileAbstractRepository(abc.ABC):
    @abc.abstractmethod
    def save_profile(self, profile: 'Profile'):
        raise NotImplementedError

    @abc.abstractmethod
    def upload_photo(self, profile: Profile, photo: Any):
        raise NotImplementedError

    @abc.abstractmethod
    def delete_photo(self, profile: Profile):
        raise NotImplementedError

    @abc.abstractmethod
    def create_enterprize(self, enterprize: Enterprize):
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_profile(self, reference: str) -> Profile:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_profiles_for_admin(self, admin_username: str) -> list[Profile]:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_by_username(self, username: str) -> Profile:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_by_username_allowed_to_register(self, username: str) -> Profile:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_enterprize(self, enterprize_subdomain: str) -> Enterprize:
        raise NotImplementedError

    # @abc.abstractmethod
    # def list_users(self) -> list[User]:
    #     raise NotImplementedError

    # @abc.abstractmethod
    # def save_user_invitation(self, invitation: UserInvitation):
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # def retrieve_user_invitation(self, email_address: str) -> UserInvitation:
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # def list_invitations_for_admin(self, admin_username: str) -> list[UserInvitation]:
    #     raise NotImplementedError

    # @abc.abstractmethod
    # def list_invitations_with_users_for_admin(self, admin_username: str) -> list[Any]:
    #     raise NotImplementedError

    @abc.abstractmethod
    def retrieve_dashboard_statistics(self, admin_username: str) -> dict[str, int]:
        raise NotImplementedError
