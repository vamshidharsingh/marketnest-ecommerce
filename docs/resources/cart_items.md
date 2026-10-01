# Cart Items

Workflow-managed basket lines with aggregated quantities.

| Field | Type | Constraint |
| --- | --- | --- |
| `cart_id` | string | Reference to `carts` |
| `product_id` | string | Reference to `products` |
| `quantity` | integer | Required |

Read endpoint: `GET /api/resources/cart_items`. A local operator bearer token is required.
This resource is read-only through the generic HTTP API. Use the documented business workflows so derived state remains consistent.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `[["cart_id", "product_id"]]`.
Fixture file: `fixtures/cart_items.json`. Repository exact-match helper: `find_by_cart_id`.
Test module: `tests/test_cart_items.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
