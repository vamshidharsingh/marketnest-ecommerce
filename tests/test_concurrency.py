from concurrent.futures import ThreadPoolExecutor
import threading
from app.db import connect
from app.workflows import execute, rows, update
from app.repository import Repository
from app.errors import Conflict
from tests.helpers import DatabaseCase

class ConcurrencyTests(DatabaseCase):

    def run_parallel(self, tasks):
        barrier = threading.Barrier(len(tasks))

        def worker(task):
            conn = connect(self.db_path)
            try:
                barrier.wait(timeout=5)
                try:
                    execute(conn, task[0], task[1])
                    return 'ok'
                except Conflict:
                    return 'conflict'
            finally:
                conn.close()
        with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
            return list(pool.map(worker, tasks))

    def test_concurrent_commands_preserve_domain_invariant(self):
        product = Repository(self.conn, 'products').get('product-1')
        update(self.conn, 'products', product, stock=1)
        second = execute(self.conn, 'create_cart', dict(customer_id='customer-1'))
        carts = ['cart-1', second['id']]
        for cart in carts:
            execute(self.conn, 'add_item', dict(cart_id=cart, product_id='product-1', quantity=1))
        tasks = [('checkout', dict(cart_id=cart, key='concurrent-' + str(i), coupon_code='')) for i, cart in enumerate(carts)]
        outcomes = self.run_parallel(tasks)
        self.assertEqual(outcomes.count('ok'), 1)
        self.assertEqual(Repository(self.conn, 'products').get('product-1')['stock'], 0)
        self.assertEqual(len(rows(self.conn, 'orders')), 1)
