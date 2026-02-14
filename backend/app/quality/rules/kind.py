from app.quality.types import QualityIssue

ALLOWED_STAGES = {"예비심사", "공모", "상장예정", "신규상장", "offering", "prelisting", "listed"}


def evaluate_kind_rules(payload: dict, *, source: str, entity_type: str, entity_key: str) -> list[QualityIssue]:
    issues: list[QualityIssue] = []

    stage = str(payload.get("stage", "")).strip()
    if stage not in ALLOWED_STAGES:
        issues.append(
            QualityIssue(
                source=source,
                rule_code="KIND_STAGE_ALLOWED",
                severity="FAIL",
                entity_type=entity_type,
                entity_key=entity_key,
                message=f"unsupported stage: {stage}",
            )
        )

    has_any_key_date = any(payload.get(key) for key in ("listing_date", "subscription_date", "demand_forecast_date"))
    if not has_any_key_date:
        issues.append(
            QualityIssue(
                source=source,
                rule_code="KIND_KEY_DATE_REQUIRED",
                severity="WARN",
                entity_type=entity_type,
                entity_key=entity_key,
                message="no key date found",
            )
        )
    return issues
