"""Workflow-managed basket lines with aggregated quantities."""
from app.repository import Repository

class ResourceRepository(Repository):
    resource = 'cart_items'

    def find_by_cart_id(self, value):
        """Return exact matches, independent of the paginated UI listing."""
        rows = self.conn.execute('SELECT id FROM records WHERE resource=? ORDER BY id', (self.resource,))
        return [item for row in rows if (item := self.get(row['id']))['cart_id'] == value]
