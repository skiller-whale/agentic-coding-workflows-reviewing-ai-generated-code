"""Staff-only endpoints. Everything under /admin requires a staff token."""

from fastapi import APIRouter, Depends

from shop.api.deps import require_staff
from shop.api.routes.admin import audit, customers, orders, products

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_staff)])
router.include_router(products.router)
router.include_router(orders.router)
router.include_router(customers.router)
router.include_router(audit.router)
