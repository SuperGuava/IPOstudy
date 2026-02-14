from app.quality.rules.dart import evaluate_dart_rules


def test_dart_rule_fails_invalid_rcept_no() -> None:
    issues = evaluate_dart_rules(
        {"corp_code": "00126380", "rcept_no": "BAD", "report_nm": "증권신고서"},
        source="DART",
        entity_type="disclosure",
        entity_key="00126380",
    )
    assert any(issue.rule_code == "DART_RCEPT_NO_FORMAT" and issue.severity == "FAIL" for issue in issues)
