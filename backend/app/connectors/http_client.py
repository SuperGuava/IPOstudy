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

    def get_text(self, url: str, params: dict) -> str:
        full_url = f"{url}?{urlencode(params)}"
        request = Request(full_url, method="GET")
        with urlopen(request, timeout=30) as response:  # noqa: S310
            return response.read().decode("utf-8")

    def post_json(self, url: str, data: dict) -> dict:
        encoded = urlencode(data).encode("utf-8")
        request = Request(
            url,
            data=encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
            method="POST",
        )
        with urlopen(request, timeout=30) as response:  # noqa: S310
            body = response.read().decode("utf-8")
        return json.loads(body)
