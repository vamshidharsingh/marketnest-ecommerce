"""Loopback-only operator HTTP API and local static UI."""
import json, logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from .db import connect
from .auth import authorize
from .config import MAX_BODY, TOKEN
from .project import PROJECT
from .schema import all_schemas, get_schema
from .registry import repository
from .errors import AppError, Forbidden, NotFound
from .pagination import pagination
from .reports import dashboard
from .audit import recent
from .export import export_csv
from .static import static_file
from .workflows import execute

class Handler(BaseHTTPRequestHandler):
    server_version = 'LocalPortfolio/1.0'

    def respond(self, status, value, content_type='application/json'):
        body = json.dumps(value, allow_nan=False).encode() if content_type == 'application/json' else value.encode() if isinstance(value, str) else value
        self.send_response(status)
        self.send_header('Content-Type', content_type + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            raise AppError('Invalid Content-Length')
        if not 0 < length <= MAX_BODY:
            raise AppError('Body must be 1 to 65536 bytes')
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            raise AppError('Content-Type application/json required')
        try:
            data = json.loads(self.rfile.read(length), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        except (ValueError, UnicodeDecodeError):
            raise AppError('Invalid JSON')
        if not isinstance(data, dict):
            raise AppError('JSON object required')
        return data

    def handle_request(self):
        conn = None
        try:
            if self.headers.get('Host', '') not in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}:
                raise Forbidden('Loopback Host header required')
            url = urlparse(self.path)
            parts = url.path.strip('/').split('/')
            query = parse_qs(url.query)
            if self.command == 'GET' and url.path == '/api/health':
                return self.respond(200, {'status': 'ok', 'project': PROJECT['slug']})
            if self.command == 'GET' and url.path == '/api/meta':
                return self.respond(200, dict(project=PROJECT, schemas=all_schemas()))
            if not url.path.startswith('/api/'):
                if self.command != 'GET':
                    raise NotFound('Endpoint not found')
                value, mime = static_file(url.path)
                return self.respond(200, value, mime)
            authorize(self.headers, self.server.token)
            conn = connect(self.server.db_path)
            if self.command == 'GET' and url.path == '/api/dashboard':
                return self.respond(200, dashboard(conn))
            if self.command == 'GET' and url.path == '/api/audit':
                return self.respond(200, {'items': recent(conn)})
            if self.command == 'GET' and len(parts) == 3 and (parts[1] == 'export'):
                return self.respond(200, export_csv(conn, parts[2]), 'text/csv')
            if self.command == 'POST' and len(parts) == 3 and (parts[1] == 'workflows'):
                return self.respond(200, execute(conn, parts[2], self.body()))
            if len(parts) in (3, 4) and parts[1] == 'resources':
                resource = parts[2]
                repo = repository(conn, resource)
                id = parts[3] if len(parts) == 4 else None
                if self.command == 'GET':
                    if id:
                        return self.respond(200, repo.get(id))
                    limit, offset = pagination(query)
                    search = query.get('search', [''])[0]
                    return self.respond(200, dict(items=repo.list(search=search, limit=limit, offset=offset), total=repo.count(), limit=limit, offset=offset))
                if not get_schema(resource)['writable']:
                    raise Forbidden('Workflow-managed resource is read-only')
                if self.command == 'POST' and (not id):
                    return self.respond(201, repo.create(self.body()))
                if self.command == 'PUT' and id:
                    data = self.body()
                    version = data.pop('_version', None)
                    return self.respond(200, repo.update(id, data, version))
                if self.command == 'DELETE' and id:
                    try:
                        version = int(query.get('version', [''])[0])
                    except ValueError:
                        raise AppError('Delete requires version query parameter')
                    repo.delete(id, version)
                    return self.respond(200, {'deleted': id})
            raise NotFound('Endpoint not found')
        except AppError as exc:
            self.respond(exc.status, {'error': str(exc)})
        except Exception:
            logging.exception('Request failed')
            self.respond(500, {'error': 'Internal server error'})
        finally:
            if conn:
                conn.close()
    do_GET = handle_request
    do_POST = handle_request
    do_PUT = handle_request
    do_DELETE = handle_request

    def log_message(self, format, *args):
        logging.info(format, *args)

def create_server(port, db_path=None, token=TOKEN, host='127.0.0.1'):
    server = ThreadingHTTPServer((host, port), Handler)
    server.db_path = db_path
    server.token = token
    return server
