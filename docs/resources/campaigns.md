# Campaigns

Manual merchandising campaign plans.

| Field | Type | Constraint |
| --- | --- | --- |
| `name` | string | Required |
| `starts_on` | string | date |
| `ends_on` | string | date |
| `status` | string | draft, active, complete |

Read endpoint: `GET /api/resources/campaigns`. A local operator bearer token is required.
Create, update and delete are supported by the operator resource API. PUT is a full replacement and requires `_version`; deletes require a version query parameter.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `[]`.
Fixture file: `fixtures/campaigns.json`. Repository exact-match helper: `find_by_name`.
Test module: `tests/test_campaigns.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
