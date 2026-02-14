from app.quality.rules.krx import evaluate_krx_rules


def test_krx_rule_warns_empty_outblock() -> None:
    issues = evaluate_krx_rules(
        {"dataset_key": "stock.marketcap", "required_params": {"trdDd": "20260214"}, "response": {"OutBlock_1": []}},
        source="KRX",
        entity_type="dataset",
        entity_key="stock.marketcap",
    )
    assert any(issue.rule_code == "KRX_EMPTY_DATA" and issue.severity == "WARN" for issue in issues)
