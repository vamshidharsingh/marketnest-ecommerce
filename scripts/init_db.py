"""Initialize a fresh local database; never overwrite existing records."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connect
from app.seed import seed
from app.config import DB_PATH
if __name__ == '__main__':
    conn = connect()
    created = seed(conn)
    conn.close()
    print('Seeded' if created else 'Already initialized', DB_PATH)
