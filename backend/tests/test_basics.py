from unittest.mock import patch, Mock

def test_addition():
    result = 1 + 1
    assert result == 2
    
def test_string():
    name = "PTBot"
    assert name.startswith("PT")
    
def test_pt_has_name(sample_pt):
    assert sample_pt['name'] == 'Tom Holman'
    
def test_pt_is_enabled(sample_pt):
    assert sample_pt['bot_enabled'] is True

def test_mock_example():
    with patch('os.getcwd') as mock_getcwd:
        mock_getcwd.return_value = '/fake/directory'
        import os
        result = os.getcwd()
        assert result == '/fake/directory'
        mock_getcwd.assert_called_once()
    