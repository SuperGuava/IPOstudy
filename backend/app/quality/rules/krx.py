from app.quality.types import QualityIssue


def _is_placeholder(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    return value.strip() in {"", "-", "--", "N/A"}


def _is_numeric_like(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return True
    if not isinstance(value, str):
        return False
    cleaned = value.replace(",", "").strip()
    if cleaned in {"", "-", "--"}:
        return True
    if cleaned.startswith(("+", "-")):
        cleaned = cleaned[1:]
    return cleaned.replace(".", "", 1).isdigit()


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
    elif isinstance(out_block, list):
        requested_bas_dd = str(request_params.get("basDd", "")).strip()
        if requested_bas_dd:
            mismatch_count = 0
            for row in out_block:
                if not isinstance(row, dict):
                    continue
                row_bas_dd = str(row.get("BAS_DD", "")).strip()
                if row_bas_dd and row_bas_dd != requested_bas_dd:
                    mismatch_count += 1
            if mismatch_count > 0:
                issues.append(
                    QualityIssue(
                        source=source,
                        rule_code="KRX_BAS_DD_MISMATCH",
                        severity="WARN",
                        entity_type=entity_type,
                        entity_key=entity_key,
                        message=f"rows with mismatched BAS_DD: {mismatch_count}",
                    )
                )

        isu_codes: list[str] = []
        for row in out_block:
            if isinstance(row, dict):
                value = row.get("ISU_CD")
                if isinstance(value, str) and value.strip():
                    isu_codes.append(value.strip())
        duplicate_count = len(isu_codes) - len(set(isu_codes))
        if duplicate_count > 0:
            issues.append(
                QualityIssue(
                    source=source,
                    rule_code="KRX_DUPLICATE_ISU_CD",
                    severity="WARN",
                    entity_type=entity_type,
                    entity_key=entity_key,
                    message=f"duplicate ISU_CD rows: {duplicate_count}",
                )
            )

        numeric_keys = {"TDD_CLSPRC", "CMPPREVDD_PRC", "FLUC_RT", "LIST_SHRS", "ACC_TRDVOL", "ACC_TRDVAL"}
        invalid_numeric_fields = 0
        for row in out_block:
            if not isinstance(row, dict):
                continue
            for key in numeric_keys:
                if key not in row:
                    continue
                value = row.get(key)
                if _is_placeholder(value):
                    continue
                if not _is_numeric_like(value):
                    invalid_numeric_fields += 1
        if invalid_numeric_fields > 0:
            issues.append(
                QualityIssue(
                    source=source,
                    rule_code="KRX_NUMERIC_FIELD_INVALID",
                    severity="WARN",
                    entity_type=entity_type,
                    entity_key=entity_key,
                    message=f"invalid numeric field count: {invalid_numeric_fields}",
                )
            )

    return issues
