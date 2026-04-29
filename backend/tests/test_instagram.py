from unittest.mock import patch, Mock

def test_invalid_signature_returns_403(client):
    with patch('blueprints.instagram.verify_signature') as mock_verify:
        mock_verify.return_value = False
        
        response = client.post('/instagram', json={})
        
        assert response.status_code == 403

def test_bot_disabled_returns_200(client):
    with patch('blueprints.instagram.verify_signature') as mock_verify, \
         patch('blueprints.instagram.parse_message') as mock_parse, \
         patch('blueprints.instagram.PT') as mock_pt_class, \
         patch('blueprints.instagram.run_agent') as mock_agent:

        mock_verify.return_value = True
        mock_parse.return_value = {
            'sender_id': 'user_123',
            'recipient_id': 'pt_456',
            'message_text': 'Hi'
        }
        mock_pt = Mock()
        mock_pt.bot_enabled = False
        mock_pt_class.query.filter_by.return_value.first.return_value = mock_pt

        response = client.post('/instagram', json={'entry' : []})

        assert response.status_code == 200
        mock_agent.assert_not_called()
        
def test_bot_enabled_returns_200(client):
    with patch('blueprints.instagram.verify_signature') as mock_verify, \
         patch('blueprints.instagram.parse_message') as mock_parse, \
         patch('blueprints.instagram.PT') as mock_pt_class, \
         patch('blueprints.instagram.run_agent') as mock_agent, \
         patch ('blueprints.instagram.send_reply') as mock_reply:

        mock_verify.return_value = True
        mock_parse.return_value = {
            'sender_id': 'user_123',
            'recipient_id': 'pt_456',
            'message_text': 'Hi'
        }
        mock_pt = Mock()
        mock_pt.bot_enabled = True
        mock_pt_class.query.filter_by.return_value.first.return_value = mock_pt
        
        mock_agent.return_value = ('Hello from PTBot!', None)

        response = client.post('/instagram', json={'entry' : []})

        assert response.status_code == 200
        mock_reply.assert_called_once()