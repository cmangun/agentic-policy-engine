from src.engine.evaluator import PolicyEngine

def test_bypass_omit_context():
    engine = PolicyEngine({"default_decision": "deny", "rules": [{"id": "allow-non-phi", "action": "search", "decision": "allow", "conditions": {"data_class": {"not": "PHI"}}}]})
    assert engine.evaluate("search").decision == "deny"

def test_bypass_wrong_case():
    engine = PolicyEngine({"default_decision": "deny", "rules": [{"id": "allow-search", "action": "search", "decision": "allow"}]})
    assert engine.evaluate("SEARCH").decision == "deny"
