# Orders

Atomic checkout totals; payment status is explicitly simulated.

| Field | Type | Constraint |
| --- | --- | --- |
| `customer_id` | string | Reference to `customers` |
| `cart_id` | string | Reference to `carts` |
| `subtotal_cents` | integer | Required |
| `discount_cents` | integer | Required |
| `total_cents` | integer | Required |
| `status` | string | placed, refunded |
| `key` | string | Required |

Read endpoint: `GET /api/resources/orders`. A local operator bearer token is required.
This resource is read-only through the generic HTTP API. Use the documented business workflows so derived state remains consistent.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `["key", "cart_id"]`.
Fixture file: `fixtures/orders.json`. Repository exact-match helper: `find_by_customer_id`.
Test module: `tests/test_orders.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
