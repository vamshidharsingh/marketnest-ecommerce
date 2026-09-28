"""Reference tax rates in basis points; checkout excludes tax in this version."""
from app.repository import Repository

class ResourceRepository(Repository):
    resource = 'tax_rules'

    def find_by_region(self, value):
        """Return exact matches, independent of the paginated UI listing."""
        rows = self.conn.execute('SELECT id FROM records WHERE resource=? ORDER BY id', (self.resource,))
        return [item for row in rows if (item := self.get(row['id']))['region'] == value]
