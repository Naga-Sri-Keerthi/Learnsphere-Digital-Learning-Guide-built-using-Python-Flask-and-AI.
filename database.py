import sqlite3
from datetime import datetime


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_NAME = "learnsphere.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_conn():

    conn = sqlite3.connect(DB_NAME)

    # Allows us to access columns by name
    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():

    conn = get_conn()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS progress (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic TEXT NOT NULL,

            progress INTEGER DEFAULT 0,

            completed INTEGER DEFAULT 0,

            quiz_score INTEGER DEFAULT 0,

            quiz_total INTEGER DEFAULT 0,

            quiz_percentage INTEGER DEFAULT 0,

            created_at TEXT NOT NULL

        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# SAVE / UPDATE LEARNING PROGRESS
# ============================================================

def save_progress(topic, percentage=0, completed=False):

    if not topic:
        return

    # Keep percentage between 0 and 100
    progress_value = max(
        0,
        min(100, int(percentage))
    )

    conn = get_conn()

    existing = conn.execute(
        """
        SELECT id
        FROM progress
        WHERE topic = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (topic,)
    ).fetchone()

    now = datetime.now().isoformat(
        timespec="seconds"
    )


    if existing:

        conn.execute(
            """
            UPDATE progress

            SET
                progress = ?,
                completed = ?,
                created_at = ?

            WHERE id = ?
            """,
            (
                progress_value,
                int(completed),
                now,
                existing["id"]
            )
        )

    else:

        conn.execute(
            """
            INSERT INTO progress
            (
                topic,
                progress,
                completed,
                quiz_score,
                quiz_total,
                quiz_percentage,
                created_at
            )

            VALUES (?, ?, ?, 0, 0, 0, ?)
            """,
            (
                topic,
                progress_value,
                int(completed),
                now
            )
        )


    conn.commit()
    conn.close()


# ============================================================
# SAVE QUIZ RESULT
# ============================================================

def save_quiz_result(
    topic,
    score,
    total,
    percentage
):

    if not topic:
        return

    # Make sure values are valid
    score = int(score)
    total = int(total)
    percentage = max(
        0,
        min(100, int(percentage))
    )

    conn = get_conn()

    now = datetime.now().isoformat(
        timespec="seconds"
    )


    # Check whether this topic already has progress
    existing = conn.execute(
        """
        SELECT id
        FROM progress
        WHERE topic = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (topic,)
    ).fetchone()


    if existing:

        conn.execute(
            """
            UPDATE progress

            SET
                progress = ?,
                completed = 1,
                quiz_score = ?,
                quiz_total = ?,
                quiz_percentage = ?,
                created_at = ?

            WHERE id = ?
            """,
            (
                percentage,
                score,
                total,
                percentage,
                now,
                existing["id"]
            )
        )

    else:

        conn.execute(
            """
            INSERT INTO progress
            (
                topic,
                progress,
                completed,
                quiz_score,
                quiz_total,
                quiz_percentage,
                created_at
            )

            VALUES (?, ?, 1, ?, ?, ?, ?)
            """,
            (
                topic,
                percentage,
                score,
                total,
                percentage,
                now
            )
        )


    conn.commit()
    conn.close()


# ============================================================
# GET PROGRESS FOR ONE TOPIC
# ============================================================

def get_topic_progress(topic):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT *
        FROM progress
        WHERE topic = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (topic,)
    ).fetchone()

    conn.close()


    if row:

        return dict(row)


    # Default progress if topic has not been studied yet
    return {
        "topic": topic,
        "progress": 0,
        "completed": 0,
        "quiz_score": 0,
        "quiz_total": 0,
        "quiz_percentage": 0,
        "created_at": ""
    }


# ============================================================
# GET ALL PROGRESS
# ============================================================

def get_progress(topic=None):

    conn = get_conn()


    # --------------------------------------------------------
    # ONE TOPIC
    # --------------------------------------------------------

    if topic:

        row = conn.execute(
            """
            SELECT *
            FROM progress
            WHERE topic = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (topic,)
        ).fetchone()

        conn.close()


        if row:

            return dict(row)


        return {
            "topic": topic,
            "progress": 0,
            "completed": 0,
            "quiz_score": 0,
            "quiz_total": 0,
            "quiz_percentage": 0,
            "created_at": ""
        }


    # --------------------------------------------------------
    # ALL TOPICS
    # --------------------------------------------------------

    rows = conn.execute(
        """
        SELECT *
        FROM progress
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()


    return [
        dict(row)
        for row in rows
    ]