from app.reports import dashboard
from app.schema import all_schemas
from tests.helpers import DatabaseCase

class ReportTests(DatabaseCase):

    def test_metrics_reflect_seeded_database(self):
        report = dashboard(self.conn)
        self.assertEqual(len(report['metrics']), 4)
        self.assertEqual(set(report['counts']), set(all_schemas()))
        for name, count in report['counts'].items():
            self.assertEqual(count, self.conn.execute('SELECT COUNT(*) FROM records WHERE resource=?', (name,)).fetchone()[0])

    def test_bar_values_are_nonnegative(self):
        for bar in dashboard(self.conn)['bars']:
            self.assertGreaterEqual(bar['value'], 0)
            self.assertGreaterEqual(bar['target'], 0)
