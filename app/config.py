import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get('APP_DB', str(ROOT / 'runtime' / 'app.sqlite3')))
TOKEN = os.environ.get('APP_TOKEN', 'demo-local-token')
HOST = os.environ.get('APP_HOST', '127.0.0.1')
MAX_BODY = 65536
