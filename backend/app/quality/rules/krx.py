from app.quality.types import QualityIssue


def evaluate_krx_rules(payload: dict, *, source: str, entity_type: str, entity_key: str) -> list[QualityIssue]:
    issues: list[QualityIssue] = []

    required_params = payload.get("required_params", {})
    request_params = payload.get("request_params", {})
    missing_required = [key for key in required_params.keys() if key not in request_params and key != "trdDd"]
    if missing_required:
        issues.append(
            QualityIssue(
                source=source,
                rule_code="KRX_REQUIRED_PARAMS",
                severity="FAIL",
                entity_type=entity_type,
                entity_key=entity_key,
                message=f"missing required params: {', '.join(missing_required)}",
            )
        )

    response = payload.get("response", {})
    out_block = response.get("OutBlock_1")
    if out_block is None:
        issues.append(
            QualityIssue(
                source=source,
                rule_code="KRX_RESPONSE_SCHEMA",
                severity="FAIL",
                entity_type=entity_type,
                entity_key=entity_key,
                message="OutBlock_1 key missing",
            )
        )
    elif isinstance(out_block, list) and len(out_block) == 0:
        issues.append(
            QualityIssue(
                source=source,
                rule_code="KRX_EMPTY_DATA",
                severity="WARN",
                entity_type=entity_type,
                entity_key=entity_key,
                message="OutBlock_1 is empty",
            )
        )

    return issues
