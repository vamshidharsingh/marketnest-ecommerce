import argparse, logging
from .config import HOST, TOKEN
from .project import PROJECT
from .db import connect
from .seed import seed
from .http import create_server

def main():
    parser = argparse.ArgumentParser(description=PROJECT['title'] + ' local demo')
    parser.add_argument('--port', type=int, default=PROJECT['port'])
    parser.add_argument('--host', choices=('127.0.0.1', '0.0.0.0'), default=HOST)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Port must be 1 to 65535')
    if args.host != '127.0.0.1' and TOKEN == 'demo-local-token':
        parser.error('A custom APP_TOKEN is required for container binding')
    conn = connect()
    seed(conn)
    conn.close()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    server = create_server(args.port, token=TOKEN, host=args.host)
    print(f"{PROJECT['title']} ready at http://127.0.0.1:{args.port}", flush=True)
    print('Open Access token and enter your APP_TOKEN (default: demo-local-token).', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
if __name__ == '__main__':
    main()
