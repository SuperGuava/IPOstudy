from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.connectors.dart_connector import DartConnector
from app.connectors.kind_connector import KindConnector
from app.connectors.krx_connector import KrxAccessDeniedError, KrxAuthError, KrxConnector, KrxRequestError
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
    initial_backoff: float = 0.2,
) -> tuple[dict, int]:
    backoff = initial_backoff
    last_auth_error: KrxAuthError | None = None
    last_request_error: KrxRequestError | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return connector.fetch_open_api(api_path, {"basDd": bas_dd}), attempt
        except KrxAccessDeniedError as exc:
            last_auth_error = exc
            if attempt < max_attempts:
                time.sleep(backoff)
                backoff = min(backoff * 2, 1.0)
                continue
            raise
        except KrxAuthError as exc:
            last_auth_error = exc
            raise
        except KrxRequestError as exc:
            last_request_error = exc
            if attempt < max_attempts:
                time.sleep(backoff)
                backoff = min(backoff * 2, 1.0)
                continue
            raise
    if last_auth_error is not None:
        raise last_auth_error
    if last_request_error is not None:
        raise last_request_error
    raise RuntimeError("unexpected krx fetch retry state")


def _collect_krx_path_result(*, krx_api_key: str, api_path: str, bas_dd: str) -> dict:
    connector = KrxConnector(api_key=krx_api_key)
    try:
        payload, attempts = _fetch_krx_with_retry(connector, api_path, bas_dd)
        out_block = payload.get("OutBlock_1")
        if not isinstance(out_block, list):
            return {"path": api_path, "status": "schema_mismatch", "rows": 0, "attempts": attempts}
        return {
            "path": api_path,
            "status": "ok",
            "rows": len(out_block),
            "attempts": attempts,
            "payload": payload,
        }
    except KrxAccessDeniedError as exc:
        return {"path": api_path, "status": "access_denied", "rows": 0, "attempts": 3, "error": str(exc)}
    except KrxAuthError as exc:
        return {"path": api_path, "status": "auth_error", "rows": 0, "attempts": 1, "error": str(exc)}
    except Exception as exc:  # pragma: no cover - runtime diagnostics
        return {"path": api_path, "status": "error", "rows": 0, "attempts": 1, "error": f"{type(exc).__name__}: {exc}"}


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


def _resolve_dart_window(bas_dd: str, lookback_days: int = 365) -> tuple[str, str]:
    target_date = datetime.strptime(bas_dd, "%Y%m%d")
    begin_date = target_date - timedelta(days=lookback_days)
    return begin_date.strftime("%Y%m%d"), target_date.strftime("%Y%m%d")


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

    kind_rows: list[dict] = []
    dart_rows: list[dict] = []
    krx_rows: list[dict] = []

    kind_error: str | None = None
    dart_error: str | None = None
    krx_status: dict[str, str] = {}
    krx_status_detail: dict[str, list[dict]] = {}

    try:
        kind_rows = kind_connector.fetch_public_offering_companies()
        krx_status["kind"] = f"ok:{len(kind_rows)}"
    except Exception as exc:  # pragma: no cover - runtime diagnostics
        kind_error = f"{type(exc).__name__}: {exc}"
        krx_status["kind"] = "error"

    if dart_api_key:
        try:
            dart_bgn_de, dart_end_de = _resolve_dart_window(bas_dd)
            dart_rows = dart_connector.fetch_list(
                corp_code=corp_code,
                page_no=1,
                page_count=100,
                bgn_de=dart_bgn_de,
                end_de=dart_end_de,
            )
            krx_status["dart"] = f"ok:{len(dart_rows)}"
        except Exception as exc:  # pragma: no cover - runtime diagnostics
            dart_error = f"{type(exc).__name__}: {exc}"
            krx_status["dart"] = "error"
    else:
        krx_status["dart"] = "missing_key"

    for category, api_paths in resolve_krx_openapi_paths().items():
        krx_status_detail[category] = []
        if not api_paths:
            krx_status[category] = "not_configured"
            continue
        if not krx_api_key:
            krx_status[category] = "missing_key"
            continue
        rows_count = 0
        auth_count = 0
        denied_count = 0
        schema_count = 0
        error_count = 0
        max_workers = min(8, max(1, len(api_paths)))
        path_results: list[dict] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(_collect_krx_path_result, krx_api_key=krx_api_key, api_path=api_path, bas_dd=bas_dd)
                for api_path in api_paths
            ]
            for future in as_completed(futures):
                path_results.append(future.result())

        for result in sorted(path_results, key=lambda item: item["path"]):
            status = result["status"]
            if status == "ok":
                rows_count += int(result["rows"])
                krx_rows.append(
                    {
                        "dataset_key": f"openapi.{category}.{result['path'].replace('/', '.')}",
                        "required_params": {"basDd": "required"},
                        "request_params": {"basDd": bas_dd},
                        "response": result["payload"],
                    }
                )
            elif status == "auth_error":
                auth_count += 1
            elif status == "access_denied":
                denied_count += 1
            elif status == "schema_mismatch":
                schema_count += 1
            else:
                error_count += 1
            detail_entry = {
                "path": result["path"],
                "status": status,
                "rows": result["rows"],
                "attempts": result["attempts"],
            }
            if "error" in result:
                detail_entry["error"] = result["error"]
            krx_status_detail[category].append(detail_entry)

        if rows_count > 0 and auth_count == 0 and denied_count == 0 and schema_count == 0 and error_count == 0:
            krx_status[category] = f"ok:{rows_count}"
        elif rows_count > 0:
            krx_status[category] = (
                f"partial:ok={rows_count},auth={auth_count},denied={denied_count},schema={schema_count},error={error_count}"
            )
        elif denied_count > 0:
            krx_status[category] = "access_denied"
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
        "source_status_detail": krx_status_detail,
    }
