

class GlobalException(Exception):
    """Base exception for all application-level errors."""
    def __init__(self, message: str, status_code: int = 500, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)