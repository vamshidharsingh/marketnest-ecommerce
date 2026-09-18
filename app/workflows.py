"""Transactional domain commands. Generic CRUD never writes derived state."""
import uuid
from datetime import date, datetime, timezone
from .repository import Repository
from .db import transaction
from .errors import AppError, Conflict, Forbidden

def rows(conn, name):
    repo = Repository(conn, name)
    return [repo.get(r['id']) for r in conn.execute('SELECT id FROM records WHERE resource=? ORDER BY id', (name,))]

def find(conn, name, **criteria):
    return next((r for r in rows(conn, name) if all((r.get(k) == v for k, v in criteria.items()))), None)

def update(conn, name, row, **changes):
    data = {k: v for k, v in row.items() if k not in ('id', '_version')}
    data.update(changes)
    return Repository(conn, name).update(row['id'], data, row['_version'])

def positive(value, name='quantity'):
    if type(value) is not int or not 0 < value <= 10 ** 12:
        raise AppError(name + ' must be a positive integer')
    return value

def text(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise AppError(name + ' must be non-empty text (max 200)')
    return value

def execute(conn, action, data):
    if not isinstance(data, dict):
        raise AppError('JSON object required')
    if action not in ACTIONS:
        raise AppError('Unknown workflow')
    with transaction(conn):
        try:
            return ACTIONS[action](conn, data)
        except KeyError as exc:
            raise AppError('Missing workflow field: ' + str(exc.args[0]))

def create_cart(conn, data):
    return Repository(conn, 'carts').create(dict(customer_id=text(data['customer_id'], 'customer_id'), status='active'))

def add_item(conn, data):
    cart = Repository(conn, 'carts').get(text(data['cart_id'], 'cart_id'))
    if cart['status'] != 'active':
        raise Conflict('Cart already checked out')
    product = Repository(conn, 'products').get(text(data['product_id'], 'product_id'))
    quantity = positive(data['quantity'])
    if product['status'] != 'active':
        raise Conflict('Product unavailable')
    line = find(conn, 'cart_items', cart_id=cart['id'], product_id=product['id'])
    total = quantity + (line['quantity'] if line else 0)
    if total > product['stock']:
        raise Conflict('Quantity exceeds current stock')
    if line:
        return update(conn, 'cart_items', line, quantity=total)
    return Repository(conn, 'cart_items').create(dict(cart_id=cart['id'], product_id=product['id'], quantity=total))

def checkout(conn, data):
    cart_id = text(data['cart_id'], 'cart_id')
    key = text(data['key'], 'key')
    code = data.get('coupon_code', '')
    if not isinstance(code, str):
        raise AppError('coupon_code must be text')
    prior = find(conn, 'orders', key=key)
    if prior:
        if prior['cart_id'] != cart_id:
            raise Conflict('Idempotency key reused with different cart')
        stored = conn.execute('SELECT fingerprint FROM checkout_requests WHERE key=?', (key,)).fetchone()
        if not stored or stored[0] != code:
            raise Conflict('Idempotency key reused with different coupon')
        return prior
    cart = Repository(conn, 'carts').get(cart_id)
    if cart['status'] != 'active':
        raise Conflict('Cart already checked out')
    lines = [r for r in rows(conn, 'cart_items') if r['cart_id'] == cart_id]
    if not lines:
        raise AppError('Cart is empty')
    products = {r['product_id']: Repository(conn, 'products').get(r['product_id']) for r in lines}
    for line in lines:
        product = products[line['product_id']]
        if product['status'] != 'active' or product['stock'] < line['quantity']:
            raise Conflict('Product unavailable or insufficient stock')
    subtotal = sum((products[r['product_id']]['price_cents'] * r['quantity'] for r in lines))
    discount = 0
    coupon = None
    if code:
        coupon = find(conn, 'coupons', code=code)
        if not coupon or coupon['status'] != 'active' or coupon['used'] >= coupon['max_uses']:
            raise Conflict('Coupon unavailable')
        discount = subtotal * coupon['percent'] // 100
    order = Repository(conn, 'orders').create(dict(customer_id=cart['customer_id'], cart_id=cart_id, subtotal_cents=subtotal, discount_cents=discount, total_cents=subtotal - discount, status='placed', key=key))
    conn.execute('INSERT INTO checkout_requests VALUES(?,?)', (key, code))
    for line in lines:
        product = products[line['product_id']]
        update(conn, 'products', product, stock=product['stock'] - line['quantity'])
        Repository(conn, 'order_items').create(dict(order_id=order['id'], product_id=product['id'], quantity=line['quantity'], unit_price_cents=product['price_cents']))
    if coupon:
        update(conn, 'coupons', coupon, used=coupon['used'] + 1)
    update(conn, 'carts', cart, status='checked_out')
    Repository(conn, 'payments').create(dict(order_id=order['id'], amount_cents=order['total_cents'], status='simulated', provider='demo'))
    return order

def refund(conn, data):
    order = Repository(conn, 'orders').get(text(data['order_id'], 'order_id'))
    reason = text(data['reason'], 'reason')
    prior = find(conn, 'refunds', order_id=order['id'])
    if prior:
        return prior
    if order['status'] != 'placed':
        raise Conflict('Order cannot be refunded')
    event = Repository(conn, 'refunds').create(dict(order_id=order['id'], amount_cents=order['total_cents'], reason=reason))
    for line in rows(conn, 'order_items'):
        if line['order_id'] == order['id']:
            product = Repository(conn, 'products').get(line['product_id'])
            update(conn, 'products', product, stock=product['stock'] + line['quantity'])
    update(conn, 'orders', order, status='refunded')
    payment = find(conn, 'payments', order_id=order['id'])
    update(conn, 'payments', payment, status='refunded')
    return event
ACTIONS = {'create_cart': create_cart, 'add_item': add_item, 'checkout': checkout, 'refund': refund}

def create_coupon(conn, data):
    percent = data['percent']
    if type(percent) is not int or not 0 <= percent <= 100:
        raise AppError('Percent must be an integer from 0 to 100')
    return Repository(conn, 'coupons').create(dict(code=text(data['code'], 'code'), percent=percent, max_uses=positive(data['max_uses'], 'max_uses'), used=0, status='active'))

def remove_item(conn, data):
    cart = Repository(conn, 'carts').get(text(data['cart_id'], 'cart_id'))
    if cart['status'] != 'active':
        raise Conflict('Cart already checked out')
    product_id = text(data['product_id'], 'product_id')
    quantity = positive(data['quantity'])
    line = find(conn, 'cart_items', cart_id=cart['id'], product_id=product_id)
    if not line or line['quantity'] < quantity:
        raise Conflict('Requested quantity is not in cart')
    remaining = line['quantity'] - quantity
    if remaining:
        return update(conn, 'cart_items', line, quantity=remaining)
    Repository(conn, 'cart_items').delete(line['id'], line['_version'])
    return dict(removed=line['id'], remaining=0)
ACTIONS.update(create_coupon=create_coupon, remove_item=remove_item)
