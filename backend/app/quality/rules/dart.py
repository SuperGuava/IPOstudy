import re

from app.quality.rules.common import check_required_keys
from app.quality.types import QualityIssue


def evaluate_dart_rules(payload: dict, *, source: str, entity_type: str, entity_key: str) -> list[QualityIssue]:
    issues = check_required_keys(payload, ["corp_code", "rcept_no"])
    rcept_no = str(payload.get("rcept_no", ""))
    if not re.fullmatch(r"\d{14}", rcept_no):
        issues.append(
            QualityIssue(
                source=source,
                rule_code="DART_RCEPT_NO_FORMAT",
                severity="FAIL",
                entity_type=entity_type,
                entity_key=entity_key,
                message="rcept_no must be 14 digits",
            )
        )
    if not payload.get("report_nm"):
        issues.append(
            QualityIssue(
                source=source,
                rule_code="DART_REPORT_NAME_EMPTY",
                severity="WARN",
                entity_type=entity_type,
                entity_key=entity_key,
                message="report_nm is empty",
            )
        )
    return issues
