import json
from .config import ROOT
from .db import transaction
from .repository import Repository

def seed(conn):
    from .project import PROJECT as config
    with transaction(conn):
        if conn.execute('SELECT COUNT(*) FROM records').fetchone()[0]:
            return False
        for resource in config['seed_order']:
            for row in json.loads((ROOT / 'fixtures' / (resource + '.json')).read_text()):
                Repository(conn, resource).create(row)
    return True
