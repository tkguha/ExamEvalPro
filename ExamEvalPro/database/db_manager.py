import sqlite3
import json
import shutil
from pathlib import Path

DB_PATH = Path(__file__).parent / "exameval.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


# ---------------------------
# INIT DATABASE
# ---------------------------

def init_db():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS examination_profile (
            exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_name TEXT,
            exam_date TEXT,
            venue TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_minutes INTEGER,
            conducting_authority TEXT,
            advertisement_no TEXT,
            question_count INTEGER,
            vacancies INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidate_status (
            exam_id INTEGER,
            serial_no TEXT,
            candidate_name TEXT,
            status TEXT,
            PRIMARY KEY (exam_id, serial_no)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidate_scores (
            exam_id INTEGER,
            serial_no TEXT,
            correct_count INTEGER,
            wrong_count INTEGER,
            blank_count INTEGER,
            multiple_count INTEGER,
            score REAL,
            PRIMARY KEY (exam_id, serial_no)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidate_responses (
            exam_id INTEGER,
            serial_no TEXT,
            responses TEXT,
            PRIMARY KEY (exam_id, serial_no)
        )
    """)

    # ✅ CONFIG TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exam_config (
            exam_id INTEGER PRIMARY KEY,
            mapping TEXT,
            answer_key TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------
# SAVE EXAM
# ---------------------------

def check_exam_exists(name, date):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT exam_id FROM examination_profile
        WHERE exam_name=? AND exam_date=?
    """, (name, date))

    row = cur.fetchone()
    conn.close()

    return row[0] if row else None


def save_exam(profile):

    conn = get_conn()
    cur = conn.cursor()

    existing = check_exam_exists(
        profile["exam_name"],
        profile["exam_date"]
    )

    if existing:
        conn.close()
        return existing, True

    cur.execute("""
        INSERT INTO examination_profile (
            exam_name,
            exam_date,
            venue,
            start_time,
            end_time,
            duration_minutes,
            conducting_authority,
            advertisement_no,
            question_count,
            vacancies
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        profile["exam_name"],
        profile["exam_date"],
        profile["venue"],
        profile["start_time"],
        profile["end_time"],
        profile["duration_minutes"],
        profile["conducting_authority"],
        profile["advertisement_no"],
        profile["question_count"],
        profile["vacancies"]
    ))

    conn.commit()

    exam_id = cur.lastrowid
    conn.close()

    return exam_id, False


# ---------------------------
# CONFIG SAVE / LOAD
# ---------------------------

def save_exam_config(exam_id, mapping, answer_key):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO exam_config (exam_id, mapping, answer_key)
        VALUES (?, ?, ?)
    """, (
        exam_id,
        json.dumps(mapping),
        json.dumps(answer_key)
    ))

    conn.commit()
    conn.close()


def load_exam_config(exam_id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT mapping, answer_key FROM exam_config WHERE exam_id=?
    """, (exam_id,))

    row = cur.fetchone()
    conn.close()

    if row:
        return json.loads(row[0]), json.loads(row[1])

    return None, None


# ---------------------------
# STATUS
# ---------------------------

def save_candidate_status(exam_id, serial_no, name, status):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO candidate_status
        VALUES (?, ?, ?, ?)
    """, (exam_id, serial_no, name, status))

    conn.commit()
    conn.close()


def get_candidate_status(exam_id, serial_no):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT status FROM candidate_status
        WHERE exam_id=? AND serial_no=?
    """, (exam_id, serial_no))

    row = cur.fetchone()
    conn.close()

    return row[0] if row else "Appeared"


# ---------------------------
# RESPONSES
# ---------------------------

def save_candidate_responses(exam_id, serial_no, responses):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO candidate_responses
        VALUES (?, ?, ?)
    """, (exam_id, serial_no, ",".join(responses)))

    conn.commit()
    conn.close()


def get_candidate_responses(exam_id, serial_no):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT responses FROM candidate_responses
        WHERE exam_id=? AND serial_no=?
    """, (exam_id, serial_no))

    row = cur.fetchone()
    conn.close()

    return row[0].split(",") if row else None


# ---------------------------
# SCORES
# ---------------------------

def save_candidate_score(exam_id, serial_no, correct, wrong, blank, multiple, score):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO candidate_scores
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (exam_id, serial_no, correct, wrong, blank, multiple, score))

    conn.commit()
    conn.close()


def get_candidate_score(exam_id, serial_no):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT correct_count, wrong_count, blank_count, multiple_count, score
        FROM candidate_scores
        WHERE exam_id=? AND serial_no=?
    """, (exam_id, serial_no))

    row = cur.fetchone()
    conn.close()

    return row


# ---------------------------
# STATUS COUNTS
# ---------------------------

def get_status_counts(exam_id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT status, COUNT(*)
        FROM candidate_status
        WHERE exam_id=?
        GROUP BY status
    """, (exam_id,))

    rows = cur.fetchall()
    conn.close()

    counts = {
        "Appeared": 0,
        "Not Appeared": 0,
        "Cancelled": 0
    }

    for status, count in rows:
        counts[status] = count

    return counts


# ---------------------------
# EXAM LIST
# ---------------------------

def get_examinations():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT exam_id, exam_name, exam_date
        FROM examination_profile
        ORDER BY exam_id DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return rows


# ---------------------------
# BACKUP / RESTORE
# ---------------------------

def backup_database(save_path):
    shutil.copy(DB_PATH, save_path)


def restore_database(load_path):
    shutil.copy(load_path, DB_PATH)