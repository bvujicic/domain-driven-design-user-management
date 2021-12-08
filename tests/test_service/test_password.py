import pytest
from passlib.hash import argon2

from saas.domain.exceptions import InvalidPasswordHash
from saas.domain.services import create_hashed_password, verify_hashed_password


class TestPassword:
    plain_password = 'plain_password'

    def test_can_create_password_hash(self):
        hashed_password = create_hashed_password(plain_password=self.plain_password)

        is_verified = argon2.verify(secret=self.plain_password, hash=hashed_password)

        assert is_verified

    def test_can_verify_password_hash(self):
        hashed_password = argon2.hash(secret=self.plain_password)

        is_verified = verify_hashed_password(plain_password=self.plain_password, password=hashed_password)

        assert is_verified

    def test_malformed_hash(self):
        hashed_password = 'malformed'
        plain_password = 'password'

        with pytest.raises(InvalidPasswordHash):
            verify_hashed_password(plain_password=plain_password, password=hashed_password)
