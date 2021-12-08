from passlib.hash import argon2

from saas.domain.exceptions import InvalidPasswordHash


def create_hashed_password(*, plain_password: str):
    return argon2.hash(secret=plain_password)


def verify_hashed_password(*, plain_password: str, password: str):
    try:
        return argon2.verify(secret=plain_password, hash=password)
    except (ValueError, TypeError):
        raise InvalidPasswordHash(hashed_password=password)
