from app.quality.rules.cross_source import evaluate_cross_source
from app.quality.rules.dart import evaluate_dart_rules
from app.quality.rules.kind import evaluate_kind_rules
from app.quality.rules.krx import evaluate_krx_rules
from app.quality.types import QualityGateResult, QualityIssue


def run_quality_gate(kind_rows: list[dict], dart_rows: list[dict], krx_rows: list[dict]) -> QualityGateResult:
    issues: list[QualityIssue] = []

    for row in dart_rows:
        issues.extend(
            evaluate_dart_rules(
                row,
                source="DART",
                entity_type="disclosure",
                entity_key=row.get("corp_code", "unknown"),
            )
        )

    for row in kind_rows:
        issues.extend(
            evaluate_kind_rules(
                row,
                source="KIND",
                entity_type="ipo",
                entity_key=row.get("corp_name", "unknown"),
            )
        )

    for row in krx_rows:
        issues.extend(
            evaluate_krx_rules(
                row,
                source="KRX",
                entity_type="dataset",
                entity_key=row.get("dataset_key", "unknown"),
            )
        )

    issues.extend(evaluate_cross_source(kind_rows=kind_rows, dart_rows=dart_rows, krx_rows=krx_rows))
    return QualityGateResult(issues=issues)
