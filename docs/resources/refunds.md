# Refunds

Full-order refunds with stock restoration, applied once.

| Field | Type | Constraint |
| --- | --- | --- |
| `order_id` | string | Reference to `orders` |
| `amount_cents` | integer | Required |
| `reason` | string | Required |

Read endpoint: `GET /api/resources/refunds`. A local operator bearer token is required.
This resource is read-only through the generic HTTP API. Use the documented business workflows so derived state remains consistent.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `["order_id"]`.
Fixture file: `fixtures/refunds.json`. Repository exact-match helper: `find_by_order_id`.
Test module: `tests/test_refunds.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
