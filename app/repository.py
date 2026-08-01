import json, uuid
from .db import transaction
from .schema import get_schema, all_schemas
from .validate import validate
from .audit import now, record
from .errors import NotFound, Conflict

class Repository:
    resource = None

    def __init__(self, conn, resource=None):
        self.conn = conn
        self.resource = resource or self.resource
        self.schema = get_schema(self.resource)

    def get(self, id):
        row = self.conn.execute('SELECT * FROM records WHERE resource=? AND id=?', (self.resource, id)).fetchone()
        if row is None:
            raise NotFound('Record not found')
        return dict(id=row['id'], **json.loads(row['payload']), _version=row['version'])

    def list(self, *, search='', limit=200, offset=0):
        rows = self.conn.execute('SELECT * FROM records WHERE resource=? ORDER BY created_at,id', (self.resource,))
        result = [dict(id=r['id'], **json.loads(r['payload']), _version=r['version']) for r in rows]
        if search:
            result = [r for r in result if search.casefold() in json.dumps(r).casefold()]
        return result[offset:offset + limit]

    def count(self):
        return self.conn.execute('SELECT COUNT(*) FROM records WHERE resource=?', (self.resource,)).fetchone()[0]

    def _constraints(self, data, exclude=None):
        for name, rule in self.schema['fields'].items():
            if 'ref' in rule:
                Repository(self.conn, rule['ref']).get(data[name])
        for constraint in self.schema['unique']:
            names = [constraint] if isinstance(constraint, str) else constraint
            rows = self.conn.execute('SELECT id,payload FROM records WHERE resource=?', (self.resource,))
            for row in rows:
                existing = json.loads(row['payload'])
                if row['id'] != exclude and all((existing[n] == data[n] for n in names)):
                    raise Conflict('Unique constraint: ' + ', '.join(names))

    def create(self, data):
        clean = validate(self.schema, data)
        id = data.get('id') or uuid.uuid4().hex
        with transaction(self.conn):
            self._constraints(clean)
            if self.conn.execute('SELECT 1 FROM records WHERE resource=? AND id=?', (self.resource, id)).fetchone():
                raise Conflict('Record id already exists')
            stamp = now()
            self.conn.execute('INSERT INTO records VALUES(?,?,?,?,?,?)', (self.resource, id, json.dumps(clean), 1, stamp, stamp))
            record(self.conn, 'create', self.resource, id)
        return self.get(id)

    def update(self, id, data, version):
        clean = validate(self.schema, data)
        if 'id' in data and data['id'] != id:
            raise Conflict('Record id is immutable')
        with transaction(self.conn):
            current = self.get(id)
            if type(version) is not int or current['_version'] != version:
                raise Conflict('Version mismatch; reload before editing')
            self._constraints(clean, id)
            self.conn.execute('UPDATE records SET payload=?,version=version+1,updated_at=? WHERE resource=? AND id=?', (json.dumps(clean), now(), self.resource, id))
            record(self.conn, 'update', self.resource, id)
        return self.get(id)

    def delete(self, id, version):
        with transaction(self.conn):
            current = self.get(id)
            if current['_version'] != version or type(version) is not int:
                raise Conflict('Version mismatch')
            for name, schema in all_schemas().items():
                refs = [n for n, r in schema['fields'].items() if r.get('ref') == self.resource]
                if not refs:
                    continue
                rows = self.conn.execute('SELECT payload FROM records WHERE resource=?', (name,))
                if any((any((json.loads(row['payload'])[n] == id for n in refs)) for row in rows)):
                    raise Conflict('Referenced by ' + name)
            self.conn.execute('DELETE FROM records WHERE resource=? AND id=?', (self.resource, id))
            record(self.conn, 'delete', self.resource, id)
