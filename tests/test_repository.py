from app.repository import Repository
from app.schema import all_schemas
from app.errors import AppError, Conflict, NotFound
from app.seed import seed
from tests.helpers import DatabaseCase, sample_for

class RepositoryTests(DatabaseCase):

    def test_stale_version_does_not_overwrite(self):
        name = next(iter(all_schemas()))
        repo = Repository(self.conn, name)
        row = repo.create(sample_for(self.conn, name))
        data = {k: v for k, v in row.items() if k not in ('id', '_version')}
        new = repo.update(row['id'], data, 1)
        self.assertEqual(new['_version'], 2)
        with self.assertRaises(Conflict):
            repo.update(row['id'], data, 1)

    def test_missing_foreign_key_rolls_back(self):
        name = next((n for n, s in all_schemas().items() if any(('ref' in r for r in s['fields'].values()))))
        repo = Repository(self.conn, name)
        data = sample_for(self.conn, name)
        key = next((k for k, r in repo.schema['fields'].items() if 'ref' in r))
        data[key] = 'missing-reference'
        before = repo.count()
        with self.assertRaises(NotFound):
            repo.create(data)
        self.assertEqual(repo.count(), before)

    def test_referenced_record_cannot_be_deleted(self):
        name = next((n for n, s in all_schemas().items() if any(('ref' in r for r in s['fields'].values()))))
        child = Repository(self.conn, name).create(sample_for(self.conn, name))
        key = next((k for k, r in all_schemas()[name]['fields'].items() if 'ref' in r))
        parent_repo = Repository(self.conn, all_schemas()[name]['fields'][key]['ref'])
        parent = parent_repo.get(child[key])
        with self.assertRaises(Conflict):
            parent_repo.delete(parent['id'], parent['_version'])

    def test_seeding_is_idempotent(self):
        before = self.conn.execute('SELECT COUNT(*) FROM records').fetchone()[0]
        self.assertFalse(seed(self.conn))
        self.assertEqual(before, self.conn.execute('SELECT COUNT(*) FROM records').fetchone()[0])

    def test_search_pagination(self):
        name = next(iter(all_schemas()))
        repo = Repository(self.conn, name)
        for _ in range(3):
            repo.create(sample_for(self.conn, name))
        self.assertEqual(len(repo.list(limit=2)), 2)
        self.assertEqual(repo.list(search='NEVER-MATCH-THIS'), [])
