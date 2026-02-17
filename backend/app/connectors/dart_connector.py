from app.connectors.http_client import HttpClient
from app.schemas.dart import DartCompanyResponse, DartDisclosureItem, DartEstkRsResponse, DartListResponse


class DartApiError(RuntimeError):
    pass


class DartConnector:
    def __init__(self, api_key: str, http_client: HttpClient | None = None) -> None:
        self.api_key = api_key
        self.http_client = http_client or HttpClient()
        self.base_url = "https://opendart.fss.or.kr/api"

    def fetch_corp_codes_zip(self) -> bytes:
        return self.http_client.get_bytes(
            f"{self.base_url}/corpCode.xml",
            {"crtfc_key": self.api_key},
        )

    def fetch_company(self, corp_code: str) -> DartCompanyResponse:
        response: DartCompanyResponse = self.http_client.get_json(
            f"{self.base_url}/company.json",
            {"crtfc_key": self.api_key, "corp_code": corp_code},
        )
        self._ensure_success(response)
        return response

    def fetch_list(
        self,
        corp_code: str,
        page_no: int = 1,
        page_count: int = 100,
        last_reprt_at: str | None = None,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> list[DartDisclosureItem]:
        params: dict[str, str | int] = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
            "page_no": page_no,
            "page_count": page_count,
        }
        if last_reprt_at:
            params["last_reprt_at"] = last_reprt_at
        if bgn_de:
            params["bgn_de"] = bgn_de
        if end_de:
            params["end_de"] = end_de
        response: DartListResponse = self.http_client.get_json(
            f"{self.base_url}/list.json",
            params,
        )
        self._ensure_success(response, allow_no_data=True)
        return response.get("list", [])

    def fetch_document_zip(self, rcept_no: str) -> bytes:
        return self.http_client.get_bytes(
            f"{self.base_url}/document.xml",
            {"crtfc_key": self.api_key, "rcept_no": rcept_no},
        )

    def fetch_estk_rs(self, rcept_no: str) -> DartEstkRsResponse:
        response: DartEstkRsResponse = self.http_client.get_json(
            f"{self.base_url}/estkRs.json",
            {"crtfc_key": self.api_key, "rcept_no": rcept_no},
        )
        self._ensure_success(response)
        return response

    @staticmethod
    def _ensure_success(response: dict, *, allow_no_data: bool = False) -> None:
        status = str(response.get("status", "")).strip()
        if status == "000":
            return
        if allow_no_data and status == "013":
            return
        message = str(response.get("message", "Unknown DART API error")).strip()
        raise DartApiError(f"DART API status={status}: {message}")
