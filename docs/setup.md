# Setup and local operations

## Prerequisites
Python 3.12+ with sqlite3; a browser with JavaScript enabled. Runtime and tests use no third-party packages. Node is only needed for optional JavaScript syntax checks.

## Start
From the `marketnest-ecommerce` directory run `python -B -m app`. Visit `http://127.0.0.1:8014` and connect using the local operator token. `-B` avoids Python cache files. The server initializes `runtime/app.sqlite3` and only seeds a completely empty records table.

## Environment
On Linux/macOS use `export APP_TOKEN='your-local-secret'`. On Windows PowerShell use `$env:APP_TOKEN='your-local-secret'`. Set `APP_DB` to change the database path. `.env.example` is documentation only; the server does not load it. `python -B -m app --port 9000` overrides the port.

Use a different `APP_DB` for a separate demo dataset. Back up before resetting. The backup script refuses to overwrite an existing destination and uses the SQLite backup API so committed WAL data is included.

## Containers
Set `APP_TOKEN` in your shell, then run `docker compose up --build`. Compose publishes the service only on host loopback and stores the database in a named volume. The container runs as UID 10001. The first-run data directory is owned by that user. Container mode binds inside the container on all interfaces, but requires a custom token. The host API still requires a localhost or 127.0.0.1 Host header.

No external credentials are used. Docker commands were not executed in this delivery environment; validate them on your target Docker installation.

## Verify and troubleshoot
Run the unittest suite and smoke test from README. A 401 means the token differs from server configuration; reconnect with the correct value. A 409 means stale version, reference conflict or domain invariant failure; reload before retrying. An empty resource list can be normal for workflow-generated data.

If the port is occupied, choose another `--port`. If a database is locked, stop a second instance or a direct SQL editor. API writes wait up to 15 seconds. This is a local single-operator demonstration, with no cloud dependencies.

## Source count
`scripts/verify_files.py` excludes runtime artifacts and checks exactly 160 source files plus their delivered hashes. Intentional edits should update `PROJECT_MANIFEST.json`. The manifest hash for itself is null. Unzip into a clean folder to reproduce the delivery inventory.
