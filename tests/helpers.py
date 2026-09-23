import itertools, json, tempfile, unittest, uuid
from pathlib import Path
from app.db import connect
from app.seed import seed
from app.schema import get_schema
from app.repository import Repository

class DatabaseCase(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db_path = Path(self.directory.name) / 'test.sqlite3'
        self.conn = connect(self.db_path)
        seed(self.conn)

    def tearDown(self):
        self.conn.close()
        self.directory.cleanup()

def sample_for(conn, resource):
    schema = get_schema(resource)
    marker = uuid.uuid4().hex[:10]
    data = {}
    for name, rule in schema['fields'].items():
        if 'ref' in rule:
            row = conn.execute('SELECT id FROM records WHERE resource=? ORDER BY id LIMIT 1', (rule['ref'],)).fetchone()
            if row is None:
                row = {'id': Repository(conn, rule['ref']).create(sample_for(conn, rule['ref']))['id']}
            data[name] = row['id']
        elif 'enum' in rule:
            data[name] = rule['enum'][0]
        elif rule['type'] in ('integer', 'number'):
            data[name] = max(3, rule.get('minimum', 0))
        elif rule.get('format') == 'email':
            data[name] = marker + '@example.test'
        elif rule.get('format') == 'date':
            data[name] = '2030-01-01'
        elif rule.get('format') == 'datetime':
            data[name] = '2030-01-01T09:00:00+00:00'
        elif 'pattern' in rule:
            data[name] = '2030-01'
        elif rule.get('maxLength') == 4:
            data[name] = '6789'
        else:
            data[name] = 'sample-' + marker
    for constraint in schema['unique']:
        if not isinstance(constraint, list):
            continue
        choices = []
        for name in constraint:
            ref = schema['fields'][name].get('ref')
            choices.append([r['id'] for r in conn.execute('SELECT id FROM records WHERE resource=? ORDER BY id', (ref,))] if ref else [data[name]])
        existing = [json.loads(r['payload']) for r in conn.execute('SELECT payload FROM records WHERE resource=?', (resource,))]
        for combo in itertools.product(*choices):
            candidate = dict(zip(constraint, combo))
            if not any((all((row[k] == v for k, v in candidate.items())) for row in existing)):
                data.update(candidate)
                break
    return data
