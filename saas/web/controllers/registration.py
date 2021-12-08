from fastapi import APIRouter, status, Depends, HTTPException

from saas.database.models import ProfileRepository
from saas.domain.exceptions import UserAlreadyActive, EnterprizeDoesNotExist, UserInactive, UsernameExists
from saas.domain.users import UserCredentials
from saas.service.exceptions import InvalidActivationCode
from saas.service.registration import register_user, activate_profile
from saas.web.serializers import (
    RegisterUserRequest,
    RegisterUserResponse,
    ActivateUserResponse,
    ActicateUserRequest,
)
from saas.web.session import profile_database

registration_router = APIRouter()


@registration_router.post(
    path='/users/actions/registration',
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterUserResponse,
    name='Register new user',
    tags=['registration'],
)
def register_user_controller(
    request: 'RegisterUserRequest',
    repository: 'ProfileRepository' = Depends(profile_database),
):
    credentials = UserCredentials(username=request.email, plain_password=request.password)
    # full_name = FullName(first_name=request.first_name, last_name=request.last_name)
    enterprize_subdomain = request.enterprize_subdomain

    try:
        user = register_user(
            credentials=credentials,
            enterprize_subdomain=enterprize_subdomain,
            repository=repository,
        )
    except (UsernameExists, EnterprizeDoesNotExist, UserInactive) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        )

    return RegisterUserResponse(email=user.username)


@registration_router.post(
    path='/users/actions/activation',
    status_code=status.HTTP_200_OK,
    response_model=ActivateUserResponse,
    name='Activate registered user',
    tags=['registration'],
)
def activate_user_controller(
    request: 'ActicateUserRequest', repository: 'ProfileRepository' = Depends(profile_database)
):
    try:
        user = activate_profile(profile_activation_token=request.activation_code, repository=repository)

    except UserAlreadyActive as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        )
    except InvalidActivationCode as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        )
    return ActivateUserResponse(email=user.username, is_active=user.is_active)
