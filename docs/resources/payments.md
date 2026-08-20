# Payments

Simulated checkout payment confirmations; no card processing.

| Field | Type | Constraint |
| --- | --- | --- |
| `order_id` | string | Reference to `orders` |
| `amount_cents` | integer | Required |
| `status` | string | simulated, refunded |
| `provider` | string | demo |

Read endpoint: `GET /api/resources/payments`. A local operator bearer token is required.
This resource is read-only through the generic HTTP API. Use the documented business workflows so derived state remains consistent.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `["order_id"]`.
Fixture file: `fixtures/payments.json`. Repository exact-match helper: `find_by_order_id`.
Test module: `tests/test_payments.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
