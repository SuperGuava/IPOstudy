from app.connectors.http_client import HttpClient


class KrxConnector:
    def __init__(self, http_client: HttpClient | None = None) -> None:
        self.http_client = http_client or HttpClient()
        self.endpoint = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"

    def fetch_dataset(self, bld: str, params: dict[str, str]) -> dict:
        payload = {"bld": bld}
        payload.update(params)
        return self.http_client.post_json(self.endpoint, payload)
