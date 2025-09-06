# app/db.py
import os
import psycopg2
import psycopg2.pool

_pool: psycopg2.pool.SimpleConnectionPool | None = None

def init_db_pool(dsn: str | None = None) -> None:
    """環境変数 DATABASE_URL からコネクションプールを初期化"""
    global _pool
    if _pool is not None:
        return
    if dsn is None:
        dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is not set")
    _pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=5, dsn=dsn)

def get_conn():
    """プールから接続を1つ借りる（未初期化なら初期化）"""
    global _pool
    if _pool is None:
        init_db_pool()
    return _pool.getconn()

def put_conn(conn) -> None:
    """借りた接続をプールに返す"""
    if _pool is not None and conn is not None:
        _pool.putconn(conn)

def close_pool() -> None:
    """アプリ終了時にプールを閉じたい場合用（任意）"""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
