# from flask import Flask

# def create_app():
#     app = Flask(__name__)

#     from app.routes.index import index_bp   
#     from app.routes.home import home_bp
#     from app.routes.photograph import photograph_bp
#     from app.routes.personal_page import personal_page_bp

#     app.register_blueprint(index_bp)
#     app.register_blueprint(home_bp)
#     app.register_blueprint(photograph_bp)
#     app.register_blueprint(personal_page_bp)

#     return app


# Flask は import しない！アプリも作らない！
from .index import index_bp
from .home import home_bp
from .photograph import photograph_bp
from .personal_page import personal_page_bp
from .subfunction import subfunction_bp
from .others import others_bp

__all__ = [
    "index_bp",
    "home_bp",
    "photograph_bp",
    "personal_page_bp",
    "subfunction_bp",
    "others_bp"
]
