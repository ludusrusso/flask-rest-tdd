# app.py

from flask import Flask
from flask_json import FlaskJSON
from fake_db import FakeDB

def create_app():
    app = Flask(__name__)
    FlaskJSON(app)
    app.db = FakeDB()
    app.config['SECRET_KEY'] = 'secret_ket'

    from main_endpoints import main_bp
    app.register_blueprint(main_bp)

    return app
