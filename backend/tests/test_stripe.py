from unittest.mock import patch, Mock
from stripe import SignatureVerificationError

def test_invalid_signature_returns_403(client):
    with patch('blueprints.stripe.stripe.Webhook.construct_event') as mock_event:
    
        mock_event.side_effect = SignatureVerificationError('invalid', 'sig', 'header')

        response = client.post('/stripe', json={'entry': []})

        assert response.status_code == 403
        
def test_subscription_change(client):
    with patch('blueprints.stripe.stripe.Webhook.construct_event') as mock_event, \
    patch('blueprints.stripe.PT') as mock_pt_class:
        
        mock_subscription = Mock()
        mock_subscription.customer = 'cus_123'
        mock_subscription.status = 'active'
        mock_subscription.items.data = [Mock(price=Mock(lookup_key='pro'))]

        mock_event.return_value = {
            'type': 'customer.subscription.updated',
            'id': 'evt_123',
            'data': {
                'object': mock_subscription
            }
        }

        mock_pt = Mock()
        mock_pt.stripe_customer_id = 'cus_123'
        mock_pt_class.query.filter_by.return_value.first.return_value = mock_pt

        response = client.post('/stripe', json={'entry' : []})

        assert response.status_code == 200
        assert mock_pt.subscription_status == 'active'

def test_subscription_deleted(client):
    with patch('blueprints.stripe.stripe.Webhook.construct_event') as mock_event, \
         patch('blueprints.stripe.PT') as mock_pt_class:

        mock_subscription = Mock()
        mock_subscription.customer = 'cus_123'

        mock_event.return_value = {
            'type': 'customer.subscription.deleted',
            'id': 'evt_123',
            'data': {'object': mock_subscription}
        }

        mock_pt = Mock()
        mock_pt_class.query.filter_by.return_value.first.return_value = mock_pt

        response = client.post('/stripe', json={'entry': []})

        assert response.status_code == 200
        assert mock_pt.subscription_status == 'cancelled'


def test_payment_failed(client):
    with patch('blueprints.stripe.stripe.Webhook.construct_event') as mock_event, \
         patch('blueprints.stripe.PT') as mock_pt_class:

        mock_invoice = Mock()
        mock_invoice.customer = 'cus_123'

        mock_event.return_value = {
            'type': 'invoice.payment_failed',
            'id': 'evt_123',
            'data': {'object': mock_invoice}
        }

        mock_pt = Mock()
        mock_pt_class.query.filter_by.return_value.first.return_value = mock_pt

        response = client.post('/stripe', json={'entry': []})

        assert response.status_code == 200
        assert mock_pt.subscription_status == 'past_due'
    
    