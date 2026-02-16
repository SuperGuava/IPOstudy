from __future__ import annotations

from dataclasses import dataclass

from app.services import ipo_service


def test_resolve_krx_openapi_paths_supports_multi_path_values() -> None:
    env = {
        "KRX_API_INDEX_PATH": "idx/krx_dd_trd, idx/kospi_dd_trd , idx/kosdaq_dd_trd",
        "KRX_API_STOCK_PATH": "sto/stk_bydd_trd",
        "KRX_API_DERIVATIVE_PATH": "drv/fut_bydd_trd,drv/opt_bydd_trd",
    }
    paths = ipo_service.resolve_krx_openapi_paths(env)
    assert paths["index"] == ["idx/krx_dd_trd", "idx/kospi_dd_trd", "idx/kosdaq_dd_trd"]
    assert paths["stock"] == ["sto/stk_bydd_trd"]
    assert paths["derivative"] == ["drv/fut_bydd_trd", "drv/opt_bydd_trd"]
    assert paths["securities"] == []
    assert paths["bond"] == []
    assert paths["general"] == []
    assert paths["esg"] == []


def test_refresh_pipeline_live_collects_rows_from_multiple_paths(monkeypatch) -> None:
    monkeypatch.setenv("DART_API_KEY", "dart-key")
    monkeypatch.setenv("KRX_API_KEY", "krx-key")
    monkeypatch.setenv("KRX_API_INDEX_PATH", "idx/krx_dd_trd,idx/kospi_dd_trd")
    monkeypatch.setenv("KRX_API_STOCK_PATH", "sto/stk_bydd_trd")
    monkeypatch.delenv("KRX_API_SECURITIES_PATH", raising=False)
    monkeypatch.delenv("KRX_API_BOND_PATH", raising=False)
    monkeypatch.delenv("KRX_API_DERIVATIVE_PATH", raising=False)
    monkeypatch.delenv("KRX_API_GENERAL_PATH", raising=False)
    monkeypatch.delenv("KRX_API_ESG_PATH", raising=False)

    class FakeKindConnector:
        def fetch_public_offering_companies(self) -> list[dict]:
            return [{"corp_name": "alpha-tech"}]

    class FakeDartConnector:
        def __init__(self, api_key: str) -> None:
            self.api_key = api_key

        def fetch_list(
            self,
            corp_code: str,
            page_no: int,
            page_count: int,
            last_reprt_at: str,
        ) -> list[dict]:
            return [{"corp_code": corp_code, "rcept_no": "1"}]

    class FakeKrxConnector:
        def __init__(self, api_key: str | None) -> None:
            self.api_key = api_key

        def fetch_open_api(self, api_path: str, params: dict[str, str]) -> dict:
            mapping = {
                "idx/krx_dd_trd": [{"id": "A"}, {"id": "B"}],
                "idx/kospi_dd_trd": [{"id": "C"}],
                "sto/stk_bydd_trd": [{"id": "D"}],
            }
            return {"OutBlock_1": mapping[api_path]}

    @dataclass
    class FakeRunResult:
        published: bool
        issues: list

    captured_bundle: dict = {}

    def fake_run_pipeline(session: object, bundle: dict) -> FakeRunResult:
        captured_bundle.update(bundle)
        return FakeRunResult(published=True, issues=[])

    monkeypatch.setattr(ipo_service, "KindConnector", FakeKindConnector)
    monkeypatch.setattr(ipo_service, "DartConnector", FakeDartConnector)
    monkeypatch.setattr(ipo_service, "KrxConnector", FakeKrxConnector)
    monkeypatch.setattr(ipo_service, "run_pipeline", fake_run_pipeline)

    result = ipo_service.refresh_pipeline_live(object(), corp_code="00126380", bas_dd="20250131")

    assert result["published"] is True
    assert result["krx_rows"] == 3
    assert result["source_status"]["index"] == "ok:3"
    assert result["source_status"]["stock"] == "ok:1"
    assert result["source_status"]["securities"] == "not_configured"
    assert len(captured_bundle["krx_rows"]) == 3


def test_refresh_pipeline_live_retries_transient_access_denied(monkeypatch) -> None:
    monkeypatch.setenv("DART_API_KEY", "dart-key")
    monkeypatch.setenv("KRX_API_KEY", "krx-key")
    monkeypatch.setenv("KRX_API_STOCK_PATH", "sto/stk_bydd_trd")
    monkeypatch.delenv("KRX_API_INDEX_PATH", raising=False)
    monkeypatch.delenv("KRX_API_SECURITIES_PATH", raising=False)
    monkeypatch.delenv("KRX_API_BOND_PATH", raising=False)
    monkeypatch.delenv("KRX_API_DERIVATIVE_PATH", raising=False)
    monkeypatch.delenv("KRX_API_GENERAL_PATH", raising=False)
    monkeypatch.delenv("KRX_API_ESG_PATH", raising=False)

    class FakeKindConnector:
        def fetch_public_offering_companies(self) -> list[dict]:
            return []

    class FakeDartConnector:
        def __init__(self, api_key: str) -> None:
            self.api_key = api_key

        def fetch_list(
            self,
            corp_code: str,
            page_no: int,
            page_count: int,
            last_reprt_at: str,
        ) -> list[dict]:
            return []

    class FakeKrxConnector:
        def __init__(self, api_key: str | None) -> None:
            self.api_key = api_key
            self.calls = 0

        def fetch_open_api(self, api_path: str, params: dict[str, str]) -> dict:
            self.calls += 1
            if self.calls == 1:
                raise ipo_service.KrxAuthError("Access Denied")
            return {"OutBlock_1": [{"id": "ok"}]}

    @dataclass
    class FakeRunResult:
        published: bool
        issues: list

    def fake_run_pipeline(session: object, bundle: dict) -> FakeRunResult:
        return FakeRunResult(published=True, issues=[])

    monkeypatch.setattr(ipo_service, "KindConnector", FakeKindConnector)
    monkeypatch.setattr(ipo_service, "DartConnector", FakeDartConnector)
    monkeypatch.setattr(ipo_service, "KrxConnector", FakeKrxConnector)
    monkeypatch.setattr(ipo_service, "run_pipeline", fake_run_pipeline)

    result = ipo_service.refresh_pipeline_live(object(), corp_code="00126380", bas_dd="20250131")
    assert result["source_status"]["stock"] == "ok:1"
