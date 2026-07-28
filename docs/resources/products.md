# Products

Sellable items priced in integer cents.

| Field | Type | Constraint |
| --- | --- | --- |
| `sku` | string | Required |
| `name` | string | Required |
| `category_id` | string | Reference to `categories` |
| `brand_id` | string | Reference to `brands` |
| `price_cents` | integer | Required |
| `stock` | integer | Required |
| `status` | string | active, draft |

Read endpoint: `GET /api/resources/products`. A local operator bearer token is required.
Create, update and delete are supported by the operator resource API. PUT is a full replacement and requires `_version`; deletes require a version query parameter.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `["sku"]`.
Fixture file: `fixtures/products.json`. Repository exact-match helper: `find_by_category_id`.
Test module: `tests/test_products.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
