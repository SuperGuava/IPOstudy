import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class HttpClient:
    def get_json(self, url: str, params: dict) -> dict:
        full_url = f"{url}?{urlencode(params)}"
        request = Request(full_url, method="GET")
        with urlopen(request, timeout=30) as response:  # noqa: S310
            body = response.read().decode("utf-8")
        return json.loads(body)

    def get_bytes(self, url: str, params: dict) -> bytes:
        full_url = f"{url}?{urlencode(params)}"
        request = Request(full_url, method="GET")
        with urlopen(request, timeout=60) as response:  # noqa: S310
            return response.read()
