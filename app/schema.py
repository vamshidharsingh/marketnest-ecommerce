import json
from functools import lru_cache
from .config import ROOT
from .errors import NotFound

@lru_cache(maxsize=1)
def all_schemas():
    return {p.stem: json.loads(p.read_text()) for p in sorted((ROOT / 'schemas').glob('*.json'))}

def get_schema(resource):
    if resource not in all_schemas():
        raise NotFound('Unknown resource')
    return all_schemas()[resource]
