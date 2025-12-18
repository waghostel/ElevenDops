"""Custom exceptions for Backend API client.

These exceptions provide meaningful error messages for UI handling
when API calls fail.
"""


class APIError(Exception):
    """Base exception for API errors.

    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code if available.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class APIConnectionError(APIError):
    """Exception raised when connection to API fails.

    This is raised when the client cannot establish a connection
    to the backend API server.
    """

    def __init__(self, message: str = "Failed to connect to backend API") -> None:
        super().__init__(message, status_code=None)


class APITimeoutError(APIError):
    """Exception raised when API request times out.

    This is raised when the API request exceeds the configured
    timeout duration.
    """

    def __init__(self, message: str = "API request timed out") -> None:
        super().__init__(message, status_code=408)
