from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).isoformat()

def record(conn, action, resource, record_id):
    conn.execute('INSERT INTO audit(action,resource,record_id,occurred_at) VALUES(?,?,?,?)', (action, resource, record_id, now()))

def recent(conn, limit=50):
    return [dict(row) for row in conn.execute('SELECT * FROM audit ORDER BY sequence DESC LIMIT ?', (limit,))]
