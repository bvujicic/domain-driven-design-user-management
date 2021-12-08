class EnterprizeDoesNotExist(Exception):
    def __init__(self, subdomain: str):
        self.message = f'Enterprize with subdomain \'{subdomain}\' does not exist.'
        super().__init__(self.message)


class EnterprizeExists(Exception):
    def __init__(self, subdomain: str):
        self.message = f'Enterprize with subdomain \'{subdomain}\' already exists.'
        super().__init__(self.message)


class UserNotAdmin(Exception):
    def __init__(self, username: str):
        self.message = f'User with username \'{username}\' is not an admin.'
        super().__init__(self.message)


class UserDoesNotExist(Exception):
    def __init__(self, reference: str):
        self.message = f'User with reference \'{reference}\' does not exist.'
        super().__init__(self.message)


class UsernameDoesNotExist(Exception):
    def __init__(self, username: str):
        self.message = f'User with username \'{username}\' does not exist.'
        super().__init__(self.message)


class UsernameExists(Exception):
    def __init__(self, username: str):
        self.message = f'User with username \'{username}\' already exists.'
        super().__init__(self.message)


class UserAlreadyExists(Exception):
    def __init__(self, profile_reference: str):
        self.message = f'Profile with reference \'{profile_reference}\' already has a registered user.'
        super().__init__(self.message)


class UserAlreadyActive(Exception):
    def __init__(self, username: str):
        self.message = f'User with username \'{username}\' is already active.'
        super().__init__(self.message)


class UserInactive(Exception):
    def __init__(self, username: str):
        self.message = f'User with username \'{username}\' is registered, but not active.'
        super().__init__(self.message)


class InvalidPasswordHash(Exception):
    def __init__(self, hashed_password: str):
        self.message = f'Hashed password \'{hashed_password}\' is invalid.'
        super().__init__(self.message)
