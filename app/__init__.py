import os
from flask import Flask

def create_app():
    app = Flask(
        __name__,
        static_folder="../static",
        static_url_path="/static"
    )
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    from .routes.index import index_bp
    from .routes.home import home_bp
    from .routes.photograph import photograph_bp
    from .routes.personal_page import personal_page_bp
    from .routes.subfunction import subfunction_bp
    from .routes.others import others_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(photograph_bp)
    app.register_blueprint(personal_page_bp)
    app.register_blueprint(subfunction_bp)
    app.register_blueprint(others_bp)

    return app

# グローバル app を使いたいなら↓もOK
app = create_app()
