from app.quality.types import QualityGateResult, QualityIssue


def run_rule_set(rule_fn, payload: dict, *, source: str, entity_type: str, entity_key: str) -> QualityGateResult:
    issues: list[QualityIssue] = rule_fn(payload, source=source, entity_type=entity_type, entity_key=entity_key)
    return QualityGateResult(issues=issues)
