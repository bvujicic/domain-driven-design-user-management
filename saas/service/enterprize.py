from saas.domain.users import ProfileAbstractRepository, Enterprize


def create_enterprize(name: str, subdomain: str, repository: 'ProfileAbstractRepository') -> 'Enterprize':
    enterprize = Enterprize(name=name, subdomain=subdomain)

    repository.create_enterprize(enterprize=enterprize)

    return enterprize
