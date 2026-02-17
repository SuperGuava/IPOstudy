from pathlib import Path

from app.connectors.kind_connector import KindConnector


LEGACY_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "kind" / "pubofrprogcom.html"
MODERN_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "kind" / "pubofrprogcom_sub.html"


class FakeKindClient:
    def get_text(self, url: str, params: dict, headers: dict | None = None) -> str:
        return "<html>main</html>"

    def post_text(self, url: str, data: dict, headers: dict | None = None) -> str:
        return MODERN_FIXTURE_PATH.read_text(encoding="utf-8")


def test_parse_public_offering_companies() -> None:
    connector = KindConnector(http_client=FakeKindClient())
    items = connector.fetch_public_offering_companies()
    assert items
    assert items[0]["corp_name"] == "지엔씨에너지"
    assert items[0]["market"] == "코스닥"
    assert items[0]["lead_manager"] == "교보증권(주)"


def test_parse_legacy_fixture_table() -> None:
    html = LEGACY_FIXTURE_PATH.read_text(encoding="utf-8")
    items = KindConnector._parse_company_table(html)
    assert items
    assert items[0]["corp_name"] == "알파테크"
    assert items[0]["stage"] == "공모"
