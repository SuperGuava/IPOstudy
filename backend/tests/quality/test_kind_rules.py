from app.quality.rules.kind import evaluate_kind_rules


def test_kind_stage_rule_fails_for_unknown_stage() -> None:
    issues = evaluate_kind_rules(
        {"corp_name": "alpha", "stage": "UNKNOWN", "listing_date": "2026-03-15"},
        source="KIND",
        entity_type="ipo",
        entity_key="alpha",
    )
    assert any(issue.rule_code == "KIND_STAGE_ALLOWED" and issue.severity == "FAIL" for issue in issues)
