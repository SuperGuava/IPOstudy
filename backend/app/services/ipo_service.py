from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.connectors.dart_connector import DartConnector
from app.connectors.kind_connector import KindConnector
from app.connectors.krx_connector import KrxAuthError, KrxConnector
from app.etl.pipeline import run_pipeline
from app.models.ipo import IpoPipelineItem

_KRX_CATEGORY_ENV_KEYS: dict[str, str] = {
    "index": "KRX_API_INDEX_PATH",
    "stock": "KRX_API_STOCK_PATH",
    "securities": "KRX_API_SECURITIES_PATH",
    "bond": "KRX_API_BOND_PATH",
    "derivative": "KRX_API_DERIVATIVE_PATH",
    "general": "KRX_API_GENERAL_PATH",
    "esg": "KRX_API_ESG_PATH",
}
_KRX_CATEGORY_DEFAULT_PATHS: dict[str, str] = {
    "index": "",
    "stock": "sto/stk_isu_base_info",
    "securities": "",
    "bond": "",
    "derivative": "",
    "general": "",
    "esg": "",
}


def _split_krx_paths(raw: str) -> list[str]:
    return [path.strip() for path in raw.split(",") if path.strip()]


def resolve_krx_openapi_paths(env: dict[str, str] | None = None) -> dict[str, list[str]]:
    source = env or os.environ
    resolved: dict[str, list[str]] = {}
    for category, env_key in _KRX_CATEGORY_ENV_KEYS.items():
        raw = source.get(env_key, _KRX_CATEGORY_DEFAULT_PATHS[category])
        resolved[category] = _split_krx_paths(raw)
    return resolved


def _fetch_krx_with_retry(
    connector: KrxConnector,
    api_path: str,
    bas_dd: str,
    max_attempts: int = 3,
) -> dict:
    last_auth_error: KrxAuthError | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return connector.fetch_open_api(api_path, {"basDd": bas_dd})
        except KrxAuthError as exc:
            last_auth_error = exc
            # KRX may intermittently return WAF "Access Denied"; retry a few times.
            if "access denied" in str(exc).lower() and attempt < max_attempts:
                continue
            raise
    if last_auth_error is not None:
        raise last_auth_error
    raise RuntimeError("unexpected krx fetch retry state")


def _to_item_payload(item: IpoPipelineItem) -> dict:
    return {
        "pipeline_id": item.pipeline_id,
        "corp_code": item.corp_code,
        "corp_name": item.corp_name,
        "stage": item.stage,
        "listing_date": item.listing_date.isoformat() if item.listing_date else None,
        "lead_manager": item.lead_manager,
        "source_dart_rcept_no": item.source_dart_rcept_no,
    }


def list_pipeline_items(session: Session) -> list[dict]:
    rows = session.execute(select(IpoPipelineItem).order_by(IpoPipelineItem.pipeline_id.asc())).scalars().all()
    return [_to_item_payload(row) for row in rows]


def get_pipeline_item(session: Session, pipeline_id: str) -> dict | None:
    row = session.get(IpoPipelineItem, pipeline_id)
    if row is None:
        return None
    return _to_item_payload(row)


def ensure_demo_pipeline_if_empty(session: Session) -> None:
    count = session.execute(select(func.count(IpoPipelineItem.pipeline_id))).scalar_one()
    if count > 0:
        return
    demo_bundle = {
        "batch_id": "demo-seed-batch",
        "kind_rows": [
            {
                "corp_name": "alpha-tech",
                "market": "KOSDAQ",
                "stage": "offering",
                "listing_date": "2026-03-15",
                "lead_manager": "future-securities",
            }
        ],
        "dart_rows": [
            {
                "corp_code": "00126380",
                "corp_name": "alpha-tech",
                "rcept_no": "20260214000001",
                "report_nm": "securities filing",
                "rcept_dt": "20260214",
            }
        ],
        "krx_rows": [],
    }
    run_pipeline(session, demo_bundle)


def refresh_pipeline_live(session: Session, *, corp_code: str, bas_dd: str) -> dict:
    dart_api_key = os.getenv("DART_API_KEY")
    krx_api_key = os.getenv("KRX_API_KEY")

    kind_connector = KindConnector()
    dart_connector = DartConnector(api_key=dart_api_key or "")
    krx_connector = KrxConnector(api_key=krx_api_key)

    kind_rows: list[dict] = []
    dart_rows: list[dict] = []
    krx_rows: list[dict] = []

    kind_error: str | None = None
    dart_error: str | None = None
    krx_status: dict[str, str] = {}

    try:
        kind_rows = kind_connector.fetch_public_offering_companies()
        krx_status["kind"] = f"ok:{len(kind_rows)}"
    except Exception as exc:  # pragma: no cover - runtime diagnostics
        kind_error = f"{type(exc).__name__}: {exc}"
        krx_status["kind"] = "error"

    if dart_api_key:
        try:
            dart_rows = dart_connector.fetch_list(corp_code=corp_code, page_no=1, page_count=100, last_reprt_at="Y")
            krx_status["dart"] = f"ok:{len(dart_rows)}"
        except Exception as exc:  # pragma: no cover - runtime diagnostics
            dart_error = f"{type(exc).__name__}: {exc}"
            krx_status["dart"] = "error"
    else:
        krx_status["dart"] = "missing_key"

    for category, api_paths in resolve_krx_openapi_paths().items():
        if not api_paths:
            krx_status[category] = "not_configured"
            continue
        if not krx_api_key:
            krx_status[category] = "missing_key"
            continue
        rows_count = 0
        auth_count = 0
        schema_count = 0
        error_count = 0
        for api_path in api_paths:
            try:
                payload = _fetch_krx_with_retry(krx_connector, api_path, bas_dd)
                out_block = payload.get("OutBlock_1")
                if not isinstance(out_block, list):
                    schema_count += 1
                    continue
                rows_count += len(out_block)
                krx_rows.append(
                    {
                        "dataset_key": f"openapi.{category}.{api_path.replace('/', '.')}",
                        "required_params": {"basDd": "required"},
                        "request_params": {"basDd": bas_dd},
                        "response": payload,
                    }
                )
            except KrxAuthError:
                auth_count += 1
            except Exception:  # pragma: no cover - runtime diagnostics
                error_count += 1

        if rows_count > 0 and auth_count == 0 and schema_count == 0 and error_count == 0:
            krx_status[category] = f"ok:{rows_count}"
        elif rows_count > 0:
            krx_status[category] = (
                f"partial:ok={rows_count},auth={auth_count},schema={schema_count},error={error_count}"
            )
        elif auth_count > 0:
            krx_status[category] = "auth_error"
        elif schema_count > 0:
            krx_status[category] = "schema_mismatch"
        else:
            krx_status[category] = "error"

    batch_id = f"live-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    result = run_pipeline(
        session,
        {
            "batch_id": batch_id,
            "kind_rows": kind_rows,
            "dart_rows": dart_rows,
            "krx_rows": krx_rows,
        },
    )
    return {
        "batch_id": batch_id,
        "published": result.published,
        "issue_count": len(result.issues),
        "kind_rows": len(kind_rows),
        "dart_rows": len(dart_rows),
        "krx_rows": len(krx_rows),
        "kind_error": kind_error,
        "dart_error": dart_error,
        "source_status": krx_status,
    }
