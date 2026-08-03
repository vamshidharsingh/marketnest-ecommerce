# Tax Rules

Reference tax rates in basis points; checkout excludes tax in this version.

| Field | Type | Constraint |
| --- | --- | --- |
| `region` | string | Required |
| `rate_basis_points` | integer | Required |

Read endpoint: `GET /api/resources/tax_rules`. A local operator bearer token is required.
Create, update and delete are supported by the operator resource API. PUT is a full replacement and requires `_version`; deletes require a version query parameter.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `[]`.
Fixture file: `fixtures/tax_rules.json`. Repository exact-match helper: `find_by_region`.
Test module: `tests/test_tax_rules.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
