import os
import sqlite3

from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "instance", "jobboard.db")
SCHEMA = os.path.join(BASE_DIR, "schema.sql")


def connect():
    """Veritabanına yeni bir bağlantı açar."""
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row             # satırlara sütun adıyla erişebilmek için
    conn.execute("PRAGMA foreign_keys = ON")   # SQLite'ta foreign key kontrolü varsayılan olarak kapalı
    return conn


def get_db():
    """Bu istek için bağlantıyı döndürür; yoksa açar.
    Aynı istek içinde birden fazla sorgu aynı bağlantıyı kullanır."""
    if "db" not in g:
        g.db = connect()
    return g.db


def close_db(exception=None):
    """İstek bitince bağlantıyı kapatır."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """schema.sql dosyasını çalıştırıp tabloları baştan oluşturur."""
    conn = connect()
    with open(SCHEMA, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def database_exists():
    return os.path.exists(DATABASE)