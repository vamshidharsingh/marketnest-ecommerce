# Security model and practical limits

This is a local single-operator project using synthetic data. Its default operator token is intentionally public for a disposable demonstration. Set a custom `APP_TOKEN` before sharing the process within a development environment. Token comparison uses `hmac.compare_digest`; tokens are never put in URLs. The interface keeps the entered token in browser sessionStorage until the tab session ends.

## Implemented controls
- Default loopback binding and strict loopback Host headers reduce accidental exposure and DNS rebinding.
- Every data API requires the operator token. Public metadata contains schemas and fixtures' example workflow IDs, not stored records.
- No CORS headers permit cross-origin browser data access. JSON content type and bearer credentials protect mutations from ordinary cross-site form submissions.
- Request bodies have a size limit. IDs have a restricted character set; static paths are resolved and checked against the web directory.
- SQL uses parameterized values. Browser-generated content uses textContent. CSV cells with leading spreadsheet formula characters are prefixed with an apostrophe.
- Required fields, integer money, finite measurements, reference targets and unique tuples are validated before commit.
- Transactional workflows and optimistic versions protect consistency. Failed writes also roll back audit rows.
- CSP excludes third-party script, frames and remote connections; cache headers avoid storing API responses in ordinary caches.

## Boundaries
There is no multi-user login, role system, patient isolation, encryption at rest, TLS termination, token rotation UI, rate limiter or retention engine. A valid local operator token grants all demo records. Health consent controls card display only; it is not a general patient permission system. Do not interpret it as a complete clinical access model.

Python's standard-library HTTP server is suitable for local development, not public hosting. Keep deployment on loopback. Container mode requires a custom token and maps host ports to loopback. File-system access to the database remains equivalent to full record access. Backups and exported CSV files should be handled as copies of the entire selected data.

## Domain scope
Local store operations demo. Payments and refunds are simulated. Checkout excludes tax and shipping; their catalogs are reference-only. Stock is tracked per product, not variant. Coupons have usage limits but no expiry schedule; full refunds do not restore coupon uses.

## Extending the project
For real users, replace the local server adapter, design a normalized database and server-enforced row-level permissions, add explicit migrations, structured retention, TLS, secret management and independent security testing. Revisit domain invariants when introducing external payments, multiple currencies, partial receipts, clinical records or tax calculations. The current tests verify the documented local scope.
