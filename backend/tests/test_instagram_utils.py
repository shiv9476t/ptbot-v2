from services.channels.instagram import verify_signature, parse_message
import hashlib
import hmac
import os

def test_no_sha56_in_signature():
    response = verify_signature(123, "123")
    assert response is False
    
def test_valid_signature():
    raw_body = b'hello'
    os.environ['META_INSTAGRAM_APP_SECRET'] = 'test_secret'
    secret = os.environ["META_INSTAGRAM_APP_SECRET"].strip().encode()
    expected = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
    response = verify_signature(b'hello', f'sha256={expected}')
    assert response is True
    
def test_invalid_signature():
    raw_body = b'hello'
    os.environ['META_INSTAGRAM_APP_SECRET'] = 'test_secret'
    response = verify_signature(raw_body, 'sha256=123')
    assert response is False
    
def test_parse_message_malinformed():
    value = parse_message({"missing_key" : 0})
    assert value is None
    
def test_parse_message_valid():
    payload = {
        'entry': [{
            'messaging': [{
                'sender': {'id': 'user_123'},
                'recipient': {'id': 'pt_456'},
                'message': {'text': 'Hi there'}
            }]
        }]
    }
    result = parse_message(payload)
    assert result == {
        'sender_id': 'user_123',
        'recipient_id': 'pt_456',
        'message_text': 'Hi there'
    }

def test_parse_message_no_message():
    payload = {
        'entry': [{
            'messaging': [{
                'sender': {'id': 'user_123'},
                'recipient': {'id': 'pt_456'}
            }]
        }]
    }
    assert parse_message(payload) is None

def test_parse_message_no_text():
    payload = {
        'entry': [{
            'messaging': [{
                'sender': {'id': 'user_123'},
                'recipient': {'id': 'pt_456'},
                'message': {'attachments': []}
            }]
        }]
    }
    assert parse_message(payload) is None

def test_parse_message_echo():
    payload = {
        'entry': [{
            'messaging': [{
                'sender': {'id': 'user_123'},
                'recipient': {'id': 'pt_456'},
                'message': {'text': 'Hi', 'is_echo': True}
            }]
        }]
    }
    assert parse_message(payload) is None
