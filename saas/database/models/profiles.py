import dataclasses
from typing import Any

import sqlalchemy
import sqlalchemy.exc
from google.cloud import storage
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import exc
from sqlalchemy.orm import joinedload

from saas.core.config import configuration
from saas.database.metadata import metadata
from saas.database.models import SystemEvent
from saas.domain.exceptions import (
    UsernameDoesNotExist,
    UserDoesNotExist,
    EnterprizeDoesNotExist,
    EnterprizeExists,
)
from saas.domain.users import (
    User,
    ProfileAbstractRepository,
    Enterprize,
    UserType,
    UserAvailability,
    Profile,
    Gender,
    LegalStatus,
)
from .enterprizes import enterprizes

profiles = sqlalchemy.Table(
    'profiles',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('reference', sqlalchemy.String(36), unique=True, index=True, nullable=False),
    sqlalchemy.Column('created', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column('first_name', sqlalchemy.String),
    sqlalchemy.Column('last_name', sqlalchemy.String),
    sqlalchemy.Column('birthdate', sqlalchemy.Date),
    sqlalchemy.Column('gender', sqlalchemy.Enum(Gender, native_enum=False, validate_strings=True)),
    sqlalchemy.Column('street', sqlalchemy.String),
    sqlalchemy.Column('town', sqlalchemy.String),
    sqlalchemy.Column('zip_code', sqlalchemy.String),
    sqlalchemy.Column('country', sqlalchemy.String),
    sqlalchemy.Column('phone_number', sqlalchemy.String),
    sqlalchemy.Column('department', sqlalchemy.String),
    sqlalchemy.Column('position', sqlalchemy.String),
    sqlalchemy.Column('photo_url', sqlalchemy.String),
    sqlalchemy.Column('skills', JSONB, server_default='[]'),
    sqlalchemy.Column('descriptions', JSONB, server_default='[]'),
    sqlalchemy.Column('motivation', JSONB, server_default='[]'),
    sqlalchemy.Column(
        'availability',
        sqlalchemy.Enum(UserAvailability, native_enum=False, validate_strings=True),
    ),
    sqlalchemy.Column('legal_status', sqlalchemy.Enum(LegalStatus, native_enum=False, validate_strings=True)),
    sqlalchemy.Column('exit_notes', sqlalchemy.String),
    sqlalchemy.Column('enter_date', sqlalchemy.Date),
    sqlalchemy.Column('exit_date', sqlalchemy.Date),
    sqlalchemy.Column(
        'enterprize_id',
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey(enterprizes.c.id),
        index=True,
        nullable=False,
    ),
)


users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('reference', sqlalchemy.String(36), unique=True, index=True, nullable=False),
    sqlalchemy.Column('created', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column('username', sqlalchemy.String, unique=True),
    sqlalchemy.Column('password', sqlalchemy.String, unique=True),
    sqlalchemy.Column('is_active', sqlalchemy.Boolean, default=False),
    sqlalchemy.Column('activated', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column('invited', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column(
        'type',
        sqlalchemy.Enum(UserType, native_enum=False, validate_strings=True),
        nullable=False,
    ),
    sqlalchemy.Column(
        'profile_id', sqlalchemy.Integer, sqlalchemy.ForeignKey(profiles.c.id), index=True, nullable=False, unique=True
    ),
)


class ProfileRepository(ProfileAbstractRepository):
    def __init__(self, session):
        self.session = session

    def save_profile(self, profile: 'Profile'):
        if getattr(profile, 'event_logs', None) is not None:
            try:
                event = profile.event_logs[-1]
            except IndexError:
                pass
            else:
                event_log = SystemEvent(stream_reference=profile.reference, payload=dataclasses.asdict(event))
                self.session.add(event_log)

        self.session.add(profile)
        self.session.commit()

    def upload_photo(self, profile: Profile, photo: Any):
        client = storage.Client()
        bucket = client.bucket(bucket_name=configuration.GOOGLE_CLOUD_STORAGE_BUCKET_NAME)
        blob = storage.Blob(name=profile.reference, bucket=bucket)
        blob.upload_from_file(file_obj=photo.file, content_type=photo.content_type)
        blob.make_public()

        profile.photo_url = blob.public_url

        self.session.add(profile)
        self.session.commit()

        return profile.photo_url

    def delete_photo(self, profile: Profile):
        client = storage.Client()
        bucket = client.bucket(bucket_name=configuration.GOOGLE_CLOUD_STORAGE_BUCKET_NAME)

        blob = bucket.blob(blob_name=profile.reference)
        blob.delete()

        profile.photo_url = None

        self.session.add(profile)
        self.session.commit()

    def create_enterprize(self, enterprize: Enterprize):
        try:
            self.session.add(enterprize)
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            raise EnterprizeExists(subdomain=enterprize.subdomain)

    def retrieve_profile(self, reference: str) -> Profile:
        try:
            return self.session.query(Profile).filter_by(reference=reference).one()
        except exc.NoResultFound:
            raise UserDoesNotExist(reference=reference)

    def retrieve_profiles_for_admin(self, admin_username: str) -> list[Profile]:
        admin = self.retrieve_by_username(username=admin_username)
        return (
            self.session.query(Profile)
            .join(User)
            .options(joinedload(Profile.user))
            .filter(Profile.enterprize == admin.enterprize, User.type == UserType.user.value, User.is_active)
            .all()
        )

    def retrieve_invited_profiles_for_admin(self, admin_username: str) -> list[Profile]:
        admin = self.retrieve_by_username(username=admin_username)
        return (
            self.session.query(Profile)
            .join(User)
            .options(joinedload(Profile.user))
            .filter(Profile.enterprize == admin.enterprize, User.invited.isnot(None))  # type: ignore
            .all()
        )

    def retrieve_by_username(self, username: str) -> 'Profile':
        try:
            return self.session.query(Profile).join(User).filter(func.lower(User.username) == username.lower()).one()
        except exc.NoResultFound:
            raise UsernameDoesNotExist(username=username)
        except exc.MultipleResultsFound:
            assert False, f'Multiple users found for {username}.'

    def retrieve_by_username_allowed_to_register(self, username: str) -> Profile:
        pass

    def retrieve_enterprize(self, enterprize_subdomain: str) -> Enterprize:
        try:
            return self.session.query(Enterprize).filter_by(subdomain=enterprize_subdomain).one()
        except exc.NoResultFound:
            raise EnterprizeDoesNotExist(subdomain=enterprize_subdomain)

    # def list_users(self) -> list[User]:
    #     return list(self.session.query(User).all())

    def retrieve_dashboard_statistics(self, admin_username: str) -> dict[str, int]:
        admin = self.retrieve_by_username(username=admin_username)

        total_registrations = (
            self.session.query(Profile)
            .join(User)
            .filter(Profile.enterprize == admin.enterprize, User.password is not None)  # type: ignore
            .count()
        )
        active_registrations = (
            self.session.query(Profile)
            .join(User)
            .filter(Profile.enterprize == admin.enterprize, User.activated.isnot(None), User.is_active)  # type: ignore
            .count()
        )
        total_invitations = (
            self.session.query(Profile)
            .join(User)
            .filter(Profile.enterprize == admin.enterprize, User.invited.isnot(None))  # type: ignore
            .count()
        )
        accepted_invitations = (
            self.session.query(Profile)
            .join(User)
            .filter(User.invited.isnot(None), User.activated.isnot(None), User.is_active)  # type: ignore
            .count()
        )

        return {
            'total_registrations': total_registrations,
            'active_registrations': active_registrations,
            'total_invitations': total_invitations,
            'accepted_invitations': accepted_invitations,
        }
