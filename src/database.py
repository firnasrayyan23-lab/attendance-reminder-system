import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "database" / "attendance.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                course_name TEXT NOT NULL,
                day_of_week TEXT NOT NULL,
                start_time TEXT NOT NULL,
                room TEXT DEFAULT '',
                reminder_minutes INTEGER NOT NULL DEFAULT 15
            )
        """)


def add_schedule(chat_id, course_name, day_of_week, start_time, room="", reminder_minutes=15):
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO schedules
               (chat_id, course_name, day_of_week, start_time, room, reminder_minutes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (chat_id, course_name, day_of_week, start_time, room, reminder_minutes),
        )
        return cursor.lastrowid


def get_schedules(chat_id=None):
    with get_connection() as conn:
        if chat_id is None:
            rows = conn.execute("SELECT * FROM schedules ORDER BY id").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM schedules WHERE chat_id = ? ORDER BY id",
                (chat_id,),
            ).fetchall()
        return [dict(row) for row in rows]


def delete_schedule(schedule_id, chat_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM schedules WHERE id = ? AND chat_id = ?",
            (schedule_id, chat_id),
        )
        return cursor.rowcount > 0
