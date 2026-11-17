import os
import sqlite3
import pytz
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'myproject.db')
DEFAULT_CSV_PATH = os.path.join(BASE_DIR, 'data', 'leaf_data.csv')

SPECIES_LIST = ['은행', '단풍', '벚나무', '감나무', '밤나무', '화살나무']

def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_all_tables():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id_num INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username TEXT NOT NULL,
                    userid TEXT UNIQUE NOT NULL,
                    passwd TEXT NOT NULL,
                    created_at TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id_num INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    userid TEXT NOT NULL,
                    q1 INTEGER, q2 INTEGER, q3 INTEGER, q4 INTEGER, q5 INTEGER,
                    q6 INTEGER, q7 INTEGER, q8 INTEGER, q9 INTEGER, q10 INTEGER,
                    created_at TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS leaf_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    item_name TEXT NOT NULL,
                    species TEXT NOT NULL,
                    width REAL NOT NULL,
                    length REAL NOT NULL,
                    petiole REAL NOT NULL,
                    is_fake INTEGER NOT NULL DEFAULT 0,
                    created_by TEXT NOT NULL DEFAULT '기본데이터',
                    created_at TEXT NOT NULL
                )''')
    c.execute("SELECT COUNT(*) FROM leaf_records")
    if c.fetchone()[0] == 0:
        _seed_default_data(c)
    conn.commit()
    conn.close()

def _seed_default_data(cursor):
    df = pd.read_csv(DEFAULT_CSV_PATH)
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
    rows = []
    for _, r in df.iterrows():
        rows.append((
            str(r['개체명']),
            str(r['종']),
            float(r['가로']),
            float(r['세로']),
            float(r['잎자루']),
            int(bool(r['가짜여부'])),
            '기본데이터',
            now
        ))
    cursor.executemany(
        "INSERT INTO leaf_records (item_name, species, width, length, petiole, is_fake, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows
    )

def get_leaf_df():
    init_all_tables()
    conn = get_conn()
    df = pd.read_sql_query(
        '''SELECT id AS ID,
                  item_name AS 개체명,
                  species AS 종,
                  width AS 가로,
                  length AS 세로,
                  petiole AS 잎자루,
                  is_fake AS 가짜여부,
                  created_by AS 작성자,
                  created_at AS 등록시각
           FROM leaf_records
           ORDER BY id ASC''',
        conn
    )
    conn.close()
    df['가짜여부'] = df['가짜여부'].astype(bool)
    return df

def add_single_leaf(item_name, species, width, length, petiole, created_by, is_fake=False):
    init_all_tables()
    conn = get_conn()
    c = conn.cursor()
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        "INSERT INTO leaf_records (item_name, species, width, length, petiole, is_fake, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (item_name, species, float(width), float(length), float(petiole), int(bool(is_fake)), created_by, now)
    )
    conn.commit()
    conn.close()

def add_bulk_leaves(records_df, created_by):
    init_all_tables()
    conn = get_conn()
    c = conn.cursor()
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
    rows = []
    for _, r in records_df.iterrows():
        rows.append((
            str(r['개체명']),
            str(r['종']),
            float(r['가로']),
            float(r['세로']),
            float(r['잎자루']),
            int(bool(r['가짜여부'])),
            created_by,
            now
        ))
    c.executemany(
        "INSERT INTO leaf_records (item_name, species, width, length, petiole, is_fake, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows
    )
    conn.commit()
    conn.close()

def delete_leaf_by_id(record_id):
    init_all_tables()
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM leaf_records WHERE id = ?", (int(record_id),))
    conn.commit()
    conn.close()

def reset_leaf_db():
    init_all_tables()
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM leaf_records")
    c.execute("DELETE FROM sqlite_sequence WHERE name='leaf_records'")
    _seed_default_data(c)
    conn.commit()
    conn.close()
