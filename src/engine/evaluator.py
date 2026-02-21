"""Policy evaluation engine with deny-by-default posture."""
import hashlib, json, uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

@dataclass
class Decision:
    decision_id: str
    action: str
    decision: str
    reason: str
    matched_rules: list[str]
    policy_hash: str
    timestamp: str

    def to_receipt(self) -> dict:
        return {"decision_id": self.decision_id, "action": self.action, "decision": self.decision, "reason": self.reason, "matched_rules": self.matched_rules, "policy_hash": self.policy_hash, "timestamp": self.timestamp}

class PolicyEngine:
    def __init__(self, policy: dict):
        self.policy = policy
        self.policy_hash = self._compute_hash(policy)
        self.default_decision = policy.get("default_decision", "deny")
        self.rules = policy.get("rules", [])

    @classmethod
    def from_file(cls, path: str | Path) -> "PolicyEngine":
        with open(path) as f:
            return cls(json.load(f))

    def evaluate(self, action: str, context: dict[str, Any] | None = None) -> Decision:
        context = context or {}
        for rule in self.rules:
            if self._matches(rule, action, context):
                return Decision(str(uuid.uuid4()), action, rule["decision"], rule.get("reason", f"Matched: {rule['id']}"), [rule["id"]], self.policy_hash, datetime.now(timezone.utc).isoformat())
        return Decision(str(uuid.uuid4()), action, self.default_decision, f"Default: {self.default_decision}", [], self.policy_hash, datetime.now(timezone.utc).isoformat())

    def _matches(self, rule: dict, action: str, context: dict) -> bool:
        if rule.get("action", "*") not in ("*", action): return False
        for key, expected in rule.get("conditions", {}).items():
            actual = context.get(key)
            if isinstance(expected, dict):
                if "gt" in expected and (actual is None or actual <= expected["gt"]): return False
                if "not" in expected and actual == expected["not"]: return False
            elif actual != expected: return False
        return True

    @staticmethod
    def _compute_hash(policy: dict) -> str:
        return f"sha256:{hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(',',':')).encode()).hexdigest()}"
