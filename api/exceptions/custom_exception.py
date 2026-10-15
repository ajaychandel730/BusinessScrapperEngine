from api.exceptions.global_exception import GlobalException


class ScraperFailedException(GlobalException):
    def __init__(self, message: str = "Scraper failed to retrieve data"):
        super().__init__(message=message, status_code=502, code="SCRAPER_FAILED")

class SecurityInputValidationException(GlobalException):
    def __init__(self, field_name: str):
        message = f"Malicious scripting or tags detected in '{field_name}'."
        super().__init__(message=message, status_code=403, code="INVALID_INPUT")
        