import dataclasses
import enum
from datetime import date
from typing import Optional

from saas.domain.mixins import ValueObjectUpdateMixin


@enum.unique
class LegalStatus(enum.Enum):
    parental_leave = 'parental_leave'
    educational_leave = 'educational_leave'
    sick_leave = 'sick_leave'
    retirement = 'retirement'
    other = 'other'


@enum.unique
class Gender(enum.Enum):
    female = 'female'
    male = 'male'
    other = 'other'


@enum.unique
class UserType(enum.Enum):
    user = 'user'
    admin = 'admin'
    super_admin = 'super_admin'


@enum.unique
class UserAvailability(enum.Enum):
    available = 'available'
    partial = 'partial'
    booked = 'booked'
    not_interested = 'not_interested'


@enum.unique
class UserMotivation(enum.Enum):
    mentor = 'mentor'
    mentee = 'mentee'
    consulting = 'consulting'
    short_term = 'short_term'
    project = 'project'
    coffee = 'coffee'
    lunch = 'lunch'
    job = 'job'
    training = 'training'


@dataclasses.dataclass(frozen=True)
class UserCredentials(ValueObjectUpdateMixin):
    username: str
    plain_password: Optional[str]


@dataclasses.dataclass(frozen=True)
class FullName(ValueObjectUpdateMixin):
    first_name: str
    last_name: str


@dataclasses.dataclass(frozen=True)
class Address(ValueObjectUpdateMixin):
    street: Optional[str]
    zip_code: Optional[str]
    town: Optional[str]
    country: Optional[str]


@dataclasses.dataclass(frozen=True)
class CompanyStatus(ValueObjectUpdateMixin):
    department: str
    position: str


@dataclasses.dataclass(frozen=True)
class Contact(ValueObjectUpdateMixin):
    address: 'Address'
    phone_number: str


@dataclasses.dataclass(frozen=True)
class EnterprizeNotes(ValueObjectUpdateMixin):
    legal_status: 'LegalStatus'
    exit_notes: str
    enter_date: date
    exit_date: date
