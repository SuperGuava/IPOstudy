from dataclasses import dataclass


@dataclass(slots=True)
class QualityIssue:
    source: str
    rule_code: str
    severity: str
    entity_type: str
    entity_key: str
    message: str


@dataclass(slots=True)
class QualityGateResult:
    issues: list[QualityIssue]

    @property
    def has_fail(self) -> bool:
        return any(issue.severity == "FAIL" for issue in self.issues)
