class DomainError(Exception):
    """A problem the caller can do something about. The API maps each subclass to a status."""

    code = "error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFound(DomainError):
    code = "not_found"


class ValidationFailed(DomainError):
    code = "validation_failed"


class Conflict(DomainError):
    code = "conflict"


class PaymentDeclined(DomainError):
    code = "payment_declined"


class Unauthorized(DomainError):
    code = "unauthorized"


class Forbidden(DomainError):
    code = "forbidden"
