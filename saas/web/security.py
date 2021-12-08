from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from saas.database.models import ProfileRepository
from saas.domain.exceptions import UsernameDoesNotExist
from saas.domain.users import Profile
from saas.service.authentication import decode_access_token
from saas.service.exceptions import InvalidToken
from saas.web.session import profile_database

oauth2 = OAuth2PasswordBearer(tokenUrl='/users/actions/login')


def get_profile(
    access_token: str = Depends(oauth2),
    user_repo: 'ProfileRepository' = Depends(profile_database),
) -> 'Profile':
    try:
        decoded_username = decode_access_token(access_token=access_token)
        profile = user_repo.retrieve_by_username(username=decoded_username)

    except (InvalidToken, UsernameDoesNotExist) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        )
    else:
        return profile


def get_admin_profile(profile: 'Profile' = Depends(get_profile)) -> 'Profile':
    if not (profile.user.is_admin or profile.user.is_super_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin permission required.')

    return profile


def get_super_admin_profile(profile: 'Profile' = Depends(get_profile)) -> 'Profile':
    if not profile.user.is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin permission required.')

    return profile
