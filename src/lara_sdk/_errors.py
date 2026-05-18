class LaraError(Exception):
    pass


class LaraApiError(LaraError):
    @classmethod
    def from_response(cls, response):
        body = response.json()

        _type = body.get('type', 'UnknownError')
        message = body.get('message', 'An unknown error occurred')

        return cls(response.status_code, _type, message)

    def __init__(self, status_code: int, _type: str, message: str):
        super().__init__(f'(HTTP {status_code}) {_type}: {message}')

        self.status_code: int = status_code
        self.type: str = _type
        self.message: str = message
