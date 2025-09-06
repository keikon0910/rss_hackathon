# app/__init__.py
import os
from flask import Flask

# DB接続ヘルパーを別ファイルに作っているならここで import
try:
    from .db import init_db_pool
except ImportError:
    init_db_pool = None


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static",
    )

    # 基本設定
    app.config["SECRET_KEY"] = os.getenv("APP_SECRET", "dev")
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL", "")

    # DBプールの初期化（あるなら）
    if init_db_pool and app.config["DATABASE_URL"]:
        init_db_pool(app.config["DATABASE_URL"])

    # ---- Blueprint 登録 ----
    from .routes.index import index_bp
    from .routes.home import home_bp
    from .routes.personal_page import personal_page_bp  # ← これだけでOK

    app.register_blueprint(index_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(personal_page_bp)

    return app
