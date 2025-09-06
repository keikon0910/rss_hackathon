from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes.index import index_bp   
    from app.routes.home import home_bp

    
    app.register_blueprint(index_bp)
    app.register_blueprint(home_bp)

    return app
