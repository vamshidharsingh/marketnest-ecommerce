# Shipping Methods

Manual delivery rate catalog; checkout excludes shipping in this version.

| Field | Type | Constraint |
| --- | --- | --- |
| `name` | string | Required |
| `price_cents` | integer | Required |
| `estimated_days` | integer | Required |

Read endpoint: `GET /api/resources/shipping_methods`. A local operator bearer token is required.
Create, update and delete are supported by the operator resource API. PUT is a full replacement and requires `_version`; deletes require a version query parameter.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `[]`.
Fixture file: `fixtures/shipping_methods.json`. Repository exact-match helper: `find_by_name`.
Test module: `tests/test_shipping_methods.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
