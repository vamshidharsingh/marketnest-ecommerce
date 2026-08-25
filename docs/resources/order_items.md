# Order Items

Price snapshots taken during checkout.

| Field | Type | Constraint |
| --- | --- | --- |
| `order_id` | string | Reference to `orders` |
| `product_id` | string | Reference to `products` |
| `quantity` | integer | Required |
| `unit_price_cents` | integer | Required |

Read endpoint: `GET /api/resources/order_items`. A local operator bearer token is required.
This resource is read-only through the generic HTTP API. Use the documented business workflows so derived state remains consistent.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `[]`.
Fixture file: `fixtures/order_items.json`. Repository exact-match helper: `find_by_order_id`.
Test module: `tests/test_order_items.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
