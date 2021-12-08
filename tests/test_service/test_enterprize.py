import pytest

from saas.domain.exceptions import EnterprizeExists
from saas.service.enterprize import create_enterprize


class TestCreateEnterprize:
    def test_can_create_enterprize(self, user_repository):
        enterprize = create_enterprize(name='test', subdomain='test', repository=user_repository)

        assert enterprize.name == 'test'
        assert enterprize.subdomain == 'test'

    def test_cannot_create_enterprize_subdomain_exists(self, user_repository, enterprize):
        with pytest.raises(EnterprizeExists):
            create_enterprize(
                name=enterprize.name,
                subdomain=enterprize.subdomain,
                repository=user_repository,
            )
