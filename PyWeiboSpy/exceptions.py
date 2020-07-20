class SpyError(Exception):
    def __init__(self, error):
        super().__init__(error)


class LoginError(SpyError):
    def __init__(self, error):
        super().__init__(error)
