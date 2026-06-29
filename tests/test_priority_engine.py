from backend.priority_engine import PriorityEngine


def test_priority_engine_outputs_fields():
    engine = PriorityEngine()
    out = engine.calculate_priority(
        {
            "confidence": 90.0,
            "eta": 10,
            "affected_vpns": ["VPN-1"],
            "affected_services": ["VoIP", "POS"],
        }
    )
    assert "priority_score" in out
    assert "severity" in out

