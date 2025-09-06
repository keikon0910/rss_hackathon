# app/db.py
import os
import psycopg2
import psycopg2.pool

_pool = None  # type: psycopg2.pool.SimpleConnectionPool | None

def init_db_pool(dsn: str | None = None) -> None:
    """
    互換API。環境変数DATABASE_URLまたは引数dsnからコネクションプールを初期化。
    create_app() から呼ばれる前提。
    """
    global _pool
    if _pool is not None:
        return
    if dsn is None:
        dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is not set")
    _pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=5, dsn=dsn)

def get_conn():
    global _pool
    if _pool is None:
        init_db_pool()
    return _pool.getconn()

def put_conn(conn) -> None:
    if _pool is not None and conn is not None:
        _pool.putconn(conn)

def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None