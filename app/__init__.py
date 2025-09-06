import os
from flask import Flask

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config["SECRET_KEY"] = os.getenv("APP_SECRET", "dev")
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")


    # ★ ここを相対importに直す
    from .routes.index import index_bp
    from .routes.home import home_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(home_bp)
    return app
