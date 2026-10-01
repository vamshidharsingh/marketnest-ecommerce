# Carts

Active customer shopping baskets.

| Field | Type | Constraint |
| --- | --- | --- |
| `customer_id` | string | Reference to `customers` |
| `status` | string | active, checked_out |

Read endpoint: `GET /api/resources/carts`. A local operator bearer token is required.
This resource is read-only through the generic HTTP API. Use the documented business workflows so derived state remains consistent.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `[]`.
Fixture file: `fixtures/carts.json`. Repository exact-match helper: `find_by_customer_id`.
Test module: `tests/test_carts.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
