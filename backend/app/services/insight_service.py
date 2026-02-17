from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.ipo import IpoPipelineItem
from app.models.quality import DataQualityIssue


def _build_company_key(corp_code: str | None, corp_name: str) -> str:
    if corp_code:
        return corp_code
    return f"name:{corp_name}"


def _risk_label(*, fail_count: int, warn_count: int) -> str:
    if fail_count > 0:
        return "high"
    if warn_count > 0:
        return "medium"
    return "low"


def list_companies_for_explorer(session: Session, *, query: str | None, limit: int) -> list[dict]:
    stmt = select(IpoPipelineItem).order_by(IpoPipelineItem.listing_date.desc().nullslast(), IpoPipelineItem.corp_name.asc())
    if query:
        q = query.strip()
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(or_(IpoPipelineItem.corp_name.ilike(pattern), IpoPipelineItem.corp_code.ilike(pattern)))
    rows = session.execute(stmt.limit(limit)).scalars().all()

    corp_codes = [row.corp_code for row in rows if row.corp_code]
    quality_counts: dict[str, dict[str, int]] = {}
    if corp_codes:
        quality_rows = session.execute(
            select(DataQualityIssue.entity_key, DataQualityIssue.severity, func.count(DataQualityIssue.id))
            .where(DataQualityIssue.entity_key.in_(corp_codes))
            .group_by(DataQualityIssue.entity_key, DataQualityIssue.severity)
        ).all()
        for entity_key, severity, count in quality_rows:
            slot = quality_counts.setdefault(str(entity_key), {"PASS": 0, "WARN": 0, "FAIL": 0})
            slot[str(severity)] = int(count)

    items: list[dict] = []
    for row in rows:
        counts = quality_counts.get(row.corp_code or "", {"PASS": 0, "WARN": 0, "FAIL": 0})
        items.append(
            {
                "company_key": _build_company_key(row.corp_code, row.corp_name),
                "corp_code": row.corp_code,
                "corp_name": row.corp_name,
                "stage": row.stage,
                "listing_date": row.listing_date.isoformat() if row.listing_date else None,
                "lead_manager": row.lead_manager,
                "quality": counts,
                "risk_label": _risk_label(fail_count=counts["FAIL"], warn_count=counts["WARN"]),
            }
        )
    return items


def get_company_insight_detail(session: Session, *, company_key: str) -> dict | None:
    row = None
    if company_key.startswith("name:"):
        corp_name = company_key.split(":", 1)[1]
        row = (
            session.execute(
                select(IpoPipelineItem)
                .where(IpoPipelineItem.corp_name == corp_name)
                .order_by(IpoPipelineItem.listing_date.desc().nullslast())
                .limit(1)
            )
            .scalars()
            .first()
        )
    else:
        row = (
            session.execute(
                select(IpoPipelineItem)
                .where(IpoPipelineItem.corp_code == company_key)
                .order_by(IpoPipelineItem.listing_date.desc().nullslast())
                .limit(1)
            )
            .scalars()
            .first()
        )

    if row is None:
        return None

    quality_by_severity = {"PASS": 0, "WARN": 0, "FAIL": 0}
    quality_by_source: dict[str, int] = {}
    if row.corp_code:
        quality_rows = session.execute(
            select(DataQualityIssue.source, DataQualityIssue.severity, func.count(DataQualityIssue.id))
            .where(DataQualityIssue.entity_key == row.corp_code)
            .group_by(DataQualityIssue.source, DataQualityIssue.severity)
        ).all()
        for source, severity, count in quality_rows:
            quality_by_source[str(source)] = quality_by_source.get(str(source), 0) + int(count)
            quality_by_severity[str(severity)] = quality_by_severity.get(str(severity), 0) + int(count)

    quick_insights: list[str] = []
    quick_insights.append(f"현재 IPO 단계는 '{row.stage}' 입니다.")
    if row.listing_date:
        quick_insights.append(f"기준 상장일은 {row.listing_date.isoformat()} 입니다.")
    if row.lead_manager:
        quick_insights.append(f"대표 주관사는 {row.lead_manager} 입니다.")
    quick_insights.append(
        f"품질 이슈 요약: FAIL {quality_by_severity['FAIL']}건, WARN {quality_by_severity['WARN']}건 입니다."
    )

    beginner_summary = (
        f"{row.corp_name}은(는) 현재 '{row.stage}' 단계이며, "
        f"즉시 확인할 항목은 품질 FAIL {quality_by_severity['FAIL']}건 입니다."
    )

    return {
        "company_key": _build_company_key(row.corp_code, row.corp_name),
        "corp_code": row.corp_code,
        "corp_name": row.corp_name,
        "ipo": {
            "pipeline_id": row.pipeline_id,
            "stage": row.stage,
            "listing_date": row.listing_date.isoformat() if row.listing_date else None,
            "lead_manager": row.lead_manager,
        },
        "quality": {"severity": quality_by_severity, "source": quality_by_source},
        "beginner_summary": beginner_summary,
        "quick_insights": quick_insights,
    }


def list_analysis_templates() -> list[dict]:
    return [
        {
            "template_id": "foundation-check",
            "title": "기본 체력 점검",
            "description": "기업의 현재 단계, 상장일, 주관사, 품질 FAIL 여부를 한 번에 확인합니다.",
            "steps": [
                "1) IPO 단계 확인",
                "2) 상장일/주관사 확인",
                "3) 품질 FAIL 우선 조치",
            ],
        },
        {
            "template_id": "quality-risk-scan",
            "title": "데이터 품질 리스크 스캔",
            "description": "DART/KIND/KRX/CROSS 이슈 분포를 보고 신뢰도 리스크를 판단합니다.",
            "steps": [
                "1) FAIL, WARN 건수 확인",
                "2) source별 집중 구간 확인",
                "3) 재수집 또는 매핑 보정",
            ],
        },
        {
            "template_id": "listing-readiness",
            "title": "상장 준비 상태 해석",
            "description": "prelisting/listed/offering 상태를 기준으로 현재 액션을 추천합니다.",
            "steps": [
                "1) stage 분류 확인",
                "2) listing_date 시점 확인",
                "3) 다음 모니터링 일정 설정",
            ],
        },
    ]

