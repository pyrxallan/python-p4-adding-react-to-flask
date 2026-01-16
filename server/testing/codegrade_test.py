
import pytest
from app import app
from models import db, Message

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_get_messages(client):
    # Create some test messages
    message1 = Message(username="Alice", body="Hello")
    message2 = Message(username="Bob", body="Hi there")
    db.session.add_all([message1, message2])
    db.session.commit()

    response = client.get('/messages')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['username'] == "Alice"
    assert data[0]['body'] == "Hello"
    assert data[1]['username'] == "Bob"
    assert data[1]['body'] == "Hi there"

def test_post_message(client):
    new_message = {"username": "Charlie", "body": "New message"}
    response = client.post('/messages', json=new_message)
    assert response.status_code == 201
    data = response.get_json()
    assert data['username'] == "Charlie"
    assert data['body'] == "New message"
    assert 'id' in data
    assert 'created_at' in data

def test_patch_message(client):
    message = Message(username="Dave", body="Original")
    db.session.add(message)
    db.session.commit()

    update_data = {"body": "Updated"}
    response = client.patch(f'/messages/{message.id}', json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['body'] == "Updated"
    assert data['username'] == "Dave"

def test_delete_message(client):
    message = Message(username="Eve", body="To delete")
    db.session.add(message)
    db.session.commit()

    response = client.delete(f'/messages/{message.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['deleted'] == True

    # Verify it's deleted
    response = client.get('/messages')
    data = response.get_json()
    assert len(data) == 0
