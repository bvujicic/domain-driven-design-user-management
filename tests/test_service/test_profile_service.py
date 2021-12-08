import dataclasses
from datetime import date, timedelta
from saas.domain.users import (
    Address,
    Contact,
    CompanyStatus,
    UserAvailability,
    UserMotivation,
    Gender,
    FullName,
    EnterprizeNotes,
    LegalStatus,
)
from saas.domain.users.events import UserInvited
from saas.service.profile import (
    retrieve_profiles,
    update_profile,
    upload_user_photo,
    create_profile,
    invite_user_to_register,
    update_non_public_profile,
)


class TestProfileService:
    address = Address(street='New', zip_code='New', town='New', country='New')
    contact = Contact(address=address, phone_number='New')
    company_status = CompanyStatus(department='New', position='New')
    full_name = FullName(first_name='New', last_name='New')
    enterprize_notes = EnterprizeNotes(
        legal_status=LegalStatus.sick_leave,
        exit_notes='test',
        enter_date=date.today() - timedelta(weeks=250),
        exit_date=date.today(),
    )

    def test_can_create_profile(self, user_repository, enterprize):
        profile = create_profile(repository=user_repository, enterprize=enterprize)

        assert profile.enterprize is enterprize

    def test_can_retrieve_profiles(self, profile, admin_profile, user_repository):
        profiles = retrieve_profiles(admin_username=admin_profile.user.username, repository=user_repository)

        assert profile in profiles
        assert admin_profile in profiles

    def test_can_update_profile(self, user, user_repository):
        update_arguments = {
            'first_name': self.full_name.first_name,
            'last_name': self.full_name.last_name,
            'street': self.contact.address.street,
            'town': self.contact.address.town,
            'zip_code': self.contact.address.zip_code,
            'country': self.contact.address.country,
            'phone_number': self.contact.phone_number,
            'department': self.company_status.department,
            'position': self.company_status.position,
            'gender': Gender.female,
            'birthdate': date.today() - timedelta(weeks=250),
            'skills': [],
            'descriptions': [],
            'availability': UserAvailability.available,
            'motivation': [UserMotivation.job, UserMotivation.mentor],
        }
        profile = update_profile(username=user.username, repository=user_repository, **update_arguments)

        assert profile.full_name == self.full_name
        assert profile.contact == self.contact
        assert profile.company_status == self.company_status
        assert profile.availability == UserAvailability.available
        assert profile.gender == Gender.female
        assert profile.birthdate == date.today() - timedelta(weeks=250)
        assert profile.motivation == [UserMotivation.job, UserMotivation.mentor]

    def test_can_update_non_public_profile(self, profile, user_repository):
        update_arguments = {
            'legal_status': self.enterprize_notes.legal_status,
            'exit_notes': self.enterprize_notes.exit_notes,
            'enter_date': self.enterprize_notes.enter_date,
            'exit_date': self.enterprize_notes.exit_date,
        }
        profile = update_non_public_profile(
            profile_id=profile.reference, repository=user_repository, **update_arguments
        )

        assert profile.enterprize_notes.legal_status == self.enterprize_notes.legal_status
        assert profile.enterprize_notes.exit_notes == self.enterprize_notes.exit_notes
        assert profile.enterprize_notes.enter_date == self.enterprize_notes.enter_date
        assert profile.enterprize_notes.exit_date == self.enterprize_notes.exit_date

    def test_can_update_non_public_profile_partially(self, profile, user_repository, enterprize_notes):
        update_arguments = {
            'legal_status': self.enterprize_notes.legal_status,
            'exit_date': self.enterprize_notes.exit_date,
        }
        profile = update_non_public_profile(
            profile_id=profile.reference, repository=user_repository, **dataclasses.asdict(enterprize_notes)
        )
        profile = update_non_public_profile(
            profile_id=profile.reference, repository=user_repository, **update_arguments
        )
        assert profile.enterprize_notes.legal_status == self.enterprize_notes.legal_status
        assert profile.enterprize_notes.exit_notes == enterprize_notes.exit_notes
        assert profile.enterprize_notes.enter_date == enterprize_notes.enter_date
        assert profile.enterprize_notes.exit_date == self.enterprize_notes.exit_date

    def test_can_upload_photo(self, profile, photo, user_repository):
        photo_url = upload_user_photo(username=profile.user.username, photo=photo, repository=user_repository)

        assert photo_url == str(profile.photo)

    def test_can_invite_user_to_register_user_exists(self, profile, admin_profile, user_repository):
        invite_user_to_register(username=profile.user.username, creator=admin_profile, repository=user_repository)

        assert profile.user.invited is not None
        assert isinstance(profile.event_logs[-1], UserInvited)

    def test_can_invite_user_to_register_user_does_not_exist(self, credentials, admin_profile, user_repository):
        invite_user_to_register(username=credentials.username, creator=admin_profile, repository=user_repository)
