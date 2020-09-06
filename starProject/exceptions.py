class SaltLifeError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WrongHashException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
