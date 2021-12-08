import dataclasses
import enum

from saas.domain.base import DomainEvent


class UserEvents(enum.Enum):
    UserRegistered = enum.auto()
    UserActivated = enum.auto()
    UserInvited = enum.auto()
    UserPasswordChangeInitiated = enum.auto()
    UserPasswordChanged = enum.auto()
    UsernameChangeInitiated = enum.auto()
    UsernameChanged = enum.auto()


@dataclasses.dataclass(frozen=True)
class UserRegistered(DomainEvent):
    name: str = dataclasses.field(default=UserEvents.UserRegistered.name, init=False)
    username: str
    activation_code: str


@dataclasses.dataclass(frozen=True)
class UserActivated(DomainEvent):
    name: str = dataclasses.field(default=UserEvents.UserActivated.name, init=False)
    username: str


@dataclasses.dataclass(frozen=True)
class UserInvited(DomainEvent):
    name: str = dataclasses.field(default=UserEvents.UserInvited.name, init=False)
    invited_email_address: str
    admin_username: str
    admin_first_name: str
    admin_last_name: str
    admin_company: str


@dataclasses.dataclass(frozen=True)
class UserPasswordChangeInitiated(DomainEvent):
    name: str = dataclasses.field(default=UserEvents.UserPasswordChangeInitiated.name, init=False)
    username: str
    password_change_token: str


@dataclasses.dataclass(frozen=True)
class UserPasswordChanged(DomainEvent):
    name: str = dataclasses.field(default=UserEvents.UserPasswordChanged.name, init=False)
    username: str


@dataclasses.dataclass(frozen=True)
class UsernameChangeInitiated(DomainEvent):
    name: str = dataclasses.field(default=UserEvents.UsernameChangeInitiated.name, init=False)
    new_username: str
    username_change_token: str


@dataclasses.dataclass(frozen=True)
class UsernameChanged(DomainEvent):
    name: str = dataclasses.field(default=UserEvents.UsernameChanged.name, init=False)
    new_username: str
