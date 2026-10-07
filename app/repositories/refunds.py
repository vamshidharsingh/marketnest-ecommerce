"""Full-order refunds with stock restoration, applied once."""
from app.repository import Repository

class ResourceRepository(Repository):
    resource = 'refunds'

    def find_by_order_id(self, value):
        """Return exact matches, independent of the paginated UI listing."""
        rows = self.conn.execute('SELECT id FROM records WHERE resource=? ORDER BY id', (self.resource,))
        return [item for row in rows if (item := self.get(row['id']))['order_id'] == value]
