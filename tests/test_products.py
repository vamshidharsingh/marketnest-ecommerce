"""Contract and validation cases for products."""
import json
from app.config import ROOT
from app.errors import AppError, Conflict
from app.registry import repository
from app.schema import get_schema
from tests.helpers import DatabaseCase, sample_for

class ResourceTests(DatabaseCase):
    resource = 'products'

    def test_round_trip_and_exact_lookup(self):
        repo = repository(self.conn, self.resource)
        data = sample_for(self.conn, self.resource)
        data['id'] = 'contract-record'
        row = repo.create(data)
        self.assertEqual(row['sku'], data['sku'])
        self.assertEqual(row['_version'], 1)
        self.assertTrue(any((r['id'] == row['id'] for r in repo.find_by_category_id(row['category_id']))))

    def test_rejects_missing_and_wrong_type(self):
        repo = repository(self.conn, self.resource)
        data = sample_for(self.conn, self.resource)
        data.pop('sku')
        with self.assertRaises(AppError):
            repo.create(data)
        data = sample_for(self.conn, self.resource)
        data['sku'] = []
        with self.assertRaises(AppError):
            repo.create(data)

    def test_duplicate_id_is_atomic(self):
        repo = repository(self.conn, self.resource)
        data = sample_for(self.conn, self.resource)
        data['id'] = 'duplicate-record'
        repo.create(data)
        before = repo.count()
        with self.assertRaises(Conflict):
            repo.create(data)
        self.assertEqual(repo.count(), before)

    def test_schema_and_seed_contract(self):
        schema = get_schema(self.resource)
        self.assertEqual(schema['name'], self.resource)
        rows = json.loads((ROOT / 'fixtures' / (self.resource + '.json')).read_text())
        for row in rows:
            self.assertTrue(repository(self.conn, self.resource).get(row['id']))
