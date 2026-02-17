import json
from pathlib import Path

import pytest

from app.connectors.dart_connector import DartApiError, DartConnector


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "dart"


class FakeHttpClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def get_json(self, url: str, params: dict) -> dict:
        self.calls.append((url, params))
        if url.endswith("/list.json"):
            return json.loads((FIXTURE_DIR / "list_response.json").read_text(encoding="utf-8"))
        if url.endswith("/company.json"):
            return json.loads((FIXTURE_DIR / "company_response.json").read_text(encoding="utf-8"))
        if url.endswith("/estkRs.json"):
            return json.loads((FIXTURE_DIR / "estkRs_response.json").read_text(encoding="utf-8"))
        raise ValueError(url)

    def get_bytes(self, url: str, params: dict) -> bytes:
        self.calls.append((url, params))
        return b"PK\x03\x04fakezip"


@pytest.fixture()
def mock_dart() -> DartConnector:
    return DartConnector(api_key="test-key", http_client=FakeHttpClient())


def test_fetch_list_parses_items(mock_dart: DartConnector) -> None:
    items = mock_dart.fetch_list("00126380")
    assert items
    assert "rcept_no" in items[0]


def test_fetch_list_passes_optional_date_range(mock_dart: DartConnector) -> None:
    _ = mock_dart.fetch_list("00126380", bgn_de="20250101", end_de="20250201")
    _, params = mock_dart.http_client.calls[0]  # type: ignore[attr-defined]
    assert params["bgn_de"] == "20250101"
    assert params["end_de"] == "20250201"
    assert "last_reprt_at" not in params


def test_fetch_list_raises_on_api_error() -> None:
    class ErrorHttpClient:
        def get_json(self, url: str, params: dict) -> dict:
            _ = (url, params)
            return {"status": "010", "message": "등록되지 않은 키입니다."}

        def get_bytes(self, url: str, params: dict) -> bytes:
            _ = (url, params)
            return b""

    dart = DartConnector(api_key="bad-key", http_client=ErrorHttpClient())
    with pytest.raises(DartApiError):
        dart.fetch_list("00126380")


def test_fetch_company_returns_payload(mock_dart: DartConnector) -> None:
    data = mock_dart.fetch_company("00126380")
    assert data["corp_code"] == "00126380"
    assert data["corp_name"] == "삼성전자"


def test_fetch_estk_rs_returns_payload(mock_dart: DartConnector) -> None:
    data = mock_dart.fetch_estk_rs("20260214000001")
    assert data["rcept_no"] == "20260214000001"


def test_fetch_document_zip_returns_bytes(mock_dart: DartConnector) -> None:
    payload = mock_dart.fetch_document_zip("20260214000001")
    assert payload.startswith(b"PK")
