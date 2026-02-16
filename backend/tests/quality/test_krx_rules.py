from app.quality.rules.krx import evaluate_krx_rules


def test_krx_rule_warns_empty_outblock() -> None:
    issues = evaluate_krx_rules(
        {"dataset_key": "stock.marketcap", "required_params": {"trdDd": "20260214"}, "response": {"OutBlock_1": []}},
        source="KRX",
        entity_type="dataset",
        entity_key="stock.marketcap",
    )
    assert any(issue.rule_code == "KRX_EMPTY_DATA" and issue.severity == "WARN" for issue in issues)


def test_krx_rule_warns_bas_dd_mismatch() -> None:
    issues = evaluate_krx_rules(
        {
            "dataset_key": "openapi.stock.sto.stk_bydd_trd",
            "required_params": {"basDd": "required"},
            "request_params": {"basDd": "20250131"},
            "response": {"OutBlock_1": [{"BAS_DD": "20250130"}]},
        },
        source="KRX",
        entity_type="dataset",
        entity_key="openapi.stock.sto.stk_bydd_trd",
    )
    assert any(issue.rule_code == "KRX_BAS_DD_MISMATCH" and issue.severity == "WARN" for issue in issues)


def test_krx_rule_warns_duplicate_isu_cd() -> None:
    issues = evaluate_krx_rules(
        {
            "dataset_key": "openapi.stock.sto.stk_bydd_trd",
            "required_params": {"basDd": "required"},
            "request_params": {"basDd": "20250131"},
            "response": {
                "OutBlock_1": [
                    {"ISU_CD": "KR7000000001", "BAS_DD": "20250131"},
                    {"ISU_CD": "KR7000000001", "BAS_DD": "20250131"},
                ]
            },
        },
        source="KRX",
        entity_type="dataset",
        entity_key="openapi.stock.sto.stk_bydd_trd",
    )
    assert any(issue.rule_code == "KRX_DUPLICATE_ISU_CD" and issue.severity == "WARN" for issue in issues)


def test_krx_rule_warns_invalid_numeric_field() -> None:
    issues = evaluate_krx_rules(
        {
            "dataset_key": "openapi.stock.sto.stk_bydd_trd",
            "required_params": {"basDd": "required"},
            "request_params": {"basDd": "20250131"},
            "response": {"OutBlock_1": [{"BAS_DD": "20250131", "ACC_TRDVOL": "abc"}]},
        },
        source="KRX",
        entity_type="dataset",
        entity_key="openapi.stock.sto.stk_bydd_trd",
    )
    assert any(issue.rule_code == "KRX_NUMERIC_FIELD_INVALID" and issue.severity == "WARN" for issue in issues)
