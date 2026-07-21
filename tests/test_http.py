import json, threading, urllib.request, urllib.error
from app.http import create_server
from app.schema import all_schemas
from tests.helpers import DatabaseCase, sample_for

class HTTPTests(DatabaseCase):

    def setUp(self):
        super().setUp()
        self.server = create_server(0, self.db_path, 'test-token')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        super().tearDown()

    def call(self, path, method='GET', data=None, token='test-token', extra=None):
        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
        headers.update(extra or {})
        req = urllib.request.Request(self.base + path, method=method, headers=headers, data=json.dumps(data).encode() if data is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                return (response.status, response.read(), response.headers)
        except urllib.error.HTTPError as error:
            return (error.code, error.read(), error.headers)

    def test_public_health_and_static_ui(self):
        status, body, headers = self.call('/api/health', token='wrong')
        self.assertEqual(status, 200)
        self.assertEqual(self.call('/')[0], 200)
        self.assertIn('frame-ancestors', headers['Content-Security-Policy'])

    def test_auth_is_required_for_data(self):
        self.assertEqual(self.call('/api/dashboard', token='wrong')[0], 401)

    def test_all_resource_routes(self):
        for name in all_schemas():
            status, body, _ = self.call('/api/resources/' + name)
            self.assertEqual(status, 200)
            self.assertIn('items', json.loads(body))

    def test_protected_resource_cannot_be_written(self):
        name = next((n for n, s in all_schemas().items() if not s['writable']))
        self.assertEqual(self.call('/api/resources/' + name, 'POST', sample_for(self.conn, name))[0], 403)

    def test_write_round_trip(self):
        name = next((n for n, s in all_schemas().items() if s['writable']))
        status, body, _ = self.call('/api/resources/' + name, 'POST', sample_for(self.conn, name))
        self.assertEqual(status, 201)
        row = json.loads(body)
        self.assertEqual(self.call('/api/resources/' + name + '/' + row['id'])[0], 200)
        payload = {k: v for k, v in row.items() if k != 'id'}
        self.assertEqual(self.call('/api/resources/' + name + '/' + row['id'], 'PUT', payload)[0], 200)
        self.assertEqual(self.call('/api/resources/' + name + '/' + row['id'] + '?version=1', 'DELETE')[0], 409)

    def test_foreign_host_and_traversal_blocked(self):
        self.assertEqual(self.call('/api/health', extra={'Host': 'foreign.example'})[0], 403)
        self.assertEqual(self.call('/%2e%2e/app/config.py')[0], 404)

    def test_invalid_query_and_json(self):
        name = next(iter(all_schemas()))
        self.assertEqual(self.call('/api/resources/' + name + '?limit=-1')[0], 400)
        self.assertEqual(self.call('/api/workflows/nonexistent', 'POST', [])[0], 400)
