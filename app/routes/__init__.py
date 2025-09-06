from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes.index import index_bp   
    from app.routes.home import home_bp
    from app.routes.photograph import photograph_bp
    from app.routes.personal_page import personal_page_bp

    
    app.register_blueprint(index_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(photograph_bp)
    app.register_blueprint(personal_page_bp)

    return app
