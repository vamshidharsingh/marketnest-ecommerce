# MarketNest architecture

## Request path
The static browser interface calls the HTTP adapter on the same origin. The adapter checks Host and bearer token, bounds request size, parses JSON, opens a short-lived SQLite connection and selects a repository or workflow. Responses have no-store caching, content type protection and a restrictive content security policy. DOM text is created with textContent rather than user-controlled HTML.

## Data model
The records table has a composite `(resource, id)` primary key, JSON payload, integer version, and created/updated timestamps. Schema JSON validates required fields, exact types, allowed choices and references. Unique fields and composite tuples are checked inside the same writer transaction. There are 20 resources; the UI and resource API use their schemas as the common contract.

This design favors transparent resource contracts in a portable demo. It is not a normalized high-throughput storage design. Filtering, uniqueness and reporting scan JSON payloads in memory. There is no database-side relational foreign-key enforcement for the payloads. Direct SQL must therefore not be used as an application write API.

## Atomicity and concurrency
`transaction()` obtains a SQLite `BEGIN IMMEDIATE` writer lock before reading workflow state. Concurrent writers serialize, so check-and-update decisions cannot interleave. On any domain error or validation failure, the transaction and its audit rows roll back. Workflows call nested repository operations under the existing transaction. Normal CRUD also uses a transaction and requires the caller's current version for updates and deletion.

Retry identifiers are not blindly accepted: finance transfer/deposit, supply shipment/receipt/transfer, and checkout commands compare key inputs. Card issuance returns an existing active card. Health booking rejects an exact timestamp collision, including equivalent timezone offsets. Add-to-cart intentionally increments quantity and is not an idempotent command. Refund is full-order and can apply once.

## Audit and export
Audit records store action, resource, record ID and UTC timestamp, without sensitive payloads. CSV exports include every record and neutralize leading formula characters. SQLite backup uses the online backup API rather than copying a possibly incomplete database file.

## Interface
Overview metrics derive from database state. Resource pages search, paginate, export and edit operator-managed records. Workflow-managed resources are read-only through generic HTTP CRUD. Workflow forms expose request examples, show returned IDs and let subsequent commands reuse those IDs. No outbound email, SMS, payments or carrier calls occur.

## Validation evidence
The delivered suite uses temporary real SQLite databases, a live threaded HTTP server and independent simultaneous connections. The bundle's `VERIFICATION.md` reports actual command results. No performance, clinical accuracy, production availability or cloud deployment benchmark is claimed.
