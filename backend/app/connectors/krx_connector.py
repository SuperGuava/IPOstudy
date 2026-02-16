import json
from urllib.error import HTTPError

from app.connectors.http_client import HttpClient


class KrxAuthError(RuntimeError):
    pass


class KrxRequestError(RuntimeError):
    pass


class KrxConnector:
    def __init__(self, http_client: HttpClient | None = None, api_key: str | None = None) -> None:
        self.http_client = http_client or HttpClient()
        self.api_key = api_key
        self.endpoint = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
        self.loader_url = "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd"
        self.openapi_base_url = "https://data-dbg.krx.co.kr/svc/apis"
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": self.loader_url,
            "Origin": "http://data.krx.co.kr",
            "X-Requested-With": "XMLHttpRequest",
        }

    @staticmethod
    def _extract_error_message(error: HTTPError) -> str:
        try:
            raw = error.read().decode("utf-8", errors="ignore")
        except Exception:
            return f"http {error.code}"
        try:
            payload = json.loads(raw)
            message = payload.get("respMsg")
            if isinstance(message, str) and message:
                return message
        except Exception:
            pass
        return raw[:200] or f"http {error.code}"

    def fetch_open_api(self, api_path: str, params: dict[str, str]) -> dict:
        if not self.api_key:
            raise ValueError("KRX_API_KEY is required for Open API calls.")
        path = api_path.lstrip("/")
        url = f"{self.openapi_base_url}/{path}"
        headers = {
            "AUTH_KEY": self.api_key,
            "User-Agent": self.browser_headers["User-Agent"],
        }
        try:
            return self.http_client.get_json(url, params, headers=headers)
        except HTTPError as exc:
            message = self._extract_error_message(exc)
            if exc.code in {401, 403}:
                raise KrxAuthError(message) from exc
            raise KrxRequestError(message) from exc

    def fetch_dataset(self, bld: str, params: dict[str, str]) -> dict:
        # KRX endpoint may reject direct POST without session priming.
        self.http_client.get_text(self.loader_url, {}, headers={"User-Agent": self.browser_headers["User-Agent"]})
        payload = {"bld": bld}
        payload.update(params)
        return self.http_client.post_json(self.endpoint, payload, headers=self.browser_headers)
