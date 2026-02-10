import sqlite3
import csv
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data.sqlite3"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS topic_info (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            difficulty INTEGER NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_info (
            id TEXT PRIMARY KEY,
            name TEXT,
            keyboard TEXT,
            language TEXT,
            ide TEXT,
            discord TEXT,
            kattis TEXT,
            timestamp TEXT,
            ip_address TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_responses (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            topic_id INTEGER,
            answer INTEGER,
            timestamp TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS mastery_feedback (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            topic_id TEXT,
            predicted_value REAL,
            feedback_value REAL,
            timestamp TEXT
        )
        """
    )

    conn.commit()

    # If topic_info is empty, try to seed from app/topics.csv
    cur.execute("SELECT COUNT(*) as cnt FROM topic_info")
    cnt = cur.fetchone()["cnt"]
    if cnt == 0:
        topics_csv = Path(__file__).resolve().parent / "topics.csv"
        if topics_csv.exists():
            with open(topics_csv, newline='') as fh:
                reader = csv.DictReader(fh)
                rows = [(i, r["name"].strip(), int(r["difficulty"])) for i, r in enumerate(reader)]
                cur.executemany("INSERT INTO topic_info(id, name, difficulty) VALUES (?, ?, ?)", rows)
                conn.commit()

    conn.close()


def get_topics():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, difficulty FROM topic_info ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_user_info(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO user_info (id, name, keyboard, language, ide, discord, kattis, timestamp, ip_address)
        VALUES (:id, :name, :keyboard, :language, :ide, :discord, :kattis, :timestamp, :ip_address)
        """,
        data,
    )
    conn.commit()
    conn.close()


def insert_quiz_response(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO quiz_responses (id, user_id, topic_id, answer, timestamp)
        VALUES (:id, :user_id, :topic_id, :answer, :timestamp)
        """,
        data,
    )
    conn.commit()
    conn.close()


def insert_mastery_feedback(records: list):
    conn = get_conn()
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT OR REPLACE INTO mastery_feedback (id, user_id, topic_id, predicted_value, feedback_value, timestamp)
        VALUES (:id, :user_id, :topic_id, :predicted_value, :feedback_value, :timestamp)
        """,
        records,
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
