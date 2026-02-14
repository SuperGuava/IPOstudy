from pathlib import Path

from app.connectors.kind_connector import KindConnector


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "kind" / "pubofrprogcom.html"


class FakeKindClient:
    def get_text(self, url: str, params: dict) -> str:
        return FIXTURE_PATH.read_text(encoding="utf-8")


def test_parse_public_offering_companies() -> None:
    connector = KindConnector(http_client=FakeKindClient())
    items = connector.fetch_public_offering_companies()
    assert items
    assert items[0]["corp_name"] == "알파테크"
    assert items[0]["stage"] == "공모"
