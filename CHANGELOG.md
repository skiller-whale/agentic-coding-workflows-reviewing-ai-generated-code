# Changelog

## Unreleased

## 0.7.0

- Added employee discounts: staff can give a customer account a percentage off with `PUT /admin/customers/{id}/employee-discount`. It shows on orders as an adjustment of kind `employee`.

## 0.6.0

- Added loyalty points. Customers earn a point per pound, and can redeem points at checkout with `redeem_points`.
- Orders now have `adjustments`, `loyalty_points_earned` and `loyalty_points_redeemed`.

## 0.5.0

- Added the audit log, and `GET /admin/audit`.
