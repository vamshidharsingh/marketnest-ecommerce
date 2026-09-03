"""Human-managed order fulfillment records."""
from app.repository import Repository

class ResourceRepository(Repository):
    resource = 'fulfillments'

    def find_by_reference(self, value):
        """Return exact matches, independent of the paginated UI listing."""
        rows = self.conn.execute('SELECT id FROM records WHERE resource=? ORDER BY id', (self.resource,))
        return [item for row in rows if (item := self.get(row['id']))['reference'] == value]
