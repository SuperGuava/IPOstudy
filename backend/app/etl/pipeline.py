from datetime import date

from sqlalchemy.orm import Session

from app.etl.normalize import normalize_dart_disclosures, normalize_kind_rows
from app.etl.reconcile import match_kind_with_dart
from app.models.ipo import IpoPipelineItem


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    cleaned = value.replace("-", "")
    if len(cleaned) != 8 or not cleaned.isdigit():
        return None
    return date(int(cleaned[0:4]), int(cleaned[4:6]), int(cleaned[6:8]))


def run_pipeline(session: Session, fixture_bundle: dict) -> None:
    kind_rows = normalize_kind_rows(fixture_bundle.get("kind_rows", []))
    dart_rows = normalize_dart_disclosures(fixture_bundle.get("dart_rows", []))
    merged = match_kind_with_dart(kind_rows, dart_rows)

    for idx, row in enumerate(merged, start=1):
        pipeline_id = f"{row['corp_name']}-{idx}"
        item = IpoPipelineItem(
            pipeline_id=pipeline_id,
            corp_name=row["corp_name"],
            corp_code=row.get("corp_code"),
            expected_stock_code=None,
            stage=row.get("stage") or "공모",
            key_dates={"listing_date": row.get("listing_date")},
            offer_price=None,
            offer_amount=None,
            lead_manager=row.get("lead_manager"),
            source_kind_row_id=str(idx),
            source_dart_rcept_no=row.get("source_dart_rcept_no"),
            listing_date=_parse_date(row.get("listing_date")),
        )
        session.merge(item)
    session.commit()
