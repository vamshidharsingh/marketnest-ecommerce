"""Export one resource to CSV at a user-selected output path."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connect
from app.export import export_csv
from app.schema import all_schemas
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('resource', choices=sorted(all_schemas()))
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    conn = connect()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(export_csv(conn, args.resource))
    conn.close()
    print(args.output)
