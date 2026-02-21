from src.engine.evaluator import PolicyEngine

def test_deny_by_default():
    engine = PolicyEngine({"default_decision": "deny", "rules": []})
    assert engine.evaluate("unknown").decision == "deny"

def test_allow_matching_rule():
    engine = PolicyEngine({"default_decision": "deny", "rules": [{"id": "allow-search", "action": "search", "decision": "allow"}]})
    d = engine.evaluate("search")
    assert d.decision == "allow" and "allow-search" in d.matched_rules

def test_phi_approval():
    engine = PolicyEngine.from_file("policies/examples/healthcare_minimum.json")
    assert engine.evaluate("search", {"data_class": "PHI"}).decision == "require_approval"

def test_budget_deny():
    engine = PolicyEngine.from_file("policies/examples/budget_caps.json")
    assert engine.evaluate("model_inference", {"estimated_cost_usd": 0.75}).decision == "deny"

def test_policy_hash():
    engine = PolicyEngine({"default_decision": "deny", "rules": []})
    assert engine.evaluate("test").policy_hash.startswith("sha256:")
