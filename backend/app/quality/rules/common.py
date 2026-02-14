from datetime import datetime

from app.quality.types import QualityIssue


def check_required_keys(payload: dict, required_keys: list[str]) -> list[QualityIssue]:
    missing = [key for key in required_keys if payload.get(key) in (None, "")]
    if not missing:
        return []
    return [
        QualityIssue(
            source="COMMON",
            rule_code="COMMON_REQUIRED_KEYS",
            severity="FAIL",
            entity_type="record",
            entity_key=payload.get("corp_code", "unknown"),
            message=f"missing required keys: {', '.join(missing)}",
        )
    ]


def check_date_format(value: str | None) -> bool:
    if not value:
        return False
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False


def check_numeric(value: str | int | float | None, *, allow_negative: bool = False) -> bool:
    if value is None:
        return False
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    if not allow_negative and number < 0:
        return False
    return True
