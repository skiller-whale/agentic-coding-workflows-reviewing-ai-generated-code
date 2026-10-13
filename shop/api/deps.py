from fastapi import Depends, Header, Request

from shop.domain.errors import Forbidden, Unauthorized
from shop.domain.models import Customer, StaffMember
from shop.services import Services


def get_services(request: Request) -> Services:
    return request.app.state.services


def _principal(authorization: str | None, services: Services) -> tuple[str, int]:
    if not authorization or not authorization.startswith("Bearer "):
        raise Unauthorized("Sign in to do that")
    principal = services.tokens.resolve(authorization.removeprefix("Bearer "))
    if principal is None:
        raise Unauthorized("That token isn't valid")
    return principal


def current_customer(
    authorization: str | None = Header(default=None),
    services: Services = Depends(get_services),
) -> Customer:
    kind, principal_id = _principal(authorization, services)
    if kind != "customer":
        raise Forbidden("Only customers can do that")
    return services.customers.get(principal_id)


def require_staff(
    authorization: str | None = Header(default=None),
    services: Services = Depends(get_services),
) -> StaffMember:
    kind, principal_id = _principal(authorization, services)
    if kind != "staff":
        raise Forbidden("Only staff can do that")
    return services.staff.get(principal_id)
