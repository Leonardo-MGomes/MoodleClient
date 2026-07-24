from typing import Any


class MoodleError(Exception):
    """Base exception for all Moodle client errors."""

    def __init__(self, message: str, details: Any | None = None):
        super().__init__(message)
        self.details = details


class MoodleNetworkError(MoodleError):
    """Wraps transport-level errors (timeouts, DNS, etc.)."""



class MoodleApiError(MoodleError):
    """Wraps HTTP 4xx/5xx responses."""

    def __init__(
        self, message: str, status_code: int, response_body: str | None = None
    ):
        super().__init__(
            message,
            details={"status_code": status_code, "response_body": response_body},
        )
        self.status_code = status_code
        self.response_body = response_body


class MoodleAuthError(MoodleError):
    """For authentication failures or token-related issues."""



class MoodleValidationError(MoodleError):
    """Wraps JSON decoding and Pydantic validation errors."""

