from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from shop.domain.errors import (
    Conflict,
    DomainError,
    Forbidden,
    NotFound,
    PaymentDeclined,
    Unauthorized,
    ValidationFailed,
)

STATUS_CODES: dict[type[DomainError], int] = {
    NotFound: 404,
    ValidationFailed: 422,
    Conflict: 409,
    PaymentDeclined: 402,
    Unauthorized: 401,
    Forbidden: 403,
}


def status_for(error: DomainError) -> int:
    for error_type in type(error).__mro__:
        if error_type in STATUS_CODES:
            return STATUS_CODES[error_type]
    return 400


def install(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status_for(exc),
            content={"error": {"code": exc.code, "message": exc.message}},
        )
