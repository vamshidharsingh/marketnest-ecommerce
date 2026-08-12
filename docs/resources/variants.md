# Variants

Descriptive options; this demo checks stock at product level.

| Field | Type | Constraint |
| --- | --- | --- |
| `product_id` | string | Reference to `products` |
| `name` | string | Required |
| `value` | string | Required |

Read endpoint: `GET /api/resources/variants`. A local operator bearer token is required.
Create, update and delete are supported by the operator resource API. PUT is a full replacement and requires `_version`; deletes require a version query parameter.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `[]`.
Fixture file: `fixtures/variants.json`. Repository exact-match helper: `find_by_product_id`.
Test module: `tests/test_variants.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
