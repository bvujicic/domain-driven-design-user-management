from typing import Any, Optional

from saas.domain.exceptions import UsernameDoesNotExist
from saas.domain.users import (
    ProfileAbstractRepository,
    FullName,
    Profile,
    Enterprize,
)
from saas.service import message_bus


def create_profile(
    repository: 'ProfileAbstractRepository', enterprize: 'Enterprize', full_name: Optional['FullName'] = None
) -> 'Profile':
    profile = Profile(enterprize=enterprize, full_name=full_name)

    repository.save_profile(profile=profile)

    return profile


def retrieve_profiles(admin_username: str, repository: ProfileAbstractRepository) -> list:
    profiles = repository.retrieve_profiles_for_admin(admin_username=admin_username)
    return profiles


def update_profile(username: str, repository: ProfileAbstractRepository, **kwargs) -> 'Profile':
    profile = repository.retrieve_by_username(username=username)

    new_address = profile.address.create_with_changed_atrributes(**kwargs)
    new_contact = profile.contact.create_with_changed_atrributes(address=new_address, **kwargs)
    new_full_name = profile.full_name.create_with_changed_atrributes(**kwargs)
    new_company_status = profile.company_status.create_with_changed_atrributes(**kwargs)

    profile.event_logs = []
    profile.full_name = new_full_name
    profile.contact = new_contact
    profile.company_status = new_company_status
    profile.gender = kwargs.get('gender') or profile.gender
    profile.birthdate = kwargs.get('birthdate') or profile.birthdate
    profile.skills = kwargs.get('skills') or profile.skills
    profile.descriptions = kwargs.get('descriptions') or profile.descriptions
    profile.availability = kwargs.get('availability') or profile.availability
    profile.motivation = kwargs.get('motivation') or profile.motivation

    repository.save_profile(profile=profile)

    return profile


def upload_user_photo(username: str, photo: Any, repository: ProfileAbstractRepository) -> str:
    profile = repository.retrieve_by_username(username=username)

    photo_url = repository.upload_photo(profile=profile, photo=photo)

    return photo_url


def delete_user_photo(username: str, repository: ProfileAbstractRepository) -> None:
    profile = repository.retrieve_by_username(username=username)

    repository.delete_photo(profile=profile)


def invite_user_to_register(username: str, creator: Profile, repository: ProfileAbstractRepository) -> 'Profile':
    try:
        profile = repository.retrieve_by_username(username=username)
    except UsernameDoesNotExist:
        profile = create_profile(repository=repository, enterprize=creator.enterprize)
        profile.preregister_username(email_address=username)

    profile.invite_to_register(creator=creator)

    repository.save_profile(profile=profile)

    message_bus.handle(profile.event_logs[-1])

    return profile


def update_non_public_profile(profile_id: str, repository: ProfileAbstractRepository, **kwargs) -> Profile:
    profile = repository.retrieve_profile(reference=profile_id)

    new_enterprize_notes = profile.enterprize_notes.create_with_changed_atrributes(**kwargs)

    profile.enterprize_notes = new_enterprize_notes

    repository.save_profile(profile=profile)

    return profile
