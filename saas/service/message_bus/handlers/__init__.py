from saas.domain.users.events import (
    UserRegistered,
    UserActivated,
    UserInvited,
    UserPasswordChangeInitiated,
    UserPasswordChanged,
    UsernameChangeInitiated,
    UsernameChanged,
)
from .email_handlers import (
    send_activation_code_email,
    send_invitation_email,
    send_initiate_password_change_email,
    send_initiate_username_change_email,
)


HANDLERS: dict = {
    UserRegistered: {send_activation_code_email},
    UserActivated: {},
    UserInvited: {send_invitation_email},
    UserPasswordChangeInitiated: {send_initiate_password_change_email},
    UserPasswordChanged: {},
    UsernameChangeInitiated: {send_initiate_username_change_email},
    UsernameChanged: {},
}
