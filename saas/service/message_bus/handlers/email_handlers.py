from saas.database.session import DatabaseSession
from saas.domain.users.events import UserRegistered, UserInvited, UserPasswordChangeInitiated, UsernameChangeInitiated
from saas.service.email.customer_io import CustomerIOEmailSender


def send_activation_code_email(event: 'UserRegistered'):
    from saas.database.models import ProfileRepository

    repository = ProfileRepository(session=DatabaseSession())
    profile = repository.retrieve_by_username(username=event.username)

    email_sender = CustomerIOEmailSender(event=event, profile=profile)
    email_sender.create_receiver()
    email_sender.create_email_message()
    email_sender.send_email()


def send_invitation_email(event: 'UserInvited'):
    from saas.database.models import ProfileRepository

    repository = ProfileRepository(session=DatabaseSession())
    profile = repository.retrieve_by_username(username=event.invited_email_address)

    email_sender = CustomerIOEmailSender(event=event, profile=profile)
    email_sender.create_receiver(email_address=event.invited_email_address)
    email_sender.create_email_message()
    email_sender.send_email()


def send_initiate_password_change_email(event: 'UserPasswordChangeInitiated'):
    from saas.database.models import ProfileRepository

    repository = ProfileRepository(session=DatabaseSession())
    profile = repository.retrieve_by_username(username=event.username)

    email_sender = CustomerIOEmailSender(event=event, profile=profile)
    email_sender.create_receiver()
    email_sender.create_email_message()
    email_sender.send_email()


def send_initiate_username_change_email(event: 'UsernameChangeInitiated'):
    # from saas.database.models import ProfileRepository
    #
    # repository = ProfileRepository(session=DatabaseSession())
    # profile = repository.retrieve_by_username(username=event.new_username)

    email_sender = CustomerIOEmailSender(event=event)
    email_sender.create_receiver(email_address=event.new_username)
    email_sender.create_email_message()
    email_sender.send_email()
