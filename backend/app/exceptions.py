"""
Domain-level exceptions.

Why these exist:
    Services should be able to say "this is a duplicate email" or
    "this employee doesn't exist" without knowing anything about HTTP
    status codes — that's a router/framework concern, not a business
    logic concern. Services raise these; main.py's exception handlers
    (registered below in this phase) translate them into clean JSON
    error responses with the right status code.

    This keeps routers thin (they don't need try/except blocks around
    every service call) and keeps raw Python/SQLAlchemy exceptions from
    ever reaching the client — satisfying the "don't expose internal
    exceptions" requirement from the spec.
"""


class AppException(Exception):
    """Base class for all domain exceptions. Never raised directly."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnauthorizedException(AppException):
    """Invalid credentials or missing/invalid JWT. Maps to HTTP 401."""


class ForbiddenException(AppException):
    """Authenticated, but not allowed to perform this action. Maps to HTTP 403."""


class NotFoundException(AppException):
    """Requested resource does not exist. Maps to HTTP 404."""


class ConflictException(AppException):
    """Request conflicts with existing data (duplicate email, duplicate attendance). Maps to HTTP 409."""


class ValidationException(AppException):
    """Business-rule validation failure that isn't a simple Pydantic type error. Maps to HTTP 422."""
