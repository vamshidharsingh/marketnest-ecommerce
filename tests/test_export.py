import csv, io
from app.export import export_csv
from app.repository import Repository
from app.schema import all_schemas
from tests.helpers import DatabaseCase, sample_for

class ExportTests(DatabaseCase):

    def test_export_has_all_rows_and_schema_headers(self):
        for name, schema in all_schemas().items():
            reader = csv.DictReader(io.StringIO(export_csv(self.conn, name)))
            self.assertEqual(set(reader.fieldnames), {'id', '_version', *schema['fields']})
            self.assertEqual(len(list(reader)), Repository(self.conn, name).count())

    def test_spreadsheet_formula_is_neutralized(self):
        name = next((n for n, s in all_schemas().items() if any((r['type'] == 'string' and (not any((k in r for k in ('ref', 'enum', 'format', 'pattern', 'maxLength')))) for r in s['fields'].values()))))
        data = sample_for(self.conn, name)
        key = next((k for k, r in all_schemas()[name]['fields'].items() if r['type'] == 'string' and (not any((n in r for n in ('ref', 'enum', 'format', 'pattern', 'maxLength'))))))
        data[key] = '=DEMO()'
        row = Repository(self.conn, name).create(data)
        exported = next((r for r in csv.DictReader(io.StringIO(export_csv(self.conn, name))) if r['id'] == row['id']))
        self.assertEqual(exported[key], "'=DEMO()")
