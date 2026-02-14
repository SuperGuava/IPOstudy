import re

from app.connectors.http_client import HttpClient


class KindConnector:
    def __init__(self, http_client: HttpClient | None = None) -> None:
        self.http_client = http_client or HttpClient()
        self.base_url = "https://kind.krx.co.kr/listinvstg"

    def fetch_public_offering_companies(self) -> list[dict[str, str]]:
        html = self.http_client.get_text(
            f"{self.base_url}/pubofrprogcom.do",
            {"method": "searchPubofrProgComMain"},
        )
        return self._parse_company_table(html)

    @staticmethod
    def _parse_company_table(html: str) -> list[dict[str, str]]:
        rows = re.findall(r"<tr>(.*?)</tr>", html, re.IGNORECASE | re.DOTALL)
        items: list[dict[str, str]] = []
        for row in rows:
            cells = re.findall(r"<td>(.*?)</td>", row, re.IGNORECASE | re.DOTALL)
            cleaned = [re.sub(r"<.*?>", "", cell).strip() for cell in cells]
            if len(cleaned) < 5:
                continue
            items.append(
                {
                    "corp_name": cleaned[0],
                    "market": cleaned[1],
                    "stage": cleaned[2],
                    "listing_date": cleaned[3],
                    "lead_manager": cleaned[4],
                }
            )
        return items
