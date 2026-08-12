from .workflows import rows
from .schema import all_schemas
from .repository import Repository

def dashboard(conn):
    counts = {name: Repository(conn, name).count() for name in all_schemas()}
    orders = rows(conn, 'orders')
    products = rows(conn, 'products')
    return dict(counts=counts, metrics=[dict(label='Net placed sales (cents)', value=sum((r['total_cents'] for r in orders if r['status'] == 'placed'))), dict(label='Placed orders', value=sum((r['status'] == 'placed' for r in orders))), dict(label='Available units', value=sum((r['stock'] for r in products))), dict(label='Simulated refunds', value=counts['refunds'])], bars=[dict(label=p['name'], value=p['stock'], target=max((r['stock'] for r in products), default=1) or 1) for p in products])
