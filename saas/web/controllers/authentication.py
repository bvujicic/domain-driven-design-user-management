from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from saas.database.models import ProfileRepository
from saas.domain.users import UserCredentials, Profile
from saas.service.authentication import (
    authenticate_credentials,
    create_access_token,
    change_user_password,
    decode_password_change_token,
    decode_username_change_token,
    initiate_password_change,
    initiate_username_change,
    change_username,
)
from saas.domain.exceptions import UsernameDoesNotExist, UsernameExists, UserInactive
from saas.service.exceptions import InvalidCredentials, InvalidToken
from saas.web.security import get_profile
from saas.web.serializers import (
    LoginResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    InitiateChangePasswordRequest,
    InitiateChangeUsernameRequest,
    ChangeUsernameRequest,
    ChangeUsernameResponse,
)
from saas.web.session import profile_database

authentication_router = APIRouter()


@authentication_router.post(
    path='/users/actions/login',
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    name='Login',
    tags=['login'],
)
def authenticate_user_controller(
    request: OAuth2PasswordRequestForm = Depends(),
    user_repo: ProfileRepository = Depends(profile_database),
):
    credentials = UserCredentials(username=request.username, plain_password=request.password)

    try:
        user = authenticate_credentials(credentials=credentials, repository=user_repo)
        access_token = create_access_token(username=user.username)

    except (InvalidCredentials, UserInactive) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        )

    return LoginResponse(access_token=access_token)


@authentication_router.post(
    path='/users/actions/password/initiate-change',
    status_code=status.HTTP_202_ACCEPTED,
    name='Initiate password change',
    tags=['login'],
)
def initiate_change_password_controller(
    request: 'InitiateChangePasswordRequest', user_repo: 'ProfileRepository' = Depends(profile_database)
):
    try:
        profile = user_repo.retrieve_by_username(username=request.username)
    except UsernameDoesNotExist as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    else:
        initiate_password_change(profile=profile, repository=user_repo)


@authentication_router.post(
    path='/users/actions/password/change',
    status_code=status.HTTP_200_OK,
    response_model=ChangePasswordResponse,
    name='Change password',
    tags=['login'],
)
def change_user_password_controller(
    request: 'ChangePasswordRequest', user_repo: 'ProfileRepository' = Depends(profile_database)
):
    try:
        username = decode_password_change_token(password_change_token=request.password_change_token)
        profile = user_repo.retrieve_by_username(username=username)
    except (InvalidToken, UsernameDoesNotExist):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    change_user_password(profile=profile, new_plain_password=request.new_password, repository=user_repo)
    access_token = create_access_token(username=profile.user.username)

    return ChangePasswordResponse(access_token=access_token)


@authentication_router.post(
    path='/users/actions/username/initiate-change',
    status_code=status.HTTP_202_ACCEPTED,
    name='Initiate username change',
    tags=['login'],
)
def initiate_username_change_controller(
    request: 'InitiateChangeUsernameRequest',
    profile: 'Profile' = Depends(get_profile),
    user_repo: 'ProfileRepository' = Depends(profile_database),
):
    try:
        initiate_username_change(profile=profile, new_username=request.new_username, repository=user_repo)
    except UsernameExists as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@authentication_router.post(
    path='/users/actions/username/change', status_code=status.HTTP_200_OK, name='Change username', tags=['login']
)
def change_username_controller(
    request: 'ChangeUsernameRequest', user_repo: 'ProfileRepository' = Depends(profile_database)
):
    try:
        username, new_username = decode_username_change_token(username_change_token=request.username_change_token)
        profile = user_repo.retrieve_by_username(username=username)
    except (InvalidToken, UsernameDoesNotExist):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    change_username(profile=profile, new_username=new_username, repository=user_repo)
    access_token = create_access_token(username=profile.user.username)

    return ChangeUsernameResponse(access_token=access_token, new_username=profile.user.username)
