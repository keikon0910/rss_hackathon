from flask import Flask

def create_app():
    app = Flask(__name__)

    # Blueprint を import & 登録
    from app.routes.index import index_bp   # ← ここを修正
    app.register_blueprint(index_bp)

    return app
