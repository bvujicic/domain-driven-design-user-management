class PostDoesNotExist(Exception):
    def __init__(self, reference: str):
        self.message = f'Post with reference \'{reference}\' does not exist.'
        super().__init__(self.message)
