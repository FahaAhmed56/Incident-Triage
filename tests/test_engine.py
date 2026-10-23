import pytest
from src.engine import IncidentMatcher, analyze, load_incidents, normalize, route_ticket

def test_sample_data_loads():
    assert len(load_incidents()) >= 20

def test_normalize():
    assert normalize(' VPN!  LOGIN ') == 'vpn login'

def test_vpn_routes_to_network():
    assert route_ticket('VPN network connection drops')['assignment_group'] == 'Network Support'

def test_password_routes_to_identity():
    assert route_ticket('Password reset needed')['assignment_group'] == 'Identity & Access'

def test_unknown_routes_to_service_desk():
    assert route_ticket('unusual request')['assignment_group'] == 'Service Desk'

def test_exact_text_is_highest_match():
    records = load_incidents()
    matcher = IncidentMatcher(records)
    item = records[0]
    results = matcher.search(item['short_description'], item['description'])
    assert results[0]['number'] == item['number']
    assert results[0]['similarity'] > 0.99

def test_missing_title_fails():
    with pytest.raises(ValueError):
        analyze('  ')

def test_max_results():
    assert len(analyze('vpn disconnected', top_k=2, minimum_score=0)['similar_incidents']) == 2

def test_response_has_disclaimer():
    assert 'human review' in analyze('printer offline')['disclaimer']
