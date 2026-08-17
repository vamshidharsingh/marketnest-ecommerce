"""Use SQLite backup API for a consistent snapshot, including WAL contents."""
import argparse, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import DB_PATH
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    if not DB_PATH.is_file():
        parser.error('Initialize the local database first')
    if args.destination.resolve() == DB_PATH.resolve():
        parser.error('Destination must differ from source')
    if args.destination.exists():
        parser.error('Destination already exists; choose a new backup path')
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(DB_PATH)
    target = sqlite3.connect(args.destination)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    print(args.destination)
