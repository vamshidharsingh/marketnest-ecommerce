import hmac
from .errors import Unauthorized

def authorize(headers, token):
    supplied = headers.get('Authorization', '')
    if not token or not hmac.compare_digest(supplied, 'Bearer ' + token):
        raise Unauthorized('Valid local operator token required')
