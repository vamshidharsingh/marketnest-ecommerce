import mimetypes
from pathlib import Path
from urllib.parse import unquote
from .config import ROOT
from .errors import NotFound

def static_file(url):
    base = (ROOT / 'web').resolve()
    target = (base / (unquote(url).lstrip('/') or 'index.html')).resolve()
    if not target.is_relative_to(base) or not target.is_file():
        raise NotFound('Asset not found')
    content_type = mimetypes.guess_type(str(target))[0] or 'application/octet-stream'
    if target.suffix == '.js':
        content_type = 'text/javascript'
    return (target.read_bytes(), content_type)
