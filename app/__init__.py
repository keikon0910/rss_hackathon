import os
from flask import Flask

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",  # ← app/ と同階層の templates/
        static_folder="../static",      # ← app/ と同階層の static/
    )

    app.config["SECRET_KEY"] = os.getenv("APP_SECRET", "dev")
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")


    from .routes.home import home_bp
    # index は今は登録しない（A案でオフにしている想定）
    app.register_blueprint(home_bp)

    return app
