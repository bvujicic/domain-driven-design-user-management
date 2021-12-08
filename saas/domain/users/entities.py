from datetime import date, datetime, timezone
from typing import Any, Optional

from saas.domain.base import DomainEntity
from saas.domain.exceptions import UserAlreadyExists
from saas.domain.services import create_hashed_password
from .events import UserRegistered, UserActivated, UserInvited
from .value_objects import (
    UserCredentials,
    FullName,
    Contact,
    CompanyStatus,
    Address,
    UserType,
    UserAvailability,
    UserMotivation,
    Gender,
    EnterprizeNotes,
)


class Enterprize(DomainEntity):
    def __init__(self, name: str, subdomain: str):
        self.name = name
        self.subdomain = subdomain

        super().__init__()

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name}, subdomain={self.subdomain}, reference={self.reference})'

    def __eq__(self, other):
        return self.reference == other.reference

    def __hash__(self):
        return hash(self.reference)


class Profile(DomainEntity):
    def __init__(self, enterprize: 'Enterprize', full_name: Optional['FullName'] = None):
        self.enterprize = enterprize
        self.full_name = full_name
        self.birthdate: Optional[date] = None
        self.gender: Optional[Gender] = None
        self.user: Optional[User] = None

        self.photo = bytes()
        self.photo_url = None
        self.availability: Optional[UserAvailability] = None
        self.motivation: list[UserMotivation] = list()
        self.skills: list[dict] = list()
        self.descriptions: list[Any] = list()

        self.contact: Optional[Contact] = None
        self.company_status: Optional[CompanyStatus] = None

        self.enterprize_notes: Optional[EnterprizeNotes] = None

        super().__init__()

    def __repr__(self):
        return f'{self.__class__.__name__}(user={self.user}, reference={self.reference})'

    def __eq__(self, other):
        if self.user is None or other.user is None:
            return False

        return self.user.username == other.user.username

    def __hash__(self):
        return hash(self.reference)

    def preregister_username(self, email_address: str):
        if self.user is not None:
            raise UserAlreadyExists(profile_reference=self.reference)

        credentials = UserCredentials(username=email_address, plain_password=None)
        self.user = User(credentials=credentials)

    def register_user(self, credentials: 'UserCredentials'):
        if self.user is None:
            self.user = User(credentials=credentials)
        else:
            raise UserAlreadyExists(profile_reference=self.reference)

    def activate(self):
        self.user.activate()
        self._publish_user_activated_event()

    def invite_to_register(self, creator: 'Profile'):
        self.user.invite()
        self._publish_user_invited_event(creator=creator)

    def _publish_user_invited_event(self, creator: 'Profile'):
        event = UserInvited(
            invited_email_address=self.user.username,
            admin_username=creator.user.username,
            admin_first_name=creator.first_name,
            admin_last_name=creator.last_name,
            admin_company=creator.enterprize.name,
        )
        self.event_logs = list()
        self.event_logs.append(event)

    def publish_profile_registered_event(self, profile_activation_token: str):
        event = UserRegistered(username=self.user.username, activation_code=profile_activation_token)
        self.event_logs = list()
        self.event_logs.append(event)

    def _publish_user_activated_event(self):
        event = UserActivated(username=self.user.username)
        self.event_logs = list()
        self.event_logs.append(event)

    @property
    def username(self):
        return self.user.username if self.user is not None else None

    @property
    def full_name(self):
        return FullName(first_name=self.first_name, last_name=self.last_name)

    @full_name.setter
    def full_name(self, full_name: FullName):
        self.first_name = full_name.first_name if full_name is not None else None
        self.last_name = full_name.last_name if full_name is not None else None

    @property
    def address(self):
        return Address(street=self.street, town=self.town, zip_code=self.zip_code, country=self.country)

    @property
    def contact(self):
        return Contact(
            address=self.address,
            phone_number=self.phone_number,
        )

    @contact.setter
    def contact(self, contact: Contact):
        self.street = contact.address.street if contact is not None else None
        self.town = contact.address.town if contact is not None else None
        self.zip_code = contact.address.zip_code if contact is not None else None
        self.country = contact.address.country if contact is not None else None
        self.phone_number = contact.phone_number if contact is not None else None

    @property
    def company_status(self):
        return CompanyStatus(position=self.position, department=self.department)

    @company_status.setter
    def company_status(self, company_status: CompanyStatus):
        self.position = company_status.position if company_status is not None else None
        self.department = company_status.department if company_status is not None else None

    @property
    def enterprize_notes(self):
        return EnterprizeNotes(
            legal_status=self.legal_status,
            exit_notes=self.exit_notes,
            enter_date=self.enter_date,
            exit_date=self.exit_date,
        )

    @enterprize_notes.setter
    def enterprize_notes(self, enterprize_notes: EnterprizeNotes):
        self.legal_status = enterprize_notes.legal_status if enterprize_notes is not None else None
        self.exit_notes = enterprize_notes.exit_notes if enterprize_notes is not None else None
        self.enter_date = enterprize_notes.enter_date if enterprize_notes is not None else None
        self.exit_date = enterprize_notes.exit_date if enterprize_notes is not None else None


class User(DomainEntity):
    def __init__(self, credentials: UserCredentials, type: UserType = UserType.user):
        self.type = type
        self.username = credentials.username.lower()

        self.is_active = False
        self.activated: Optional[datetime] = None
        self.invited: Optional[datetime] = None

        self.password = credentials.plain_password

        super().__init__()

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(username={self.username}, reference={self.reference}, active={self.is_active})'
        )

    def __eq__(self, other):
        return self.username == other.username

    def __hash__(self):
        return hash(self.username)

    def invite(self):
        self.invited = datetime.now(tz=timezone.utc)

    def activate(self):
        self.is_active = True
        self.activated = datetime.now(tz=timezone.utc)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str):
        if value is not None:
            self._password = create_hashed_password(plain_password=value)
        else:
            self._password = None

    @property
    def is_admin(self):
        return self.type == UserType.admin

    @property
    def is_super_admin(self):
        return self.type == UserType.super_admin
