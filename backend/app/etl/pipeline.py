from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from app.etl.normalize import normalize_dart_disclosures, normalize_kind_rows
from app.etl.reconcile import match_kind_with_dart
from app.models.ipo import IpoPipelineItem
from app.quality.gate import run_quality_gate
from app.quality.types import QualityIssue
from app.services.quality_log_service import save_publish_log, save_quality_issues


@dataclass(slots=True)
class PipelineRunResult:
    published: bool
    issues: list[QualityIssue]


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    cleaned = value.replace("-", "")
    if len(cleaned) != 8 or not cleaned.isdigit():
        return None
    return date(int(cleaned[0:4]), int(cleaned[4:6]), int(cleaned[6:8]))


def run_pipeline(session: Session, fixture_bundle: dict) -> PipelineRunResult:
    batch_id = fixture_bundle.get("batch_id")
    kind_rows = normalize_kind_rows(fixture_bundle.get("kind_rows", []))
    dart_rows = normalize_dart_disclosures(fixture_bundle.get("dart_rows", []))
    krx_rows = fixture_bundle.get("krx_rows", [])
    merged = match_kind_with_dart(kind_rows, dart_rows)

    gate_result = run_quality_gate(kind_rows=kind_rows, dart_rows=dart_rows, krx_rows=krx_rows)
    save_quality_issues(session, gate_result.issues, batch_id=batch_id)

    if gate_result.has_fail:
        save_publish_log(
            session,
            snapshot_type="ipo_pipeline",
            entity_key=batch_id or "unknown",
            published=False,
            blocked_reason="quality_fail",
            batch_id=batch_id,
        )
        session.commit()
        return PipelineRunResult(published=False, issues=gate_result.issues)

    for idx, row in enumerate(merged, start=1):
        pipeline_id = f"{row['corp_name']}-{idx}"
        item = IpoPipelineItem(
            pipeline_id=pipeline_id,
            corp_name=row["corp_name"],
            corp_code=row.get("corp_code"),
            expected_stock_code=None,
            stage=row.get("stage") or "offering",
            key_dates={"listing_date": row.get("listing_date")},
            offer_price=None,
            offer_amount=None,
            lead_manager=row.get("lead_manager"),
            source_kind_row_id=str(idx),
            source_dart_rcept_no=row.get("source_dart_rcept_no"),
            listing_date=_parse_date(row.get("listing_date")),
        )
        session.merge(item)

    save_publish_log(
        session,
        snapshot_type="ipo_pipeline",
        entity_key=batch_id or "unknown",
        published=True,
        blocked_reason=None,
        batch_id=batch_id,
    )
    session.commit()
    return PipelineRunResult(published=True, issues=gate_result.issues)
