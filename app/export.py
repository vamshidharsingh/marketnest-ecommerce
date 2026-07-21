import csv, io
from .repository import Repository
from .schema import get_schema

def export_csv(conn, resource):
    out = io.StringIO(newline='')
    columns = ['id'] + list(get_schema(resource)['fields']) + ['_version']
    writer = csv.DictWriter(out, fieldnames=columns)
    writer.writeheader()
    rows = conn.execute('SELECT id FROM records WHERE resource=? ORDER BY id', (resource,))
    for record in rows:
        row = Repository(conn, resource).get(record['id'])
        safe = {k: "'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@', '\t', '\r')) else v for k, v in row.items()}
        writer.writerow(safe)
    return out.getvalue()
