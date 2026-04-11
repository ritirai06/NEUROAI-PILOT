import sqlite3, json, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "memory", "agent_memory.db")


class Memory:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._init_db()

    def _conn(self):
        return sqlite3.connect(DB_PATH)

    def _init_db(self):
        with self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, input TEXT, plan TEXT, results TEXT
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY, value TEXT
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS context (
                key TEXT PRIMARY KEY, value TEXT, updated TEXT
            )""")

    def save(self, user_input: str, plan: dict, results: dict):
        with self._conn() as c:
            c.execute("INSERT INTO history (timestamp,input,plan,results) VALUES (?,?,?,?)",
                (datetime.now().isoformat(), user_input,
                 json.dumps(plan), json.dumps(results)))

    def get_history(self, limit: int = 50) -> list:
        with self._conn() as c:
            rows = c.execute(
                "SELECT id,timestamp,input,plan,results FROM history ORDER BY id DESC LIMIT ?",
                (limit,)).fetchall()
        return [{"id":r[0],"timestamp":r[1],"input":r[2],
                 "plan":json.loads(r[3]),"results":json.loads(r[4])} for r in rows]

    def get_recent(self, n: int = 3) -> list:
        with self._conn() as c:
            rows = c.execute(
                "SELECT input FROM history ORDER BY id DESC LIMIT ?", (n,)).fetchall()
        return [{"input": r[0]} for r in rows]

    def set_context(self, key: str, value: str):
        with self._conn() as c:
            c.execute("INSERT OR REPLACE INTO context (key,value,updated) VALUES (?,?,?)",
                (key, value, datetime.now().isoformat()))

    def get_context(self, key: str) -> str | None:
        with self._conn() as c:
            r = c.execute("SELECT value FROM context WHERE key=?", (key,)).fetchone()
        return r[0] if r else None

    def set_preference(self, key: str, value: str):
        with self._conn() as c:
            c.execute("INSERT OR REPLACE INTO preferences (key,value) VALUES (?,?)", (key, value))

    def get_preference(self, key: str, default: str = None) -> str:
        with self._conn() as c:
            r = c.execute("SELECT value FROM preferences WHERE key=?", (key,)).fetchone()
        return r[0] if r else default

    def clear(self):
        with self._conn() as c:
            c.execute("DELETE FROM history")
