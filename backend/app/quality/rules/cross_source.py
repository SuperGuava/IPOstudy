from app.quality.types import QualityIssue


def evaluate_cross_source(kind_rows: list[dict], dart_rows: list[dict], krx_rows: list[dict]) -> list[QualityIssue]:
    issues: list[QualityIssue] = []

    kind_names = {row.get("corp_name") for row in kind_rows if row.get("corp_name")}
    dart_names = {row.get("corp_name") for row in dart_rows if row.get("corp_name")}

    if kind_names:
        linked = kind_names.intersection(dart_names)
        ratio = len(linked) / len(kind_names)
        if ratio < 0.7:
            issues.append(
                QualityIssue(
                    source="CROSS",
                    rule_code="CROSS_KIND_DART_LINKAGE_RATIO",
                    severity="WARN",
                    entity_type="batch",
                    entity_key="kind_dart",
                    message=f"kind-dart linkage ratio below threshold: {ratio:.2f}",
                )
            )

    listed_count = len([row for row in kind_rows if row.get("stage") in {"신규상장", "listed"}])
    if listed_count > 0 and len(krx_rows) == 0:
        issues.append(
            QualityIssue(
                source="CROSS",
                rule_code="CROSS_POST_LISTING_KRX_ATTACH",
                severity="WARN",
                entity_type="batch",
                entity_key="kind_krx",
                message="no KRX rows attached for listed items",
            )
        )
    return issues
