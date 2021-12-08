class InvalidCredentials(Exception):
    def __init__(self):
        self.message = 'Invalid credentials provided.'
        super().__init__(self.message)


class InvalidToken(Exception):
    def __init__(self, token: str):
        self.message = f'Invalid token \'{token}\'.'
        super().__init__(self.message)


class InvalidActivationCode(Exception):
    def __init__(self, activation_code: str):
        self.message = f'Invalid activation code \'{activation_code}\'.'


class InvalidPasswordHash(Exception):
    def __init__(self, hashed_password: str):
        self.message = f'Hashed password \'{hashed_password}\' is invalid.'
        super().__init__(self.message)


class InvalidPassword(Exception):
    def __init__(self, old_password: str):
        self.message = f'Old password \'{old_password}\' is invalid.'
        super().__init__(self.message)
