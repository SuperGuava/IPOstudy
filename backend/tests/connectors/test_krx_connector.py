import json
import io
from pathlib import Path
from urllib.error import HTTPError

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.connectors.krx_connector import KrxAuthError, KrxConnector
from app.db.base import Base
from app.models.snapshot import DatasetRegistry
from app.services.dataset_registry_service import DatasetRegistryService


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "krx" / "marketcap_response.json"


class FakeKrxClient:
    def __init__(self) -> None:
        self.preflight_url: str | None = None
        self.preflight_headers: dict[str, str] | None = None
        self.last_url: str | None = None
        self.last_data: dict | None = None
        self.last_headers: dict[str, str] | None = None

    def get_text(self, url: str, params: dict, headers: dict[str, str] | None = None) -> str:
        self.preflight_url = url
        self.preflight_headers = headers
        return "ok"

    def post_json(self, url: str, data: dict, headers: dict[str, str] | None = None) -> dict:
        self.last_url = url
        self.last_data = data
        self.last_headers = headers
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


class FakeOpenApiClient:
    def __init__(self) -> None:
        self.last_url: str | None = None
        self.last_params: dict | None = None
        self.last_headers: dict[str, str] | None = None

    def get_json(self, url: str, params: dict, headers: dict[str, str] | None = None) -> dict:
        self.last_url = url
        self.last_params = params
        self.last_headers = headers
        return {"OutBlock_1": [{"ISU_CD": "KR7005930003"}]}


class UnauthorizedOpenApiClient:
    def get_json(self, url: str, params: dict, headers: dict[str, str] | None = None) -> dict:
        body = io.BytesIO(b'{"respMsg":"Unauthorized Key","respCode":"401"}')
        raise HTTPError(url=url, code=401, msg="Unauthorized", hdrs=None, fp=body)


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_krx_connector_uses_registry_bld(db_session: Session) -> None:
    fake_http = FakeKrxClient()
    db_session.add(
        DatasetRegistry(
            dataset_key="stock.marketcap",
            bld="dbms/MDC/STAT/standard/MDCSTAT01501",
            required_params={"trdDd": "required"},
        )
    )
    db_session.commit()

    connector = KrxConnector(http_client=fake_http)
    registry = DatasetRegistryService(session=db_session)
    data = registry.fetch_dataset(
        "stock.marketcap",
        {"trdDd": "20260213"},
        connector=connector,
    )

    assert "OutBlock_1" in data
    assert fake_http.last_data is not None
    assert fake_http.last_data["bld"] == "dbms/MDC/STAT/standard/MDCSTAT01501"


def test_krx_connector_primes_session_and_sets_browser_headers() -> None:
    fake_http = FakeKrxClient()
    connector = KrxConnector(http_client=fake_http)

    connector.fetch_dataset("dbms/MDC/STAT/standard/MDCSTAT01501", {"trdDd": "20260213"})

    assert fake_http.preflight_url is not None
    assert fake_http.preflight_url.endswith("/contents/MDC/MDI/mdiLoader/index.cmd")
    assert fake_http.preflight_headers is not None
    assert fake_http.preflight_headers["User-Agent"].startswith("Mozilla/")

    assert fake_http.last_headers is not None
    assert fake_http.last_headers["Referer"].endswith("/contents/MDC/MDI/mdiLoader/index.cmd")
    assert fake_http.last_headers["X-Requested-With"] == "XMLHttpRequest"


def test_krx_open_api_uses_auth_header_and_get_endpoint() -> None:
    fake_http = FakeOpenApiClient()
    connector = KrxConnector(http_client=fake_http, api_key="sample-key")

    data = connector.fetch_open_api("sto/stk_isu_base_info", {"basDd": "20250131"})

    assert "OutBlock_1" in data
    assert fake_http.last_url == "https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info"
    assert fake_http.last_params == {"basDd": "20250131"}
    assert fake_http.last_headers is not None
    assert fake_http.last_headers["AUTH_KEY"] == "sample-key"


def test_krx_open_api_requires_key() -> None:
    fake_http = FakeOpenApiClient()
    connector = KrxConnector(http_client=fake_http, api_key=None)

    with pytest.raises(ValueError, match="KRX_API_KEY"):
        connector.fetch_open_api("sto/stk_isu_base_info", {"basDd": "20250131"})


def test_krx_open_api_unauthorized_maps_to_auth_error() -> None:
    connector = KrxConnector(http_client=UnauthorizedOpenApiClient(), api_key="bad-key")

    with pytest.raises(KrxAuthError, match="Unauthorized Key"):
        connector.fetch_open_api("sto/stk_isu_base_info", {"basDd": "20250131"})
