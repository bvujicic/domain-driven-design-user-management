from datetime import datetime, timezone, timedelta

from jose import jwt

from saas.core.config import configuration
from saas.service.exceptions import InvalidToken


def create_access_token(*, username: str) -> str:
    claims = {'sub': 'access', 'username': username, 'iat': datetime.now(tz=timezone.utc)}
    return _create_json_web_token(claims=claims)


def create_profile_activation_token(*, username: str) -> str:
    claims = {'sub': 'activation', 'username': username, 'iat': datetime.now(tz=timezone.utc)}
    return _create_json_web_token(claims=claims)


def create_password_change_token(*, username: str) -> str:
    current_time = datetime.now(tz=timezone.utc)
    claims = {
        'sub': 'password',
        'username': username,
        'iat': current_time,
        'exp': current_time + timedelta(seconds=configuration.JWT_CHANGE_TOKEN_EXPIRY_IN_SECONDS),
    }
    return _create_json_web_token(claims=claims)


def create_username_change_token(*, username: str, new_username: str) -> str:
    current_time = datetime.now(tz=timezone.utc)
    claims = {
        'sub': 'username',
        'username': username,
        'new_username': new_username,
        'iat': current_time,
        'exp': current_time + timedelta(seconds=configuration.JWT_CHANGE_TOKEN_EXPIRY_IN_SECONDS),
    }
    return _create_json_web_token(claims=claims)


def decode_access_token(*, access_token: str) -> str:
    decoded_access_token = _decode_json_web_token(token=access_token)

    return decoded_access_token['username']


def decode_profile_activation_token(*, token) -> str:
    decoded_profile_activation_token = _decode_json_web_token(token=token)

    if decoded_profile_activation_token.get('sub', None) != 'activation':
        raise InvalidToken(token=token)

    return decoded_profile_activation_token['username']


def decode_password_change_token(*, password_change_token: str) -> str:
    decoded_password_change_token = _decode_json_web_token(token=password_change_token)

    if decoded_password_change_token.get('sub', None) != 'password':
        raise InvalidToken(token=password_change_token)

    return decoded_password_change_token['username']


def decode_username_change_token(*, username_change_token: str) -> tuple[str, str]:
    decoded_username_change_token = _decode_json_web_token(token=username_change_token)

    if decoded_username_change_token.get('sub', None) != 'username':
        raise InvalidToken(token=username_change_token)

    return decoded_username_change_token['username'], decoded_username_change_token['new_username']


def _create_json_web_token(claims: dict) -> str:
    return jwt.encode(claims=claims, key=configuration.SECRET_KEY, algorithm=configuration.JWT_ALGORITHM)


def _decode_json_web_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token=token, key=configuration.SECRET_KEY, algorithms=[configuration.JWT_ALGORITHM])
    except jwt.JWTError:
        raise InvalidToken(token=token)
    else:
        return decoded_token
