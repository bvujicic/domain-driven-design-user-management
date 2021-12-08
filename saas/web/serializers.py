import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, EmailStr, validator

from saas.domain.users import UserAvailability, UserMotivation, LegalStatus, Gender


class BaseModelWithValidator(BaseModel):
    @validator('*')
    def disallow_empty_strings(cls, value):
        if isinstance(value, str) and not value:
            return None

        return value


class ProfileSerializer(BaseModelWithValidator):
    reference: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[Gender]
    birthdate: Optional[datetime.date]
    role: Optional[str]
    activated: Optional[bool]
    invited: Optional[bool]
    street: Optional[str]
    town: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]
    phone_number: Optional[str]
    position: Optional[str]
    department: Optional[str]
    photo_url: Optional[str]
    availability: Optional[UserAvailability]
    motivation: list[UserMotivation]
    skills: list[dict]
    descriptions: list[Any]


class AdminProfileSerializer(ProfileSerializer):

    legal_status: Optional[LegalStatus]
    exit_notes: Optional[str]
    enter_date: Optional[datetime.date]
    exit_date: Optional[datetime.date]


class RegisterUserRequest(BaseModelWithValidator):
    enterprize_subdomain: str
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterUserResponse(BaseModelWithValidator):
    email: EmailStr


class ActicateUserRequest(BaseModelWithValidator):
    activation_code: str


class ActivateUserResponse(BaseModelWithValidator):
    email: EmailStr
    is_active: bool


class LoginResponse(BaseModelWithValidator):
    access_token: str
    token_type: str = 'bearer'


class CreateEnterprizeRequest(BaseModelWithValidator):
    name: str
    subdomain: str


class CreateEnterprizeResponse(BaseModelWithValidator):
    subdomain: str


class RetrieveProfileResponse(ProfileSerializer):
    pass


class RetrieveAdminProfileResponse(AdminProfileSerializer):
    pass


class UpdateProfileRequest(BaseModelWithValidator):
    first_name: Optional[str]
    last_name: Optional[str]
    street: Optional[str]
    town: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]
    phone_number: Optional[str]
    position: Optional[str]
    department: Optional[str]
    skills: Optional[list[dict]]
    descriptions: Optional[list[Any]]
    gender: Optional[Gender]
    birthdate: Optional[datetime.date]
    availability: Optional[UserAvailability]
    motivation: Optional[list[UserMotivation]]


class UpdateProfileResponse(UpdateProfileRequest):
    class Config:
        orm_mode = True


class InviteUserRequest(BaseModelWithValidator):
    email: EmailStr


class InviteUserResponse(InviteUserRequest):
    pass


class UploadPhotoResponse(BaseModelWithValidator):
    photo_url: str


class CreatePostRequest(BaseModelWithValidator):
    title: str
    body: str


class CreatePostResponse(BaseModelWithValidator):
    author: str
    created: datetime.datetime


class EventSerializer(BaseModelWithValidator):
    reference: str
    title: str
    body: str
    location: str
    starts_at: datetime.datetime
    ends_at: datetime.datetime
    created: datetime.datetime

    class Config:
        orm_mode = True


class CreateEventRequest(BaseModelWithValidator):
    title: str
    body: str
    location: str
    starts_at: datetime.datetime
    ends_at: datetime.datetime


class CreateEventResponse(BaseModelWithValidator):
    organizer: str
    created: datetime.datetime


class ListEventsResponse(BaseModelWithValidator):
    events: list[EventSerializer]


class ListProfilesResponse(BaseModelWithValidator):
    profiles: list[AdminProfileSerializer]


class Post(BaseModelWithValidator):
    reference: str
    author: str
    title: str
    body: str
    created: datetime.datetime


class ListPostsResponse(BaseModelWithValidator):
    posts: Optional[list[Post]]


class RetrievePostResponse(Post):
    pass


class UserInvitation(BaseModelWithValidator):
    email: EmailStr
    registered: bool
    activated: bool


class UserInvitationResponse(BaseModelWithValidator):
    email: EmailStr
    registered: bool
    activated: bool
    invited: bool


class ListUserInvitationsResponse(BaseModelWithValidator):
    invitations: Optional[list[UserInvitationResponse]]


class AdminDashboardResponse(BaseModelWithValidator):
    active_registrations: int
    total_registrations: int
    accepted_invitations: int
    total_invitations: int


class CreateQuestionRequest(BaseModelWithValidator):
    title: str
    body: str
    tags: Optional[set[str]] = set()


class CreateQuestionResponse(BaseModelWithValidator):
    id: str
    author: str
    tags: Optional[set[str]] = set()
    created: datetime.datetime


class CreateAnswerRequest(BaseModelWithValidator):
    body: str


class CreateAnswerResponse(BaseModelWithValidator):
    id: str
    question_id: str
    author: str
    created: datetime.datetime


class Answer(BaseModelWithValidator):
    id: str
    body: str
    author: str
    created: datetime.datetime


class Question(BaseModelWithValidator):
    id: str
    title: str
    body: str
    author: str
    tags: Optional[set[str]] = set()
    created: datetime.datetime
    answers: list[Answer]


class ListQuestionsResponse(BaseModelWithValidator):
    questions: list[Question]


class RetrieveQuestionResponse(Question):
    pass


class ChangePasswordRequest(BaseModelWithValidator):
    password_change_token: str
    new_password: str


class InitiateChangePasswordRequest(BaseModelWithValidator):
    username: EmailStr


class ChangePasswordResponse(LoginResponse):
    pass


class InitiateChangeUsernameRequest(BaseModelWithValidator):
    new_username: EmailStr


class ChangeUsernameRequest(BaseModelWithValidator):
    username_change_token: str


class ChangeUsernameResponse(LoginResponse):
    new_username: EmailStr


class AdminUpdateProfileRequest(BaseModelWithValidator):
    legal_status: Optional[LegalStatus]
    exit_notes: Optional[str]
    enter_date: Optional[datetime.date]
    exit_date: Optional[datetime.date]


class AdminUpdateProfileResponse(AdminUpdateProfileRequest):
    username: EmailStr

    class Config:
        orm_mode = True
