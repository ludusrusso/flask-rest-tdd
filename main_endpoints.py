# main_endpoints.py

from flask import current_app as app
from flask import Blueprint, request
from flask_json import as_json
import jwt

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
@as_json
def main():
    return {}

@main_bp.route('/login', methods=['POST'])
@as_json
def login():
    try:
        username = request.get_json()['username']
        password = request.get_json()['password']
        if app.db.check_user(username, password):
            token = jwt.encode({'username':username}, app.config['SECRET_KEY']).decode('utf-8')
            return {'access_token': token}
        else:
            return {'error': 'invalid login'}, 401
    except KeyError:
        return {'error': 'invalid login'}, 401

@main_bp.route('/protected')
@as_json
def protected():
    try:
        auth = request.headers['Authorization'].split()
    except KeyError:
        return {}, 401

    if len(auth) != 2 or auth[0] != 'Bearer':
        return {}, 401
    
    token =  auth[1]
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'])
    except jwt.exceptions.DecodeError:
        return {}, 401
    return data, 200
