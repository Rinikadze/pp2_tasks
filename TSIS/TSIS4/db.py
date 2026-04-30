"""
db.py - PostgreSQL integration via pg8000 (no encoding issues on Windows)
pip install pg8000
"""

import pg8000.native

DB_HOST     = "localhost"
DB_PORT     = 5432
DB_NAME     = "snake_db"
DB_USER     = "postgres"
DB_PASSWORD = "K0309an++"   # <-- замени на свой пароль


def _connect():
    return pg8000.native.Connection(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db():
    try:
        conn = _connect()
        conn.run("""
            CREATE TABLE IF NOT EXISTS players (
                id       SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            )
        """)
        conn.run("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id            SERIAL PRIMARY KEY,
                player_id     INTEGER REFERENCES players(id),
                score         INTEGER   NOT NULL,
                level_reached INTEGER   NOT NULL,
                played_at     TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.close()
        print("[DB] Tables ready.")
        return True
    except Exception as e:
        print(f"[DB] init_db error: {e}")
        return False


def get_or_create_player(username: str):
    try:
        conn = _connect()
        conn.run(
            "INSERT INTO players (username) VALUES (:u) ON CONFLICT (username) DO NOTHING",
            u=username
        )
        rows = conn.run("SELECT id FROM players WHERE username = :u", u=username)
        conn.close()
        return rows[0][0] if rows else None
    except Exception as e:
        print(f"[DB] get_or_create_player error: {e}")
        return None


def save_result(username: str, score: int, level_reached: int):
    try:
        player_id = get_or_create_player(username)
        if player_id is None:
            print("[DB] save_result: player not found")
            return False
        conn = _connect()
        conn.run(
            "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (:p, :s, :l)",
            p=player_id, s=score, l=level_reached
        )
        conn.close()
        print(f"[DB] Saved: {username} score={score} level={level_reached}")
        return True
    except Exception as e:
        print(f"[DB] save_result error: {e}")
        return False


def get_top10() -> list:
    try:
        conn = _connect()
        rows = conn.run("""
            SELECT p.username, gs.score, gs.level_reached, gs.played_at
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            ORDER BY gs.score DESC
            LIMIT 10
        """)
        conn.close()
        return [
            {"username": r[0], "score": r[1], "level_reached": r[2], "played_at": r[3]}
            for r in rows
        ]
    except Exception as e:
        print(f"[DB] get_top10 error: {e}")
        return []


def get_personal_best(username: str) -> int:
    try:
        conn = _connect()
        rows = conn.run("""
            SELECT MAX(gs.score)
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            WHERE p.username = :u
        """, u=username)
        conn.close()
        return rows[0][0] if rows and rows[0][0] is not None else 0
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0