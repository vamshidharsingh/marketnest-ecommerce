from .errors import AppError

def pagination(query):
    try:
        limit = int(query.get('limit', ['50'])[0])
        offset = int(query.get('offset', ['0'])[0])
    except (ValueError, TypeError):
        raise AppError('Invalid pagination')
    if not 1 <= limit <= 200 or offset < 0:
        raise AppError('Pagination out of range')
    return (limit, offset)
