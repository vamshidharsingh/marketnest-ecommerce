from app.workflows import execute, rows, update
from app.repository import Repository
from app.errors import AppError, Conflict, Forbidden, NotFound
from tests.helpers import DatabaseCase

class WorkflowTests(DatabaseCase):

    def add(self, qty=2):
        return execute(self.conn, 'add_item', dict(cart_id='cart-1', product_id='product-1', quantity=qty))

    def checkout(self, key='checkout-1', coupon='DEMO10'):
        return execute(self.conn, 'checkout', dict(cart_id='cart-1', key=key, coupon_code=coupon))

    def test_cart_aggregates_duplicate_product(self):
        self.add()
        self.add()
        self.assertEqual(len(rows(self.conn, 'cart_items')), 1)
        self.assertEqual(rows(self.conn, 'cart_items')[0]['quantity'], 4)

    def test_checkout_computes_integer_totals(self):
        self.add()
        order = self.checkout()
        self.assertEqual(order['subtotal_cents'], 9800)
        self.assertEqual(order['discount_cents'], 980)
        self.assertEqual(order['total_cents'], 8820)
        self.assertEqual(Repository(self.conn, 'products').get('product-1')['stock'], 18)

    def test_retry_does_not_charge_or_decrement_twice(self):
        self.add()
        first = self.checkout()
        self.assertEqual(first['id'], self.checkout()['id'])
        self.assertEqual(len(rows(self.conn, 'payments')), 1)
        self.assertEqual(Repository(self.conn, 'products').get('product-1')['stock'], 18)

    def test_changed_coupon_on_retry_conflicts(self):
        self.add()
        self.checkout()
        with self.assertRaises(Conflict):
            self.checkout(coupon='')

    def test_stock_rechecked_at_checkout(self):
        self.add()
        product = Repository(self.conn, 'products').get('product-1')
        update(self.conn, 'products', product, stock=1)
        with self.assertRaises(Conflict):
            self.checkout()
        self.assertEqual(rows(self.conn, 'orders'), [])
        self.assertEqual(Repository(self.conn, 'carts').get('cart-1')['status'], 'active')

    def test_invalid_coupon_rolls_back(self):
        self.add()
        with self.assertRaises(Conflict):
            self.checkout(coupon='MISSING')
        self.assertEqual(Repository(self.conn, 'products').get('product-1')['stock'], 20)

    def test_coupon_use_limit_enforced(self):
        self.add()
        coupon = Repository(self.conn, 'coupons').get('coupon-1')
        update(self.conn, 'coupons', coupon, used=50)
        with self.assertRaises(Conflict):
            self.checkout()

    def test_empty_cart_rejected(self):
        with self.assertRaises(AppError):
            self.checkout()

    def test_checked_out_cart_cannot_be_modified(self):
        self.add()
        self.checkout()
        with self.assertRaises(Conflict):
            self.add()

    def test_refund_restores_stock_once(self):
        self.add()
        order = self.checkout()
        payload = dict(order_id=order['id'], reason='Demo return')
        first = execute(self.conn, 'refund', payload)
        second = execute(self.conn, 'refund', payload)
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(Repository(self.conn, 'products').get('product-1')['stock'], 20)
        self.assertEqual(Repository(self.conn, 'orders').get(order['id'])['status'], 'refunded')

    def test_payment_is_explicitly_simulated(self):
        self.add()
        self.checkout()
        self.assertEqual(rows(self.conn, 'payments')[0]['provider'], 'demo')
        self.assertEqual(rows(self.conn, 'payments')[0]['status'], 'simulated')

    def test_invalid_quantities_rejected(self):
        for qty in (0, -1, True, 1.2):
            with self.assertRaises(AppError):
                self.add(qty)

    def test_remove_line_does_not_change_stock(self):
        self.add()
        execute(self.conn, 'remove_item', dict(cart_id='cart-1', product_id='product-1', quantity=2))
        self.assertEqual(rows(self.conn, 'cart_items'), [])
        self.assertEqual(Repository(self.conn, 'products').get('product-1')['stock'], 20)

    def test_operator_can_create_coupon(self):
        coupon = execute(self.conn, 'create_coupon', dict(code='NEW15', percent=15, max_uses=1))
        self.add()
        order = self.checkout(coupon='NEW15')
        self.assertEqual(order['discount_cents'], 1470)
        self.assertEqual(Repository(self.conn, 'coupons').get(coupon['id'])['used'], 1)

    def test_coupon_percentage_bounds(self):
        with self.assertRaises(AppError):
            execute(self.conn, 'create_coupon', dict(code='BAD', percent=101, max_uses=1))
