from fastapi.testclient import TestClient
from src.main import app
from src.fake_db import db

client = TestClient(app)

db._users.extend([
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
])

def test_get_existed_user():
    '''Получение существующего пользователя'''

    response = client.get("/api/v1/user", params={'email': 'i.i.ivanov@mail.com'})
    assert response.status_code == 200
    assert response.json() == {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    }

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'no.one@mail.com'})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        "name": "Sergey Sergeev",
        "email": "s.sergeev@mail.com"
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    user_id = response.json()
    assert isinstance(user_id, int)
    get_response = client.get("/api/v1/user", params={"email": new_user["email"]})
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Sergey Sergeev"

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_user = {
        "name": "Duplicate",
        "email": "i.i.ivanov@mail.com"
    }
    response = client.post("/api/v1/user", json=existing_user)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}

def test_delete_user():
    '''Удаление пользователя'''
    db.reset()
    email = "p.p.petrov@mail.com"
    response = client.delete("/api/v1/user", params={'email': email})
    assert response.status_code == 204
    response_check = client.get("/api/v1/user", params={'email': email})
    assert response_check.status_code == 404
