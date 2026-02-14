from sqlalchemy.orm import Session

from app.models.quality import DataQualityIssue, SnapshotPublishLog
from app.quality.types import QualityIssue


def save_quality_issues(session: Session, issues: list[QualityIssue], *, batch_id: str | None) -> None:
    for issue in issues:
        session.add(
            DataQualityIssue(
                source=issue.source,
                rule_code=issue.rule_code,
                severity=issue.severity,
                entity_type=issue.entity_type,
                entity_key=issue.entity_key,
                message=issue.message,
                batch_id=batch_id,
            )
        )


def save_publish_log(
    session: Session,
    *,
    snapshot_type: str,
    entity_key: str,
    published: bool,
    blocked_reason: str | None,
    batch_id: str | None,
) -> None:
    session.add(
        SnapshotPublishLog(
            snapshot_type=snapshot_type,
            entity_key=entity_key,
            published=published,
            blocked_reason=blocked_reason,
            batch_id=batch_id,
        )
    )
