import math, re
from datetime import date, datetime
from .errors import AppError

def validate(schema, data):
    if not isinstance(data, dict):
        raise AppError('JSON object required')
    fields = schema['fields']
    unknown = set(data) - set(fields) - {'id'}
    if unknown:
        raise AppError('Unknown fields: ' + ', '.join(sorted(unknown)))
    if 'id' in data and (not isinstance(data['id'], str) or not re.fullmatch('[A-Za-z0-9_-]{1,80}', data['id'])):
        raise AppError('Invalid record id')
    result = {}
    for name, rule in fields.items():
        if name not in data:
            raise AppError(f'Missing field: {name}')
        value = data[name]
        kind = rule['type']
        valid = kind == 'string' and isinstance(value, str) or (kind == 'integer' and type(value) is int) or (kind == 'number' and type(value) in (int, float) and math.isfinite(value))
        if not valid:
            raise AppError(f'{name}: expected {kind}')
        if kind == 'string':
            if len(value.strip()) < rule.get('minLength', 1) or len(value) > rule.get('maxLength', 1000):
                raise AppError(f'{name}: invalid length')
            if 'pattern' in rule and (not re.fullmatch(rule['pattern'], value)):
                raise AppError(f'{name}: invalid format')
            try:
                if rule.get('format') == 'email' and (not re.fullmatch('[^\\s@]+@[^\\s@]+\\.[^\\s@]+', value)):
                    raise ValueError()
                if rule.get('format') == 'date':
                    if len(value) != 10:
                        raise ValueError()
                    date.fromisoformat(value)
                if rule.get('format') == 'datetime':
                    dt = datetime.fromisoformat(value)
                    if dt.tzinfo is None:
                        raise ValueError()
            except ValueError:
                raise AppError(f"{name}: invalid {rule.get('format')}")
        elif value < rule.get('minimum', -10 ** 18) or value > rule.get('maximum', 10 ** 15):
            raise AppError(f'{name}: out of range')
        if 'enum' in rule and value not in rule['enum']:
            raise AppError(f'{name}: invalid choice')
        result[name] = value
    return result
