# Coupons

Percentage discounts with integer arithmetic and explicit use limits.

| Field | Type | Constraint |
| --- | --- | --- |
| `code` | string | Required |
| `percent` | integer | Required |
| `max_uses` | integer | Required |
| `used` | integer | Required |
| `status` | string | active, inactive |

Read endpoint: `GET /api/resources/coupons`. A local operator bearer token is required.
This resource is read-only through the generic HTTP API. Use the documented business workflows so derived state remains consistent.

Foreign keys are checked before writes; referenced records cannot be deleted. Unique constraints: `["code"]`.
Fixture file: `fixtures/coupons.json`. Repository exact-match helper: `find_by_code`.
Test module: `tests/test_coupons.py` checks persistence, validation, duplicate rollback and fixture compatibility.
Every fixture is synthetic and is safe to reset in a disposable local database.
