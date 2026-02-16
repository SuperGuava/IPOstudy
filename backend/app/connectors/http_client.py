import json
from http.cookiejar import CookieJar
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener


class HttpClient:
    def __init__(self) -> None:
        self._opener = build_opener(HTTPCookieProcessor(CookieJar()))

    def _open(self, request: Request, timeout: int) -> bytes:
        with self._opener.open(request, timeout=timeout) as response:  # noqa: S310
            return response.read()

    def get_json(self, url: str, params: dict, headers: dict[str, str] | None = None) -> dict:
        full_url = f"{url}?{urlencode(params)}"
        request = Request(full_url, headers=headers or {}, method="GET")
        body = self._open(request, timeout=30).decode("utf-8")
        return json.loads(body)

    def get_bytes(self, url: str, params: dict, headers: dict[str, str] | None = None) -> bytes:
        full_url = f"{url}?{urlencode(params)}"
        request = Request(full_url, headers=headers or {}, method="GET")
        return self._open(request, timeout=60)

    def get_text(self, url: str, params: dict, headers: dict[str, str] | None = None) -> str:
        full_url = f"{url}?{urlencode(params)}"
        request = Request(full_url, headers=headers or {}, method="GET")
        return self._open(request, timeout=30).decode("utf-8")

    def post_json(self, url: str, data: dict, headers: dict[str, str] | None = None) -> dict:
        encoded = urlencode(data).encode("utf-8")
        request_headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        if headers:
            request_headers.update(headers)
        request = Request(
            url,
            data=encoded,
            headers=request_headers,
            method="POST",
        )
        body = self._open(request, timeout=30).decode("utf-8")
        return json.loads(body)
