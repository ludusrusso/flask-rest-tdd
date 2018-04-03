import pytest
from app import create_app
from app import FakeDB

from flask import Flask, Response as BaseResponse, json
from flask.testing import FlaskClient
from werkzeug.utils import cached_property
import jwt

@pytest.fixture
def app():
    class Response(BaseResponse):
        @cached_property
        def json(self):
            return json.loads(self.data)


    class TestClient(FlaskClient):
        def open(self, *args, **kwargs):
            if 'json' in kwargs:
                kwargs['data'] = json.dumps(kwargs.pop('json'))
                kwargs['content_type'] = 'application/json'
            return super(TestClient, self).open(*args, **kwargs)

    app = create_app()
    app.response_class = Response
    app.test_client_class = TestClient
    app.testing = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db():
    return FakeDB()

def test_app_runs(client):
    res = client.get('/')
    assert res.status_code == 200

def test_app_returns_json(client):
    res = client.get('/')
    assert res.headers['Content-Type'] == 'application/json'

def test_db_get_user(db):
    db.add_user("test@test.com", "password", {"name": "test"})
    user = db.get_user("test@test.com")
    assert user["username"] == "test@test.com"
    assert user["name"] == "test"

def test_db_get_not_known_user(db):
    with pytest.raises(KeyError):
        user = db.get_user("nouser@test.com")

def test_db_password_check(db):
    db.add_user("test@test.com", "password", {"name": "test"})
    assert db.check_user("test@test.com", "password") == True
    assert db.check_user("test@test.com", "wrong") == False

def test_invalid_login(client):
    res = client.post('/login', json={'username': 'nouser', 'password': 'no password'})
    assert res.status_code == 401
    assert res.json['error'] == 'invalid login'

def test_correct_login(client, app):
    username = "test@test.com"
    password =  "password"
    app.db.add_user(username, password, {"name": "test"})
    res = client.post('/login', json={'username': username, 'password': password})
    assert res.status_code == 200
    assert "access_token" in res.json
    token = res.json["access_token"]
    data = jwt.decode(token, verify=False)
    assert data['username'] == username

def test_unauthorized_request_to_protected(client, app):
    res = client.get('/protected')
    assert res.status_code == 401

def test_invalid_token_request_to_protected(client, app):
    invalid_token = '12345'
    headers = {
        'Authorization': 'Bearer {}'.format(invalid_token)
    }
    res = client.get('/protected', headers=headers)
    print(res.json)
    assert res.status_code == 401

def test_valid_token_request_to_protected(client, app):
    valid_token = jwt.encode({'username':'username'}, app.config['SECRET_KEY']).decode('utf-8')
    headers = {
        'Authorization': 'Bearer {}'.format(valid_token)
    }

    res = client.get('/protected', headers=headers)
    print(res.json)
    assert res.status_code == 200