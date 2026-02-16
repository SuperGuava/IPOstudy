from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.connectors.dart_connector import DartConnector
from app.connectors.kind_connector import KindConnector
from app.connectors.krx_connector import KrxAuthError, KrxConnector
from app.etl.pipeline import run_pipeline
from app.jobs.tasks import run_quality_summary_job
from app.models.quality import DataQualityIssue


def load_env_from_repo_root() -> dict[str, str]:
    env: dict[str, str] = {}
    root_env = Path(__file__).resolve().parents[2] / ".env"
    if not root_env.exists():
        return env
    for line in root_env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def resolve_krx_stock_path(env: dict[str, str]) -> str:
    return env.get("KRX_API_STOCK_PATH", "sto/stk_isu_base_info")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one ETL/quality pipeline cycle with live connectors.")
    parser.add_argument("--corp-code", default="00126380", help="DART corp_code used for disclosure pull")
    parser.add_argument("--bas-dd", default=datetime.now().strftime("%Y%m%d"), help="KRX basDd (YYYYMMDD)")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    env = load_env_from_repo_root()

    database_url = env.get("DATABASE_URL")
    dart_api_key = env.get("DART_API_KEY")
    krx_api_key = env.get("KRX_API_KEY")

    if not database_url:
        print("DATABASE_URL missing in .env")
        return 2
    if not dart_api_key:
        print("DART_API_KEY missing in .env")
        return 2

    engine = create_engine(database_url, future=True)

    kind_rows: list[dict] = []
    dart_rows: list[dict] = []
    krx_rows: list[dict] = []

    kind_error: str | None = None
    dart_error: str | None = None
    krx_status = "not_called"

    kind_connector = KindConnector()
    dart_connector = DartConnector(api_key=dart_api_key)
    krx_connector = KrxConnector(api_key=krx_api_key)

    try:
        kind_rows = kind_connector.fetch_public_offering_companies()
    except Exception as exc:  # pragma: no cover - runtime diagnostics
        kind_error = f"{type(exc).__name__}: {exc}"

    try:
        dart_rows = dart_connector.fetch_list(args.corp_code, page_no=1, page_count=20, last_reprt_at="Y")
    except Exception as exc:  # pragma: no cover - runtime diagnostics
        dart_error = f"{type(exc).__name__}: {exc}"

    request_params = {"basDd": args.bas_dd}
    response_payload: dict = {}
    stock_api_path = resolve_krx_stock_path(env)
    if krx_api_key:
        try:
            response_payload = krx_connector.fetch_open_api(stock_api_path, request_params)
            krx_status = "ok"
        except KrxAuthError as exc:
            krx_status = f"auth_error:{exc}"
        except Exception as exc:  # pragma: no cover - runtime diagnostics
            krx_status = f"error:{type(exc).__name__}:{exc}"
    else:
        krx_status = "missing_key"

    krx_rows.append(
        {
            "dataset_key": f"openapi.stock.{stock_api_path.replace('/', '.')}",
            "required_params": {"basDd": "required"},
            "request_params": request_params,
            "response": response_payload,
        }
    )

    batch_id = f"live-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    bundle = {
        "batch_id": batch_id,
        "kind_rows": kind_rows,
        "dart_rows": dart_rows,
        "krx_rows": krx_rows,
    }

    with Session(engine) as session:
        result = run_pipeline(session, bundle)
        summary_rows = run_quality_summary_job(session, datetime.now().date().isoformat())
        batch_issues = (
            session.execute(select(DataQualityIssue).where(DataQualityIssue.batch_id == batch_id))
            .scalars()
            .all()
        )

    severity_counts: dict[str, int] = {}
    for issue in batch_issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

    print("pipeline_batch_id=", batch_id)
    print("published=", result.published)
    print("kind_rows=", len(kind_rows), "kind_error=", kind_error)
    print("dart_rows=", len(dart_rows), "dart_error=", dart_error)
    print("krx_status=", krx_status)
    print("issues_total=", len(batch_issues), "severity=", severity_counts)
    print("daily_summary_sources=", summary_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
