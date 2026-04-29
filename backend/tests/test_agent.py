from unittest.mock import patch, Mock

def test_agent_returns_reply(pt):
    with patch('services.agent.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = Mock(
            stop_reason='end_turn',
            content=[Mock(text='Hello from PTBot!', type='text')]
        )

        from services.agent import run_agent
        reply, photo_url = run_agent(
            pt=pt,
            sender_id='user_123',
            message_text='Hi'
        )

        assert reply == 'Hello from PTBot!'
        assert photo_url is None