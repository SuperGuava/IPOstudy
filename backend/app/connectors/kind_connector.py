import html
import re
from datetime import date

from app.connectors.http_client import HttpClient


class KindConnector:
    def __init__(self, http_client: HttpClient | None = None) -> None:
        self.http_client = http_client or HttpClient()
        self.base_url = "https://kind.krx.co.kr/listinvstg"
        self.main_url = f"{self.base_url}/pubofrprogcom.do"
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": f"{self.main_url}?method=searchPubofrProgComMain",
            "Origin": "https://kind.krx.co.kr",
            "X-Requested-With": "XMLHttpRequest",
        }

    def fetch_public_offering_companies(self) -> list[dict[str, str]]:
        # KIND listing page renders rows via server-side sub request.
        self.http_client.get_text(
            self.main_url,
            {"method": "searchPubofrProgComMain"},
            headers={"User-Agent": self.browser_headers["User-Agent"]},
        )
        sub_html = self.http_client.post_text(
            self.main_url,
            {
                "method": "searchPubofrProgComSub",
                "forward": "pubofrprogcom_sub",
                "currentPageSize": "3000",
                "pageIndex": "1",
                "marketType": "",
                "searchCorpName": "",
                "fromDate": "",
                "toDate": "",
                "repMajAgntDesignAdvserComp": "",
                "repMajAgntComp": "",
                "designAdvserComp": "",
            },
            headers=self.browser_headers,
        )
        return self._parse_company_table(sub_html)

    @staticmethod
    def _clean_cell(value: str) -> str:
        stripped = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
        stripped = re.sub(r"<.*?>", "", stripped)
        return html.unescape(stripped).replace("\xa0", " ").strip()

    @staticmethod
    def _normalize_stage(listing_date: str | None) -> str:
        if not listing_date:
            return "offering"
        cleaned = listing_date.replace("-", "")
        if len(cleaned) != 8 or not cleaned.isdigit():
            return "offering"
        target = date(int(cleaned[:4]), int(cleaned[4:6]), int(cleaned[6:8]))
        return "prelisting" if target >= date.today() else "listed"

    @staticmethod
    def _parse_company_table(html: str) -> list[dict[str, str]]:
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.IGNORECASE | re.DOTALL)
        items: list[dict[str, str]] = []
        for row in rows:
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.IGNORECASE | re.DOTALL)
            if len(cells) < 5:
                continue
            cleaned = [KindConnector._clean_cell(cell) for cell in cells]
            if len(cells) >= 9:
                market_match = re.search(r"alt=['\"]([^'\"]+)['\"]", cells[0], re.IGNORECASE)
                market = KindConnector._clean_cell(market_match.group(1)) if market_match else ""
                corp_name = cleaned[0]
                listing_date = cleaned[7]
                lead_manager = cleaned[8]
                stage = KindConnector._normalize_stage(listing_date)
            else:
                corp_name = cleaned[0]
                market = cleaned[1]
                stage = cleaned[2] or KindConnector._normalize_stage(cleaned[3] if len(cleaned) > 3 else None)
                listing_date = cleaned[3] if len(cleaned) > 3 else ""
                lead_manager = cleaned[4] if len(cleaned) > 4 else ""
            if not corp_name:
                continue
            items.append({"corp_name": corp_name, "market": market, "stage": stage, "listing_date": listing_date, "lead_manager": lead_manager})
        return items
