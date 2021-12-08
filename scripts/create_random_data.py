from faker import Faker

from saas.core.config import configuration
from saas.database.models import ProfileRepository, PostRepository
from saas.database.session import create_session
from saas.domain.posts import PostContent
from saas.domain.users import FullName, UserCredentials, Contact, Address, UserAvailability, Gender, LegalStatus
from saas.service.post import create_post
from saas.service.profile import create_profile

fake = Faker(locale='de_at')
Faker.seed()

gender = [element.value for element in list(Gender)]
availability = [element.value for element in list(UserAvailability)]
legal_status = [element.value for element in list(LegalStatus)]

session = create_session()
profile_repository = ProfileRepository(session=session)
post_repository = PostRepository(session=session)
enterprize = profile_repository.retrieve_enterprize(enterprize_subdomain='staging')
admin = profile_repository.retrieve_by_username(username=configuration.SUPERADMIN_USERNAME)


def random_profiles():
    full_name = FullName(first_name=fake.first_name(), last_name=fake.last_name())
    credentials = UserCredentials(username=fake.company_email(), plain_password=None)
    address = Address(street=fake.street_address(), zip_code=fake.postcode(), town=fake.city(), country='AT')
    phone_number = fake.phone_number()
    contact = Contact(address=address, phone_number=phone_number)

    profile = create_profile(repository=profile_repository, enterprize=enterprize, full_name=full_name)
    profile.register_user(credentials=credentials)
    profile.activate()

    profile.gender = fake.words(1, gender, True)[0]
    profile.availability = fake.words(1, availability, True)[0]
    profile.legal_status = fake.words(1, legal_status, True)[0]
    profile.contact = contact
    profile.birthdate = fake.date_of_birth(minimum_age=30, maximum_age=67)
    profile.position = fake.job()

    profile_repository.save_profile(profile=profile)


def random_posts():
    post_content = PostContent(title=fake.sentence(6), body=fake.paragraph(20))
    create_post(author=admin, content=post_content, repository=post_repository)


if __name__ == '__main__':
    for i in range(300):
        random_profiles()

    # for i in range(15):
    #     random_posts()
