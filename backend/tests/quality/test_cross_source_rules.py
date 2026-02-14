from app.quality.rules.cross_source import evaluate_cross_source


def test_cross_source_warns_low_linkage_ratio() -> None:
    issues = evaluate_cross_source(
        kind_rows=[{"corp_name": "alpha"}, {"corp_name": "beta"}],
        dart_rows=[{"corp_name": "alpha"}],
        krx_rows=[],
    )
    assert any(issue.rule_code == "CROSS_KIND_DART_LINKAGE_RATIO" and issue.severity == "WARN" for issue in issues)
