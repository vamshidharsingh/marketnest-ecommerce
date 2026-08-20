from importlib import import_module
from .schema import get_schema

def repository(conn, resource):
    get_schema(resource)
    return import_module('app.repositories.' + resource).ResourceRepository(conn)
