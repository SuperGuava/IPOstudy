from dataclasses import dataclass, field


@dataclass(slots=True)
class CompanySnapshotResponse:
    corp_code: str
    partial: bool
    source_status: dict[str, str]
    missing_sections: list[str] = field(default_factory=list)
    profile: dict = field(default_factory=dict)
    disclosures: list[dict] = field(default_factory=list)
    financials: dict = field(default_factory=dict)
    market: dict = field(default_factory=dict)
