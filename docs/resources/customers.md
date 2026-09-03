# Customers

Synthetic buyer profiles.

| Field | Type | Constraint |
| --- | --- | --- |
| `name` | string | Required |
| `email` | string | email |

Read endpoint: `GET /api/resources/customers`. A local operator bearer token is required.
Create, update and delete are supported by the operator resource API. PUT is a full replacement and requires `_version`; deletes require a version query parameter.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `["email"]`.
Fixture file: `fixtures/customers.json`. Repository exact-match helper: `find_by_name`.
Test module: `tests/test_customers.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
