"""End-to-end local API smoke check in a disposable seeded database."""
import json, sys, tempfile, threading, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connect
from app.seed import seed
from app.http import create_server
from app.project import PROJECT
if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'demo.sqlite3'
        conn = connect(path)
        seed(conn)
        conn.close()
        server = create_server(0, path, 'smoke-token')
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'

        def get(route):
            req = urllib.request.Request(base + route, headers={'Authorization': 'Bearer smoke-token'})
            with urllib.request.urlopen(req, timeout=5) as response:
                assert response.status == 200
                return json.loads(response.read())
        try:
            assert get('/api/health')['status'] == 'ok'
            for name in PROJECT['seed_order']:
                assert 'items' in get('/api/resources/' + name)
            assert len(get('/api/dashboard')['metrics']) == 4
            print('PASS: live HTTP health, 20 resource routes, dashboard')
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
