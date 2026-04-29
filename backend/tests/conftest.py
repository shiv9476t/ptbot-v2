import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extensions import db as _db
from models.pt import PT

from app import create_app


@pytest.fixture
def sample_pt():
    return {
        'id' : 1,
        'name' : 'Tom Holman',
        'bot_enabled' : True,
    }

@pytest.fixture
def client():
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['ANTHROPIC_API_KEY'] = 'test_key'
    app = create_app()
    with app.test_client() as client:
        yield client
        
@pytest.fixture
def db(client):
    with client.application.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()
        
@pytest.fixture
def pt(db):
    pt = PT(
        clerk_user_id='test_clerk_id',
        email='tom@test.com',
        name='Tom Holman',
        instagram_account_id='pt_456',
        instagram_token='fake_token',
        slug='tom-holman',
        bot_enabled=True,
    )
    _db.session.add(pt)
    _db.session.commit()
    return pt